from pathlib import Path
from functools import partial
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot, QPoint
from PySide6.QtWidgets import QLCDNumber, QInputDialog, QFileDialog, QMessageBox

from asm.assembler_helpers import parse_num
from emulator.processor import UndefinedInstructionError
from gui.bus_geometry import AnimationPaths
from gui.animations import build_animation
from gui.processor_visualization import ProcessorVisualization
from gui.emulator_window import EmulatorWindow
from asm.assembler import AssemblerError, assemble_file

REGISTER_NAMES = {
    'A': 'accumulator',
    'AB': 'accumulator_binary',
    'ARH': 'address_register_high_byte',
    'ARL': 'address_register_low_byte',
    'OP1': 'alu_op1',
    'OP2': 'alu_op2',
    'RES': 'alu_res',
    'B': 'flag_b',
    'C': 'flag_c',
    'D': 'flag_d',
    'I': 'flag_i',
    'N': 'flag_n',
    'V': 'flag_v',
    'Z': 'flag_z',
    'X': 'index_x',
    'Y': 'index_x',
    'S': 'stack_pointer',

    'IR': 'instruction_register',
    'ZD': 'zero_page_data',
    'MD': 'memory_data',
    'SD': 'stack_data'
}


def split_to_bytes(value):
    return [int(value[i:i + 2], 16) for i in range(0, len(value), 2)]


def segment_length(point_a: QPoint, point_b: QPoint) -> int:
    return abs(point_a.x() - point_b.x()) + abs(point_a.y()-point_b.y())


class RunWorker(QObject):
    finished = Signal()
    steps = Signal(int)
    update_label_signal = Signal(str, object)

    def __init__(self, processor) -> None:
        super().__init__()
        self.processor = processor
        self.processor_ready = True

    def run_processor(self):
        i = 0
        while not self.processor.interrupt_requested:
            if self.processor_ready:
                try:
                    self.processor.run_instruction()
                except UndefinedInstructionError as exception:
                    self.update_label_signal.emit('current_instruction', str(exception))
                i += 1
                self.steps.emit(i)
        self.finished.emit()

    def run_instruction(self):
        try:
            self.processor.run_instruction()
        except UndefinedInstructionError as exception:
            self.update_label_signal.emit('current_instruction', str(exception))
        self.finished.emit()


class Simulator(EmulatorWindow):
    interrupt_signal = Signal()
    nminterrupt_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setup()
        self.retranslate()

        self.processor = ProcessorVisualization(self)

        self.interrupt_signal.connect(self.processor.interrupt)
        self.nminterrupt_signal.connect(self.processor.non_maskable_interrupt)

        self.shown_page = 2
        self.shown_page_col = 0
        self.shown_page_row = 0

        self.shown_zero_page_col = 0
        self.shown_zero_page_row = 0

        self.show_page(2, force_update=True)
        self.show_page(0, force_update=True)
        self.shown_stack_pointer = self.processor.S
        self.show_stack(force_update=True)

        self.assembler_file_name = ''
        self.assembler_file_unsaved_changes = False
        self.assembler_input.textChanged.connect(self.assembler_file_changed)
        self.debug_info = {}

        self.program_counter_frame.mousePressEvent = partial(self.set_register, 'PC')
        self.accumulator_frame.mousePressEvent = partial(self.set_register, 'A')
        self.index_x.mousePressEvent = partial(self.set_register, 'X')
        self.index_y.mousePressEvent = partial(self.set_register, 'Y')
        self.stack_pointer.mousePressEvent = partial(self.set_register, 'S')
        self.status_register_frame.mousePressEvent = partial(self.set_register, 'SR')
        self.shown_page_frame.mousePressEvent = self.set_shown_page

        for offset in range(0x100):
            widget = self.__getattribute__(f'reg_{offset:02X}')
            widget.mousePressEvent = partial(self.set_memory_address, offset, 'reg')
            widget = self.__getattribute__(f'zp_{offset:02X}')
            widget.mousePressEvent = partial(self.set_memory_address, offset, 'zp')

        self.run_button.clicked.connect(self.run_button_clicked)
        self.program_running = False
        self.step_button.clicked.connect(self.step_button_clicked)
        self.reset_button.clicked.connect(self.reset_button_clicked)
        self.interrupt_button.clicked.connect(self.interrupt_button_clicked)
        self.nminterrupt_button.clicked.connect(self.nminterrupt_button_clicked)
        self.clear_memory_button.clicked.connect(self.clear_processor_memory)
        self.assemble_button.clicked.connect(self.assemble_button_clicked)
        self.open_file_button.clicked.connect(self.open_assembler_file_clicked)
        self.save_file_button.clicked.connect(self.save_assembler_file_clicked)
        self.save_file_as_button.clicked.connect(self.save_assembler_file_as_clicked)

        self.speed_dial.setMinimum(0)
        self.speed_dial.setMaximum(100)
        self.speed_dial.valueChanged.connect(self.set_speed)
        self.animation_max_speed = 1.5
        self.animation_min_speed = 0.01
        self.animation_speed = 0.4
        self.animation_running = False
        self.speed_dial.setValue(30)
        self.set_speed()

        self.animation_mode_checkbox.stateChanged.connect(self.animations_checkbox_clicked)
        self.animation_mode = False
        self.paths = AnimationPaths
        self.animators = []

        self.decimal_mode_checkbox.stateChanged.connect(self.decimal_display_checkbox_clicked)
        self.set_base_mode(QLCDNumber.Mode.Hex)
        self.accumulator_binary.setMode(QLCDNumber.Mode.Bin)
        self.processor.reset()

    def input_byte(self, title, text, word=False):
        text, ok = QInputDialog.getText(self, title, text)
        maximum = 0xffff if word else 0xff
        if ok and text:
            try:
                value = parse_num(text)
            except ValueError:
                QMessageBox.warning(self,
                                    "Invalid number format", "Valid number formats are:\n"
                                    "'0x..' or '$..' for hexadecimal numbers\n"
                                    "'...' for decimal numbers\n"
                                    "'0b........' for binary numbers.")
            else:
                if 0 <= value <= maximum:
                    return value
                else:
                    QMessageBox.warning(self, "Out of range", f"Value must be between $00 and ${maximum:02X}")

    def set_speed(self):
        value = self.speed_dial.value()
        # For animation mode
        self.animation_speed = self.animation_min_speed + (self.animation_max_speed-self.animation_min_speed)*value/100
        # Cycle delay is used without animations
        self.cycle_delay = 5 - 5*value/100

    def set_shown_page(self, _) -> None:
        page = self.input_byte("Select page", f"Set shown page to:")
        if page:
            self.shown_page = page
            self.show_page(page, force_update=True)

    @Slot(int, object)
    def show_page(self, page, force_update=True):
        if not force_update and self.shown_page == page:
            return

        if page == 1:
            self.show_stack()
            return
        if page == 0:
            # Zero page has separate Widgets
            prefix = 'zp'
        else:
            prefix = 'reg'
        for c in range(0x10):
            self.set_page_row_color(c, 'black')
            self.set_page_col_color(c, 'black')

        for r in range(0x100):
            byte = self.processor.memory.data[(page << 8) + r]
            getattr(self, f'{prefix}_{r:02X}').setText(byte)

        if page > 0:
            self.shown_page_display.setText(f'${page:02X}')
            self.shown_page = page

    def set_page_row_color(self, row, color):
        getattr(self, f'reg_row_{row:1X}').setStyleSheet(f'color: {color}')

    def set_page_col_color(self, col, color):
        getattr(self, f'reg_col_{col:1X}').setStyleSheet(f'color: {color}')

    def set_zero_page_row_color(self, row, color):
        getattr(self, f'zp_row_{row:1X}').setStyleSheet(f'color: {color}')

    def set_zero_page_col_color(self, col, color):
        getattr(self, f'zp_col_{col:1X}').setStyleSheet(f'color: {color}')

    @Slot(int, object)
    def show_memory_address(self, address: int):
        page = address >> 8
        if page != self.shown_page:
            self.show_page(page)
        if page == 0:
            self.show_zero_page_address(address)
        elif page == 1:
            self.show_stack()
        else:
            self.show_memory_page_address(page, address)

    def show_memory_page_address(self, page, address):
        row = (address & 0xf0) >> 4
        col = address & 0x0f
        if self.shown_page != page or self.shown_page_row != row or self.shown_page_col != col:
            self.set_page_row_color(self.shown_page_row, 'black')
            self.set_page_col_color(self.shown_page_col, 'black')
            self.set_page_row_color(row, 'red')
            self.set_page_col_color(col, 'red')
            self.shown_page_col = col
            self.shown_page_row = row
        reg = address & 0xff
        byte = self.processor.memory.data[(page << 8) + reg]
        self.__getattribute__(f'reg_{reg:02X}').setText(byte)

    def show_zero_page_address(self, address):
        row = (address & 0xf0) >> 4
        col = address & 0x0f
        if self.shown_zero_page_row != row or self.shown_zero_page_col != col:
            self.set_zero_page_row_color(self.shown_zero_page_row, 'black')
            self.set_zero_page_col_color(self.shown_zero_page_col, 'black')
            self.set_zero_page_row_color(row, 'red')
            self.set_zero_page_col_color(col, 'red')
            self.shown_zero_page_col = col
            self.shown_zero_page_row = row
        reg = address & 0xff
        byte = self.processor.memory.data[reg]
        self.__getattribute__(f'zp_{reg:02X}').setText(byte)

    def show_stack(self, force_update=True) -> None:
        stack_pointer = self.processor.S
        if not force_update and stack_pointer == self.shown_stack_pointer:
            return

        if force_update or stack_pointer != self.shown_stack_pointer:
            self.show_stack_labels(stack_pointer)
            self.shown_stack_pointer = stack_pointer

        for i in range(0x10):
            address = 0x100 + (self.processor.S + i - 8) % 0x100
            getattr(self, f'stack_{(i%0x10):01X}').setText(f'{self.processor.memory.data[address]:02X}')

    def show_stack_labels(self, stack_pointer):
        for i in range(0x10):
            address = (stack_pointer + i - 8) % 0x100
            getattr(self, f'stack_sp_{(i%0x10):01X}').setText(f'{address:02X}')

    @Slot(str, str)
    def update_label(self, name: str, value):
        getattr(self, name).setText(value)

    def set_base_mode(self, mode: QLCDNumber.Mode):
        for r in range(0x100):
            getattr(self, f'zp_{r:02X}').setMode(mode)
            getattr(self, f'reg_{r:02X}').setMode(mode)
        self.accumulator.setMode(mode)
        self.index_x.setMode(mode)
        self.index_y.setMode(mode)
        self.stack_pointer.setMode(mode)
        self.instruction_register.setMode(mode)

    def decimal_display_checkbox_clicked(self, value):
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked:
            self.set_base_mode(QLCDNumber.Mode.Dec)
        elif state == Qt.CheckState.Unchecked:
            self.set_base_mode(QLCDNumber.Mode.Hex)

    def animations_checkbox_clicked(self, value):
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked:
            self.animation_mode = True
        elif state == Qt.CheckState.Unchecked:
            self.animation_mode = False

    def clear_processor_memory(self):
        self.processor.clear_memory()
        self.reset_button_clicked()

    def set_register(self, register, _):
        if register == 'PC':
            value = self.input_byte("Set Register", f"Set register {register} to:", word=True)
        else:
            value = self.input_byte("Set Register", f"Set register {register} to:")

        if value:
            setattr(self.processor, register, value)

    def set_memory_address(self, offset, prefix, _):
        if prefix == 'zp':
            address = offset
        else:
            page = self.shown_page
            address = (page << 8) + offset

        value = self.input_byte(f'Set Memory Address', f'Set address {address:04X} to:')

        if value is not None:
            self.processor.memory.data[address] = value
            getattr(self, f'{prefix}_{offset:02X}').setText(value)

    def enable_buttons(self, state: bool) -> None:
        self.run_button.setEnabled(state)
        self.step_button.setEnabled(state)
        self.reset_button.setEnabled(state)
        self.assemble_button.setEnabled(state)
        self.open_file_button.setEnabled(state)
        self.save_file_button.setEnabled(state)
        self.save_file_as_button.setEnabled(state)

    def run_button_clicked(self):
        if self.program_running:
            self.run_button.setEnabled(False)
            self.worker.finished.emit()
            self.program_running = False
        else:
            self.enable_buttons(False)

            self.run_button.setEnabled(True)
            self.run_button.setText('Stop')
            self.program_running = True
            self.processor.interrupt_requested = False
            self.thread = QThread()
            self.worker = RunWorker(self.processor)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run_processor)
            self.worker.finished.connect(self.thread.quit)
            # self.worker.finished.connect(self.interrupt)
            self.worker.update_label_signal.connect(self.update_label)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
            self.thread.finished.connect(
                lambda: (
                    self.run_button.setText('Run'),
                    self.enable_buttons(True),
                )
            )

    def step_button_clicked(self):
        self.enable_buttons(False)

        self.thread = QThread()
        self.worker = RunWorker(self.processor)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_instruction)
        self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.interrupt)
        self.worker.update_label_signal.connect(self.update_label)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(
            lambda: (
                self.enable_buttons(True)
            )
        )
        self.thread.start()

    def reset_button_clicked(self):
        self.processor.reset()
        self.current_instruction.setText('')
        self.cycle_stage.setText('')
        self.processor.cycles = 0
        self.reset_vector.setText(f'{self.processor.word(self.processor.reset_vector_address):04X}')
        self.interrupt_vector.setText(f'{self.processor.word(self.processor.interrupt_vector_address):04X}')
        self.nminterrupt_vector.setText(f'{self.processor.word(self.processor.nmi_vector_address):04X}')
        self.show_stack(force_update=True)
        self.show_page(2, force_update=True)
        self.show_page(0, force_update=True)

    def interrupt_button_clicked(self):
        self.interrupt_signal.emit()

    def nminterrupt_button_clicked(self):
        self.nminterrupt_signal.emit()

    def format_assembler_errors(self, errors):
        message = 'Assembler error:\n'
        for line, error in errors.errors.items():
            message += f'Line {line}: {error}\n'
            self.assembler_input.mark_line(line)
        return message

    def assemble_button_clicked(self):
        if not self.assembler_file_name:
            self.save_assembler_file_as_clicked()

        if self.assembler_file_unsaved_changes:
            answer = QMessageBox.question(self, 'Unsaved changes', 'Save changes before assembling?')
            if answer == QMessageBox.Yes:
                self.save_assembler_file()

        try:
            data, self.debug_info = assemble_file(self.assembler_file_name)
        except AssemblerError as e:
            # todo: Mark lines with errors
            QMessageBox.critical(self, 'Assembler error', self.format_assembler_errors(e))
        except Exception as error:
            QMessageBox.critical(self, 'Assembler error',
                                       f'Something went wrong with your assembler code: {error}')
        else:
            first_address = None
            for key, value in data.items():
                bytes = split_to_bytes(value)
                for byte in bytes:
                    if first_address is None:
                        first_address = key
                    self.processor.memory.data[key] = byte
                    key += 1
            self.show_page(first_address >> 8, force_update=True)
            self.processor.reset()

    def open_assembler_file_clicked(self):
        if self.assembler_file_unsaved_changes:
            button = QMessageBox.question(self, "Discard changes?", "You have unsaved changes. Discard?")
            if button == QMessageBox.ButtonRole.NoRole:
                return

        file_name = QFileDialog.getOpenFileName(
            self, "Open Assembler File", "", "Assembler Files (*.asm *.as)"
        )[0]
        if not file_name:
            return
        with open(file_name) as file:
            self.assembler_input.setPlainText(file.read())
        self.assembler_file_name = file_name
        self.assembler_file_unsaved_changes = False
        self.show_assembler_file_name()

    def save_assembler_file_clicked(self):
        if not self.assembler_file_name:
            self.save_assembler_file_as_clicked()
        self.save_assembler_file()
        self.assembler_file_unsaved_changes = False
        self.show_assembler_file_name()

    def save_assembler_file_as_clicked(self):
        file_name = QFileDialog.getSaveFileName(
            self, "Save Assembler File", self.assembler_file_name, "Assembler Files (*.asm *.as)"
        )[0]
        with open(file_name, 'w') as file:
            file.write(self.assembler_input.toPlainText())
        self.assembler_file_name = file_name
        self.assembler_file_unsaved_changes = False
        self.show_assembler_file_name()

    def assembler_file_changed(self):
        self.assembler_file_unsaved_changes = True
        self.show_assembler_file_name()

    def show_assembler_file_name(self):
        file_name = Path(self.assembler_file_name).stem
        if self.assembler_file_unsaved_changes:
            file_name += ' *'
        self.assembler_file_name_label.setText(file_name)

    def save_assembler_file(self):
        with open(self.assembler_file_name, 'w') as file:
            file.write(self.assembler_input.toPlainText())
        self.assembler_file_unsaved_changes = False
        self.show_assembler_file_name()

    def animate(self, transfer):
        """Animates data transfer along the given path (a list of coordinates)"""
        self.animation = build_animation(transfer, self)

        self.animation.finished.connect(self.stop_animation)

        self.animation_running = True
        self.animation.start()

    @Slot()
    def stop_animation(self):
        for animator in self.animators:
            animator.hide()
            animator.deleteLater()

        # for destination in self.transfer_destinations:
        #     self.update_label(REGISTER_NAMES[destination], getattr(self.processor, destination))
        self.animators = []
        self.animation_running = False
