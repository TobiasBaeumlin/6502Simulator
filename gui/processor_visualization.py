import time
from PySide6.QtCore import QObject, Signal, QMutex, QWaitCondition
from emulator.processor import Processor
from emulator.operators import set_bit
from gui.bus_geometry import AnimationPaths


class ProcessorVisualization(QObject, Processor):
    animate_signal = Signal(list)
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
        self.update_label_signal.emit('page', f'{value:02X}')

    def show_cycle_status(self, status: str):
        self.update_label_signal.emit('cycle_stage', status)
        if not self.window.animation_mode:
            time.sleep(self.window.cycle_delay)

    def animate_data_transfer(self, data_transfers):
        self.window.animation_running = True
        self.animate_signal.emit(data_transfers)
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
        # self.update_label_signal.emit('current_address', f'{value:04X}')
        self.show_address_signal.emit(value, self.memory.data)
        self.program_counter_high.set_value(value >> 8)
        self.program_counter_low.set_value(value & 0xff)

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
    def I(self, value):
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
        self.animate_data_transfer([{'path': path, 'data': data}])

    def alu_operation(self, operator):
        super().alu_operation(operator)
        self.update_label_signal.emit('alu_operator', operator)

    def cycle(self):
        super().cycle()
        self.update_label_signal.emit('cycle_counter', f'{self.cycles}')

    def fetch_byte(self, address: int) -> int:
        byte = super().fetch_byte(address)
        self.show_address_signal.emit(address, self.memory.data)
        if (address >> 8) == 1:
            self.animate_data_transfer([{'path': AnimationPaths['AR']['MA'], 'data': f'{address:04X}'}])
            self.update_label_signal.emit('data_zp', f'{byte:02X}')
        else:
            self.animate_data_transfer([{'path': AnimationPaths['AR']['ZA'], 'data': f'{address:02X}'}])
            self.update_label_signal.emit('data_mem', f'{byte:02X}')
        return byte

    def fetch_byte_to_register(self, address: int, register: str) -> None:
        super().fetch_byte_to_register(address, register)
        page = address >> 0
        if page == 1:
            path = AnimationPaths['ZD'][register]
        else:
            path = AnimationPaths['MD'][register]
        self.animate_data_transfer([{'path': path, 'data': self.__getattribute__(register)}])

    def put_byte(self, address: int, byte: int) -> None:
        super().put_byte(address, byte)
        self.show_address_signal.emit(address, self.memory.data)
        self.update_label_signal.emit('data', f'{byte:02x}')

    def push_pc_to_stack(self, word: int) -> None:
        super().push_pc_to_stack(word)
        self.animate_data_transfer([{'path': AnimationPaths['PC']['MD'], 'data': f'{(word & 0xff):02x}'}])
        self.animate_data_transfer([{'path': AnimationPaths['PC']['MD'], 'data': f'{(word >> 0xff):02x}'}])

    def pull_pc_from_stack(self) -> None:
        super().pull_pc_from_stack()
        self.animate_data_transfer([{'path': AnimationPaths['MD']['PC'], 'data': f'{(self.PC & 0xff):02x}'}])
        self.animate_data_transfer([{'path': AnimationPaths['PC']['MD'], 'data': f'{(self.PC >> 0xff):02x}'}])

    def fetch_instruction(self) -> int:
        self.show_cycle_status('fetch')
        data = f'{self.PC:04X}'
        self.animate_data_transfer([{'path': AnimationPaths['PC']['AR'], 'data': data}])
        op_code = super().fetch_instruction()
        data = f'{op_code:02X}'
        self.animate_data_transfer([{'path': AnimationPaths['MD']['IR'], 'data': data}])
        return op_code

    def run_instruction(self):
        super().run_instruction()

    def decode(self, op_code: int) -> None:
        self.show_cycle_status('decode')
        super().decode(op_code)

    def load_register(self, register: str, mode: str, index_register=None) -> None:
        self.show_cycle_status('run')
        # path = AnimationPaths['MD'][register]
        # self.animate_data_transfer([{'path': path, 'data': str(self.__getattribute__(register))}])
        super().load_register(register, mode, index_register)

    def store_register(self, register: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        # path = AnimationPaths[register]['MD']
        # self.animate_data_transfer([{'path': path, 'data': str(self.__getattribute__(register))}])
        super().store_register(register, mode, index_register)

    def transfer_register(self, source: str, destination: str) -> None:
        self.show_cycle_status('run')
        path = AnimationPaths[source][destination]
        self.animate_data_transfer([{'path': path, 'data': str(self.__getattribute__(source))}])
        super().transfer_register(source, destination)

    def add_with_carry(self, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().add_with_carry(mode, index_register)
        # self.animate_data_transfer([{'path': self.window.paths.dat_al_i2, 'data': '-1'},
        #                            {'path': self.window.paths.ac_al_i1, 'data': '-1'}])
        # self.animate_data_transfer([{'path': self.window.paths.al_o_ac, 'data': '-1'}])

    def subtract_with_carry(self, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().subtract_with_carry(mode, index_register)
        # self.animate_data_transfer([{'path': self.window.paths.dat_al_i2, 'data': '-1'},
        #                            {'path': self.window.paths.ac_al_i1, 'data': '-1'}])
        # self.animate_data_transfer([{'path': self.window.paths.al_o_ac, 'data': '-1'}])

    def logical_operation(self, operator: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().logical_operation(operator, mode, index_register)
        # self.animate_data_transfer([{'path': self.window.paths.dat_al_i2, 'data': '-1'},
        #                             {'path': self.window.paths.ac_al_i1, 'data': '-1'}])
        # self.animate_data_transfer([{'path': self.window.paths.al_o_ac, 'data': '-1'}])

    def compare(self, register: str, mode: str, index_register: str = None) -> None:
        self.show_cycle_status('run')
        super().compare(register, mode, index_register)
        # self.animate_data_transfer([{'path': self.window.paths.dat_al_i2, 'data': '-1'},
        #                             {'path': self.window.paths.ac_al_i1, 'data': '-1'}])
        # self.animate_data_transfer([{'path': self.window.paths.al_o_sr, 'data': '-1'}])

    def branch(self, flag: str, state: bool) -> None:
        self.show_cycle_status('run')
        super().branch(flag, state)
        data = '1' if state else '0'
        # self.animate_data_transfer([{'path': self.window.paths.dat_pc, 'data': '-1'},
        #                             {'path': self.window.paths.sr_pc, 'data': data}])

    def set_flag(self, flag: str, state: bool) -> None:
        self.show_cycle_status('run')
        super().set_flag(flag, state)
        data = '1' if state else '0'
        # self.animate_data_transfer([{'path': self.window.paths.ir_sr, 'data': data}])

    def increment(self, increment:int, mode: str, index_register: str=None) -> None:
        self.show_cycle_status('run')
        super().increment(increment, mode, index_register)
        self.animate_data_transfer([{'path': self.window.paths.dat_al_i2, 'data': '-1'},
                                    {'path': self.window.paths.ir_al_i1, 'data': str(increment)}])
        # Todo: Set ALU
        # self.animate_data_transfer([{'path': self.window.paths.al_0_dat, 'data': '-1'}])

    def increment_register(self, step: int, register: str) -> None:
        self.show_cycle_status('run')
        super().increment_register(step, register)
        # if register == 'X':
        #     path = [{'path': self.window.paths.ir_ix, 'data': f'{self.X:02X}'}]
        # else:
        #     path = [{'path': self.window.paths.ir_iy, 'data': f'{self.Y:02X}'}]
        # self.animate_data_transfer(path)

    def push_processor_status(self) -> None:
        self.show_cycle_status('run')
        super().push_processor_status()
        # self.animate_data_transfer([{'path': self.window.paths.sr_mem, 'data': f'{self.status.value:02X}'}])

    def push_accumulator(self) -> None:
        self.show_cycle_status('run')
        super().push_accumulator()
        # self.animate_data_transfer([{'path': self.window.paths.ac_dat, 'data': f'{self.A:02X}'}])

    def pull_processor_status(self) -> None:
        self.show_cycle_status('run')
        super().pull_processor_status()
        # self.animate_data_transfer([{'path': self.window.paths.dat_sr, 'data': f'{self.status.value:02X}'}])

    def pull_accumulator(self) -> None:
        self.show_cycle_status('run')
        super().pull_accumulator()
        # self.animate_data_transfer([{'path': self.window.paths.dat_ac, 'data': f'{self.A:02X}'}])

    def jump(self, mode) -> None:
        self.show_cycle_status('run')
        super().jump(mode)
        # self.animate_data_transfer([{'path': self.window.paths.dat_pc, 'data': f'{self.PC:02X}'}])

    def jump_to_subroutine(self):
        self.show_cycle_status('run')
        # super().jump_to_subroutine()

    def return_from_subroutine(self):
        self.show_cycle_status('run')
        super().return_from_subroutine()
        # self.animate_data_transfer([{'path': self.window.paths.sr_dat, 'data': f'{self.status.value:02x}'}])
        # self.animate_data_transfer([{'path': self.window.paths.dat_pc, 'data': f'{self.PC & 0xff}'}])
        # self.animate_data_transfer([{'path': self.window.paths.dat_pc, 'data': f'{self.PC >> 8}'}])



