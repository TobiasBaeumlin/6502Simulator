import time
from PySide6.QtCore import QObject, Signal, QMutex, QWaitCondition
from emulator.processor import Processor
from emulator.operators import set_bit
from gui.bus_geometry import AnimationPaths


class ProcessorVisualization(QObject, Processor):
    animate_signal = Signal(dict)
    update_label_signal = Signal(str, object)
    show_page_signal = Signal(int, object)
    show_address_signal = Signal(int, object)

    def __init__(self,  window, mutex: QMutex, can_continue: QWaitCondition):
        super().__init__()
        self.window = window
        self.mutex = mutex
        self.can_continue = can_continue

        self.interrupt_requested = False
        self.single_cycle = False  # Do not stop after each cycle
        self.cycle_delay = 1  # Wait for 1s after each cycle
        self.shown_page = 0
        self.shown_page_row = 0
        self.shown_page_col = 0
        self._current_page = 0
        self.animate_signal.connect(window.animate)
        self.update_label_signal.connect(window.update_label)
        self.show_page_signal.connect(window.show_page)
        self.show_address_signal.connect(window.show_memory_address)

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, value: int) -> None:
        assert 0 <= value < 0x100
        self._current_page = value
        self.show_page_signal.emit(value, self.memory.data)
        self.update_label_signal.emit('page', f'{value:{self.byte_format}}')

    def show_cycle_status(self, status: str):
        self.update_label_signal.emit('cycle_stage', status)
        if not self.window.animation_mode:
            time.sleep(self.window.cycle_delay)

    # Blocks while the animation in the gui is running
    def animate_data_transfer(self, data_transfer):
        self.window.animation_running = True
        self.animate_signal.emit(data_transfer)
        while self.window.animation_running:
            pass

    # Overriding methods from class Processor
    @Processor.CI.setter
    def CI(self, value: str) -> None:
        self.current_instruction = value
        if not self.window.animation_mode:
            time.sleep(self.window.cycle_delay)
        self.update_label_signal.emit('current_instruction', value)

    @Processor.PC.setter
    def PC(self, value: int) -> None:
        assert 0 <= value < 0x10000
        self.update_label_signal.emit('program_counter_high_byte', (value >> 8))
        self.update_label_signal.emit('program_counter_low_byte', (value & 0xff))
        self.show_address_signal.emit(value, self.memory.data)
        self.program_counter_high.set_value(value >> 8)
        self.program_counter_low.set_value(value & 0xff)

    @Processor.AR.setter
    def AR(self, value):
        assert 0 <= value < 0x10000
        self.update_label_signal.emit('address_register_high_byte', (value >> 8))
        self.update_label_signal.emit('address_register_low_byte', (value & 0xff))
        self.address_register_high.set_value(value >> 8)
        self.address_register_low.set_value(value & 0xff)

    @Processor.SP.setter
    def SP(self, value):
        self.update_label_signal.emit('stack_pointer', value)
        self.stack_pointer.set_value(value)

    @Processor.A.setter
    def A(self, value):
        self.update_label_signal.emit('accumulator', value)
        self.update_label_signal.emit('accumulator_binary', value)
        self.accumulator.set_value(value)

    @Processor.X.setter
    def X(self, value):
        self.update_label_signal.emit('index_x', value)
        self.index_x.set_value(value)

    @Processor.Y.setter
    def Y(self, value):
        self.update_label_signal.emit('index_y', value)
        self.index_y.set_value(value)

    @Processor.C.setter
    def C(self, value):
        self.update_label_signal.emit('flag_c', value)
        self.status.value = set_bit(self.status.value, 0, value)

    @Processor.Z.setter
    def Z(self, value):
        self.update_label_signal.emit('flag_z', value)
        self.status.value = set_bit(self.status.value, 1, value)

    @Processor.I.setter
    def I(self, value):                   # noqa e743
        self.update_label_signal.emit('flag_i', value)
        self.status.value = set_bit(self.status.value, 2, value)

    @Processor.D.setter
    def D(self, value):
        self.update_label_signal.emit('flag_d', value)
        self.status.value = set_bit(self.status.value, 3, value)

    @Processor.B.setter
    def B(self, value):
        self.update_label_signal.emit('flag_b', value)
        self.status.value = set_bit(self.status.value, 4, value)

    @Processor.V.setter
    def V(self, value):
        self.update_label_signal.emit('flag_v', value)
        self.status.value = set_bit(self.status.value, 6, value)

    @Processor.N.setter
    def N(self, value):
        self.update_label_signal.emit('flag_n', value)
        self.status.value = set_bit(self.status.value, 7, value)

    def reset(self) -> None:
        super().reset()
        self.update_label_signal.emit('cycle_stage', '')

    def set_zero_and_negative_status_flags(self, register: str = 'RES') -> None:
        super().set_zero_and_negative_status_flags(register)
        data = f'N:{self.N} Z:{self.Z}'
        path = AnimationPaths[register]['SR']
        self.animate_data_transfer({'path': path, 'data': data})

    def alu_operation(self, operator):
        super().alu_operation(operator)
        self.update_label_signal.emit('alu_operator', operator)

    def cycle(self):
        super().cycle()
        self.update_label_signal.emit('cycle_counter', f'{self.cycles}')

    def copy_byte(self, from_register: str, to_register: str) -> None:
        super().copy_byte(from_register, to_register)
        data = self.__getattribute__(from_register)
        self.animate_data_transfer({'path': AnimationPaths[from_register][to_register],
                                    'data': f'{data:{self.byte_format}}'})

    def fetch_byte(self) -> int:
        byte = super().fetch_byte()
        self.show_address_signal.emit(self.AR, self.memory.data)
        self.animate_data_transfer({'path': AnimationPaths['AR']['ZA'],
                                    'data': f'{self.AR:{self.byte_format}}'})
        if (self.AR >> 8) == 0:
            self.update_label_signal.emit('data_mem',
                                          f'{byte:{self.byte_format}}')
        else:
            self.update_label_signal.emit('data_zp',
                                          f'{byte:{self.byte_format}}')
        return byte

    def fetch_byte_to_register(self, register: str) -> None:
        super().fetch_byte_to_register(register)
        if (self.AR >> 8) == 0:
            path = AnimationPaths['ZD'][register]
        else:
            path = AnimationPaths['MD'][register]
        self.animate_data_transfer({'path': path,
                                    'data': f'{getattr(self, register):{self.byte_format}}'})

    def put_byte(self, byte: int) -> None:
        super().put_byte(byte)
        if (self.AR >> 8) == 0:
            self.update_label_signal.emit('data_zp', f'{byte:{self.byte_format}}')
        else:
            self.update_label_signal.emit('data_mem', f'{byte:{self.byte_format}}')

    def put_byte_from_register(self, register: str) -> None:
        super().put_byte_from_register(register)
        if (self.AR >> 8) == 0:
            self.animate_data_transfer({'path': AnimationPaths[register]['ZD'],
                                        'data': f'{getattr(self, register):{self.byte_format}}'})
        else:
            self.animate_data_transfer({'path': AnimationPaths[register]['ZD'],
                                        'data': f'{getattr(self, register)}:{self.byte_format}'})

    def push_pc_to_stack(self, word: int) -> None:
        super().push_pc_to_stack(word)
        self.animate_data_transfer({'path': AnimationPaths['PC']['MD'],
                                    'data': f'{(word & 0xff):{self.byte_format}}'})
        self.animate_data_transfer({'path': AnimationPaths['PC']['MD'],
                                    'data': f'{(word >> 0xff):{self.byte_format}}'})

    def pull_pc_from_stack(self) -> None:
        super().pull_pc_from_stack()
        self.animate_data_transfer({'path': AnimationPaths['MD']['PC'],
                                    'data': f'{(self.PC & 0xff):{self.byte_format}}'})
        self.animate_data_transfer({'path': AnimationPaths['PC']['MD'],
                                    'data': f'{(self.PC >> 0xff):{self.byte_format}}'})

    def fetch_instruction(self) -> None:
        self.show_cycle_status('fetch')
        address = f'{self.PC:{self.word_format}}'
        self.animate_data_transfer({'path': AnimationPaths['PC']['AR'], 'data': address})
        super().fetch_instruction()
        if (self.PC >> 8) == 0:
            self.animate_data_transfer({'path': AnimationPaths['ZD']['IR'],
                                        'data': f'{self.IR:{self.byte_format}}'})
        else:
            self.animate_data_transfer({'path': AnimationPaths['MD']['IR'],
                                        'data': f'{self.IR:{self.byte_format}}'})

    def load_register(self, register: str, mode: str, index_register=None) -> None:
        self.show_cycle_status('run')
        super().load_register(register, mode, index_register)

    def store_register(self, register: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().store_register(register, mode, index_register)

    def transfer_register(self, source: str, destination: str) -> None:
        self.show_cycle_status('run')
        path = AnimationPaths[source][destination]
        self.animate_data_transfer({'path': path,
                                    'data': str(self.__getattribute__(source))})

        super().transfer_register(source, destination)

    def arithmetic_operation(self, operator: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().arithmetic_operation(operator, mode, index_register)

    def compare(self, register: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().compare(register, mode, index_register)

    def branch(self, flag: str, state: bool) -> None:
        self.show_cycle_status('run')
        super().branch(flag, state)

    def set_flag(self, flag: str, state: bool) -> None:
        self.show_cycle_status('run')
        super().set_flag(flag, state)

    def increment(self, increment: int, mode: str, index_register: str=None) -> None:  # noqa 252
        self.show_cycle_status('run')
        super().increment(increment, mode, index_register)
        # self.animate_data_transfer({'path': self.window.paths.dat_al_i2, 'data': '-1'},
        #                             {'path': self.window.paths.ir_al_i1, 'data': str(increment)})

    def increment_register(self, step: int, register: str) -> None:
        self.show_cycle_status('run')
        super().increment_register(step, register)

    def push_processor_status(self) -> None:
        self.show_cycle_status('run')
        super().push_processor_status()

    def push_accumulator(self) -> None:
        self.show_cycle_status('run')
        super().push_accumulator()

    def pull_processor_status(self) -> None:
        self.show_cycle_status('run')
        super().pull_processor_status()

    def pull_accumulator(self) -> None:
        self.show_cycle_status('run')
        super().pull_accumulator()

    def jump(self, mode) -> None:
        self.show_cycle_status('run')
        super().jump(mode)

    def jump_to_subroutine(self):
        self.show_cycle_status('run')
        super().jump_to_subroutine()

    def return_from_subroutine(self):
        self.show_cycle_status('run')
        super().return_from_subroutine()

    def run_instruction(self):
        super().run_instruction()

    def decode_instruction(self) -> None:
        self.show_cycle_status('decode')
        super().decode_instruction()
