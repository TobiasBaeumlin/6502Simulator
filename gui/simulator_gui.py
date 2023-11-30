from pathlib import Path
from functools import partial
from PySide6.QtCore import QObject, QThread, Signal, Slot, QPoint, QMutex, QWaitCondition
from PySide6 import QtWidgets
from PySide6.QtWidgets import QLCDNumber, QInputDialog, QFileDialog, QMessageBox

from asm.assembler_helpers import parse_num
from gui.bus_geometry import AnimationPaths
from gui.animations import build_animation
from gui.processor_visualization import ProcessorVisualization
from gui.mainwindow import Ui_MainWindow
from asm.assembler import AssemblerError, assemble_file


def split_to_bytes(value):
    return [int(value[i:i + 2], 16) for i in range(0, len(value), 2)]


def segment_length(point_a: QPoint, point_b: QPoint) -> int:
    return abs(point_a.x() - point_b.x()) + abs(point_a.y()-point_b.y())


class RunWorker(QObject):
    finished = Signal()
    steps = Signal(int)

    def __init__(self, processor) -> None:
        super().__init__()
        self.processor = processor
        self.processor_ready = True

    @Slot()
    def set_processor_ready(self):
        self.processor_ready = True

    def run_processor(self):
        i = 0
        while not self.processor.interrupt_requested:
            if self.processor_ready:
                self.set_processor_ready = False
                self.processor.run_instruction()
                i += 1
                self.steps.emit(i)
        self.finished.emit()

    def run_instruction(self):
        self.processor.run_instruction()
        self.finished.emit()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.set_base_mode(QLCDNumber.Mode.Hex)
        self.accumulator_binary.setMode(QLCDNumber.Mode.Bin)
        self.shown_page = 0xff
        self.shown_page_col = 0
        self.shown_page_row = 0

        self.assembler_file_name = ''
        self.assembler_file_unsaved_changes = False
        self.assembler_input.textChanged.connect(self.assembler_file_changed)
        self.program_counter_frame.mousePressEvent = partial(self.set_register, 'PC')
        self.accumulator_frame.mousePressEvent = partial(self.set_register, 'A')
        self.index_x.mousePressEvent = partial(self.set_register, 'X')
        self.index_y.mousePressEvent = partial(self.set_register, 'Y')
        self.stack_pointer.mousePressEvent = partial(self.set_register, 'SP')
        self.status_register_frame.mousePressEvent = partial(self.set_register, 'SR')

        for offset in range(0x100):
            widget = self.__getattribute__(f'reg_{offset:02X}')
            widget.mousePressEvent = partial(self.set_memory_address, offset, 'reg')
            widget = self.__getattribute__(f'zp_{offset:02X}')
            widget.mousePressEvent = partial(self.set_memory_address, offset, 'zp')

        self.run_button.clicked.connect(self.run_button_clicked)
        self.program_running = False
        self.step_button.clicked.connect(self.step_button_clicked)
        self.reset_button.clicked.connect(self.reset_button_clicked)
        self.assemble_button.clicked.connect(self.assemble_button_clicked)
        self.open_file_button.clicked.connect(self.open_assembler_file_clicked)
        self.save_file_button.clicked.connect(self.save_assembler_file_clicked)
        self.save_file_as_button.clicked.connect(self.save_assembler_file_as_clicked)

        self.cycle_delay = 2.5

        self.animation_mode = True
        self.mutex = QMutex()
        self.can_continue = QWaitCondition()
        self.paths = AnimationPaths
        self.animators = []
        self.animation_duration = 2000    # in ms
        self.animation_speed = 0.2        # pixel/ms
        self.animation_running = False
        self.processor = ProcessorVisualization(self, self.mutex, self.can_continue)

    @Slot(int, object)
    def show_page(self, page, data, force=False):
        # if page == 1:
        #     self.show_stack_page(data)
        #     return
        if page == 0:
            # Zero page has separate Widgets
            prefix = 'zp'
        else:
            prefix = 'reg'
        for c in range(0x10):
            self.set_page_row_color(c, 'black')
            self.set_page_col_color(c, 'black')

        for r in range(0x100):
            byte = data[(page << 8) + r]
            self.__getattribute__(f'{prefix}_{r:02X}').setText(f'{byte:02X}')

        if page > 2:
            self.page.setText(f'{page:2X}')
        self.shown_page = page

    def set_page_row_color(self, row, color):
        self.__getattribute__(f'page_row_{row:1X}').setStyleSheet(f'color: {color}')

    def set_page_col_color(self, col, color):
        self.__getattribute__(f'page_col_{col:1X}').setStyleSheet(f'color: {color}')

    @Slot(int, object)
    def show_memory_address(self, address: int, data):
        page = address >> 8
        reg = address & 0xff
        if page != self.shown_page:
            self.show_page(page, data)
        row = (address & 0xf0) >> 4
        col = address & 0x0f
        if self.shown_page == page and self.shown_page_row == row and self.shown_page_col == col:
            return
        self.set_page_row_color(self.shown_page_row, 'black')
        self.set_page_col_color(self.shown_page_col, 'black')
        self.set_page_row_color(row, 'red')
        self.set_page_col_color(col, 'red')
        self.shown_page_col = col
        self.shown_page_row = row
        byte = data[(page << 8) + reg]
        self.__getattribute__(f'reg_{reg:02X}').setProperty('intValue', byte)
        # self.page.setText(f'{(address >> 8):02X}')

    @Slot(str, str)
    def update_label(self, name: str, value):
        self.__getattribute__(name).setText(value)

    def set_base_mode(self, mode: QLCDNumber.Mode):
        for r in range(0x100):
            self.__getattribute__(f'reg_{r:02X}').setMode(mode)
        self.program_counter_high_byte.setMode(mode)
        self.program_counter_low_byte.setMode(mode)
        self.accumulator.setMode(mode)
        self.index_x.setMode(mode)
        self.index_y.setMode(mode)
        self.stack_pointer.setMode(mode)

    def set_register(self, register, event):
        text, ok = QInputDialog.getText(
            self, "Set Register", f"Set register {register} to:")
        if ok and text:
            try:
                value = parse_num(text)
            except ValueError:
                pass
            else:
                if (0 <= value <= 0xff) or (register == 'PC' and 0 <= value <= 0xffff):
                    setattr(self.processor, register, value)
                else:
                    pass

    def set_memory_address(self, offset, prefix, event):
        if prefix == 'zp':
            address = offset
        else:
            page = self.processor.current_page
            address = (page << 8) + offset

        text, ok = QInputDialog.getText(self, f'Set Memory Address', f'Set address {address} to:')
        if ok and text:
            value = parse_num(text)
            if 0 <= value <= 0xff:
                self.processor.memory.data[address] = value
                self.__getattribute__(f'{prefix}_{offset:02x}').setText(value)
            else:
                pass

    def run_button_clicked(self):
        if self.program_running:
            self.run_button.setEnabled(False)
            self.worker.finished.emit()
            self.program_running = False
        else:
            self.run_button.setText('Stop')
            self.step_button.setEnabled(False)
            self.program_running = True
            self.processor.interrupt_requested = False

            self.thread = QThread()
            self.worker = RunWorker(self.processor)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run_processor)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.interrupt)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.steps.connect(self.count_steps)
            self.thread.start()
            self.can_continue.wakeAll()
            self.thread.finished.connect(
                lambda: (
                    self.run_button.setText('Run'),
                    self.run_button.setEnabled(True),
                    self.step_button.setEnabled(True)
                )
            )

    def count_steps(int):
        pass

    @Slot()
    def interrupt(self):
        self.processor.interrupt_requested = True

    def step_button_clicked(self):
        self.run_button.setEnabled(False)
        self.step_button.setEnabled(False)

        self.thread = QThread()
        self.worker = RunWorker(self.processor)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_instruction)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.interrupt)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.can_continue.wakeAll()
        self.thread.finished.connect(
            lambda: (
                self.run_button.setEnabled(True),
                self.step_button.setEnabled(True)
            )
        )

    def reset_button_clicked(self):
        self.processor.reset()

    def assemble_button_clicked(self):
        if not self.assembler_file_name:
            self.save_assembler_file_as_clicked()
        try:
            data = assemble_file(self.assembler_file_name)
        except AssemblerError as e:
            # todo: Mark lines with errors
            print(e)
        else:
            for key, value in data.items():
                bytes = split_to_bytes(value)
                for byte in bytes:
                    self.processor.memory.data[key] = byte
                    key += 1

    def open_assembler_file_clicked(self):
        if self.assembler_file_unsaved_changes:
            button = QMessageBox.question(self, "Discard changes?", "You have unsaved changes. Discard?")
            if button == QMessageBox.No:
                return

        file_name = QFileDialog.getOpenFileName(
            self, "Open Assembler File", "", "Assembler Files (*.asm *.as)"
        )[0]
        with open(file_name) as file:
            self.assembler_input.setPlainText(file.read())
        self.assembler_file_name = file_name
        self.assembler_file_unsaved_changes = False
        self.show_assembler_file_name()

    def save_assembler_file_clicked(self):
        if not self.assembler_file_name:
            self.save_assembler_file_as_clicked()
        with open(self.assembler_file_name, 'w') as file:
            file.write(self.assembler_input.toPlainText())
        self.assembler_file_unsaved_changes = False

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

    def animate(self, paths):
        """Animates data transfer along the given paths
        paths: A list of lists. Each element is a list of paths that are animated in parallel.
               Then the parallel animations are executed sequentially."""
        self.animation = build_animation(paths, self)

        self.animation.finished.connect(self.stop_animation)

        self.animation_running = True
        self.animation.start()

    @Slot()
    def stop_animation(self):
        for animator in self.animators:
            animator.hide()
            animator.deleteLater()
            
        self.animators = []

        self.animation_running = False
        self.can_continue.wakeAll()
