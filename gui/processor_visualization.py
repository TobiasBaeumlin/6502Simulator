import time
from PySide6.QtCore import QObject, Signal
from emulator.processor import Processor
from emulator.operators import set_bit
from gui.bus_geometry import AnimationPaths

ADDRESS_MODES_SHORT = {
    'immediate': 'imm',
    'zero_page': 'zp',
    'zero_page_indexed': 'zp_idx',
    'absolute': 'abs',
    'absolute_indexed': 'abs_idx',
    'indexed_indirect_x': 'idx_x_ind',
    'indirect_indexed_y': 'ind_idx_y',
}


def build_address_mode_string(mode: str, index_register: str) -> str:
    result = ADDRESS_MODES_SHORT[mode]
    if index_register:
        result += ',' + index_register
    return result


class ProcessorVisualization(QObject, Processor):
    animate_signal = Signal(dict, list)
    update_label_signal = Signal(str, object)
    show_page_signal = Signal(int)
    show_address_signal = Signal(int)
    highlight_pc_in_assembler_signal = Signal(int)

    def __init__(self, window):
        super().__init__()
        self.window = window

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
        self.highlight_pc_in_assembler_signal.connect(window.assembler_input.highlight_pc_line)
        # Current instruction in disassembled form
        self.current_instruction = ''

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, value: int) -> None:
        assert 0 <= value < 0x100
        self._current_page = value
        self.show_page_signal.emit(value)
        self.update_label('page', f'{value:{self.byte_format}}')

    def show_cycle_status(self, status: str):
        self.update_label('cycle_stage', status)
        if self.window.animation_mode and status == 'decode':
            time.sleep(0.5)
        if not self.window.animation_mode:
            time.sleep(self.window.cycle_delay)

    # Blocks while the animation in the gui is running
    def animate_data_transfer(self, data_transfer, destination=None):
        if destination is None:
            destinations = []
        elif destination == 'AR':
            destinations = ['ARH', 'ARL']
        elif destination == 'PC':
            destinations = ['PCH', 'PCL']
        elif destination == 'A':
            destinations = ['A', 'AB']
        else:
            destinations = [destination]
        self.window.animation_running = True
        self.animate_signal.emit(data_transfer, destinations)
        time.sleep(0.1)
        while self.window.animation_running:
            pass

    def update_label(self, label, value):
        self.update_label_signal.emit(label, value)

    def highlight_pc_in_assembler(self):
        print('highlight_pc_in_assembler', self.PC)
        if self.PC in self.window.debug_info:
            print('sending signal')
            self.highlight_pc_in_assembler_signal.emit(self.window.debug_info[self.PC]-1)

    # Overriding methods from class Processor
    @property
    def CI(self):
        return self.current_instruction

    @CI.setter
    def CI(self, value):
        self.current_instruction = value
        if not self.window.animation_mode:
            time.sleep(self.window.cycle_delay)
        self.update_label('current_instruction', value)

    @Processor.PC.setter
    def PC(self, value: int) -> None:
        assert 0 <= value < 0x10000
        self.update_label('program_counter_high_byte', (value >> 8))
        self.update_label('program_counter_low_byte', (value & 0xff))
        self.program_counter_high.set_value(value >> 8)
        self.program_counter_low.set_value(value & 0xff)

    @Processor.AR.setter
    def AR(self, value):
        assert 0 <= value < 0x10000
        self.ARH = (value >> 8)
        self.ARL = (value & 0xff)

    @Processor.ARH.setter
    def ARH(self, value):
        assert 0 <= value < 0x100
        self.update_label('address_register_high_byte', value)
        self.address_register_high.set_value(value)

    @Processor.ARL.setter
    def ARL(self, value):
        assert 0 <= value < 0x100
        self.update_label('address_register_low_byte', value)
        self.address_register_low.set_value(value)

    @Processor.S.setter
    def S(self, value):
        self.update_label('stack_pointer', value)
        self.stack_pointer.set_value(value)

    @Processor.A.setter
    def A(self, value):
        self.update_label('accumulator', value)
        self.update_label('accumulator_binary', value)
        self.accumulator.set_value(value)

    # Binary representation of register A
    @property
    def AB(self):
        return f'{self.A:08b}'

    @Processor.X.setter
    def X(self, value):
        self.update_label('index_x', value)
        self.index_x.set_value(value)

    @Processor.Y.setter
    def Y(self, value):
        self.update_label('index_y', value)
        self.index_y.set_value(value)

    @Processor.C.setter
    def C(self, value):
        self.update_label('flag_c', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 0, value)

    @Processor.Z.setter
    def Z(self, value):
        self.update_label('flag_z', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 1, value)

    @Processor.I.setter
    def I(self, value):  # noqa e743
        self.update_label('flag_i', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 2, value)

    @Processor.D.setter
    def D(self, value):
        self.update_label('flag_d', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 3, value)

    @Processor.B.setter
    def B(self, value):
        self.update_label('flag_b', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 4, value)

    @Processor.V.setter
    def V(self, value):
        self.update_label('flag_v', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 6, value)

    @Processor.N.setter
    def N(self, value):
        self.update_label('flag_n', '1' if value else '0')
        self.status.value = set_bit(self.status.value, 7, value)

    @Processor.OP1.setter
    def OP1(self, value):
        # if not self.window.animation_mode:
        self.update_label('alu_op1', value)
        self.alu_op_1.set_value(value)

    @Processor.OP2.setter
    def OP2(self, value):
        self.update_label('alu_op2', value)
        self.alu_op_2.set_value(value)

    @Processor.RES.setter
    def RES(self, value):
        self.update_label('alu_res', value)
        self.alu_res.set_value(value)

    @Processor.IR.setter
    def IR(self, value):
        self.update_label('instruction_register', value)
        self.instruction_register.set_value(value)

    # Address modes
    def immediate(self):
        super().immediate()

    def zero_page(self):
        super().zero_page()
        self.CI = self.CI[:3] + f' ${self.AR:02X}'

    def zero_page_indexed(self, register, penalty_cycle=False):
        super().zero_page_indexed(register, penalty_cycle)
        self.CI = self.CI[:3] + f' ${self.AR:02X},${getattr(self, register)}'

    def absolute(self):
        super().absolute()
        self.CI = self.CI[:3] + f' ${self.AR:04X}'

    def absolute_indexed(self, register, penalty_cycle=False) -> None:
        super().absolute_indexed(register, penalty_cycle)
        self.CI = self.CI[:3] + f' ${self.AR:04X},${getattr(self, register)}'

    def indexed_indirect_x(self) -> None:
        super().indexed_indirect_x()
        self.CI = self.CI[:3] + f' (${self.AR:04X},${self.X})'

    def indirect_indexed_y(self) -> None:
        super().indirect_indexed_y()
        self.CI = self.CI[:3] + f' (${self.AR:04X}),${self.Y}'

    def indirect(self) -> None:
        super().indirect()
        self.CI = self.CI[:3] + f' (${self.AR:04X})'

    def reset(self) -> None:
        super().reset()
        self.update_label('cycle_stage', '')
        self.window.show_page(self.memory.data[0xfffc])
        self.window.show_memory_address(self.PC)

    def set_zero_and_negative_status_flags(self, register: str = 'RES') -> None:
        super().set_zero_and_negative_status_flags(register)
        if self.window.animation_mode:
            data = f'N:{self.N} Z:{self.Z}'
            path = AnimationPaths[register]['SR']
            self.animate_data_transfer({'path': path, 'data': data})

    def alu_operation(self, operator):
        super().alu_operation(operator)
        self.update_label('alu_operator', operator)

    def cycle(self):
        super().cycle()
        self.update_label('cycle_counter', f'{self.cycles}')

    def copy_byte(self, from_register: str, to_register: str) -> None:
        if self.window.animation_mode:
            data = self.__getattribute__(from_register)
            self.animate_data_transfer({'path': AnimationPaths[from_register][to_register],
                                        'data': f'{data:{self.byte_format}}'}, to_register)
        super().copy_byte(from_register, to_register)

    def fetch_byte(self) -> int:
        if self.window.animation_mode:
            data = f'{self.AR:{self.byte_format}}'
            if self.AR >> 8 == 0:
                path = AnimationPaths['AR']['ZA']
            else:
                path = AnimationPaths['AR']['MA']
            self.animate_data_transfer({'path': path, 'data': data})
        self.show_address_signal.emit(self.AR)
        byte = super().fetch_byte()
        return byte

    def fetch_byte_to_register(self, register: str) -> None:
        if self.window.animation_mode:
            if (self.AR >> 8) == 0:
                path = AnimationPaths['ZD'][register]
            else:
                path = AnimationPaths['MD'][register]
            data = f'{self.memory.data[self.AR]:{self.byte_format}}'
        byte = self.fetch_byte()
        if self.window.animation_mode:
            self.animate_data_transfer({'path': path, 'data': data}, register)
        setattr(self, register, byte)

    def fetch_byte_at_pc(self) -> int:
        if self.window.animation_mode:
            data = f'{self.PC:{self.byte_format}}'
            if self.PC >> 8 == 0:
                path = AnimationPaths['PC']['ZA']
            else:
                path = AnimationPaths['PC']['MA']
            self.animate_data_transfer({'path': path, 'data': data})
        self.show_address_signal.emit(self.PC)
        if self.window.animation_mode:
            self.update_label('program_counter_high_byte', self.PCH)
            self.update_label('program_counter_low_byte', self.PCL)
        return super().fetch_byte_at_pc()

    def fetch_byte_at_pc_to_register(self, register: str) -> None:
        if self.window.animation_mode:
            if (self.PC >> 8) == 0:
                path = AnimationPaths['ZD'][register]
            else:
                path = AnimationPaths['MD'][register]
            data = f'{self.memory.data[self.PC]:{self.byte_format}}'
        byte = self.fetch_byte_at_pc()
        if self.window.animation_mode:
            self.animate_data_transfer({'path': path, 'data': data}, register)
        setattr(self, register, byte)

    def put_byte_from_register(self, register: str) -> None:
        if self.window.animation_mode:
            data = f'{getattr(self, register):{self.byte_format}}'
        super().put_byte_from_register(register)
        if self.window.animation_mode:
            if (self.AR >> 8) == 0:
                path = AnimationPaths[register]['ZD']
            else:
                path = AnimationPaths[register]['MD']
            self.animate_data_transfer({'path': path, 'data': data})
        self.cycle()
        self.memory.data[self.AR] = getattr(self, register)
        self.show_address_signal.emit(self.AR)

    def push_pc_to_stack(self, word: int) -> None:
        if self.window.animation_mode:
            data = f'{(word & 0xff):{self.byte_format}}'
            self.animate_data_transfer({'path': AnimationPaths['PC']['MD'], 'data': data})
        if self.window.animation_mode:
            data = f'{(word >> 0xff):{self.byte_format}}'
            self.animate_data_transfer({'path': AnimationPaths['PC']['MD'], 'data': data})
        super().push_pc_to_stack(word)

    def pull_pc_from_stack(self) -> None:
        if self.window.animation_mode:
            self.animate_data_transfer({'path': AnimationPaths['MD']['PC'],
                                        'data': f'{(self.PC & 0xff):{self.byte_format}}'}, 'PC')
            self.animate_data_transfer({'path': AnimationPaths['PC']['MD'],
                                        'data': f'{(self.PC >> 0xff):{self.byte_format}}'})
        super().pull_pc_from_stack()

    def fetch_instruction(self) -> None:
        self.show_cycle_status('fetch')
        super().fetch_instruction()

    def run_instruction(self) -> None:
        self.highlight_pc_in_assembler()
        super().run_instruction()

    # Processor instructions
    def load_register(self, register: str, mode: str, index_register=None) -> None:
        self.CI = f'LD{register} {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().load_register(register, mode, index_register)
        if mode == 'immediate':
            self.CI = self.CI[:3] + f' ${self.memory.data[self.AR]:02X}'

    def store_register(self, register: str, mode: str, index_register: str = None) -> None:
        self.CI = f'ST{register} {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().store_register(register, mode, index_register)

    def transfer_register(self, source: str, destination: str) -> None:
        self.CI = f'T{source}{destination}'
        self.show_cycle_status('run')
        if self.window.animation_mode:
            path = AnimationPaths[source][destination]
            self.animate_data_transfer({'path': path,
                                        'data': str(getattr(self, source))}, destination)
        super().transfer_register(source, destination)

    def arithmetic_operation(self, operator: str, mode: str, index_register: str = None) -> None:
        self.CI = f'{operator[0:3].upper()} {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().arithmetic_operation(operator, mode, index_register)
        if mode == 'immediate':
            self.CI = self.CI[:3] + f' ${self.memory.data[self.AR]:02X}'

    def compare(self, register: str, mode: str, index_register: str = None) -> None:
        if register == 'A':
            self.CI = f'CMP {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'CP{register} {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().compare(register, mode, index_register)
        if mode == 'immediate':
            self.CI = self.CI[:3] + f' ${self.memory.data[self.AR]:02X}'

    def bit_test(self, mode: str, index_register: str = None) -> None:
        self.CI = f'BIT {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().bit_test(mode, index_register)

    def shift_accumulator(self, left: bool = True) -> None:
        if left:
            self.CI = 'ASL A'
        else:
            self.CI = 'LSR A'
        self.show_cycle_status('run')
        super().shift_accumulator(left)

    def shift_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        if left:
            self.CI = f'ASL {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'LSR {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().shift_memory(mode, index_register, left)

    def rotate_accumulator(self, left: bool = True) -> None:
        if left:
            self.CI = 'ROL A'
        else:
            self.CI = 'ROR A'
        self.show_cycle_status('run')
        super().rotate_accumulator(left)

    def rotate_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        if left:
            self.CI = f'ROL {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'ROR {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().rotate_memory(mode, index_register, left)

    def increment_register(self, increment: int, register: str) -> None:
        if increment == 1:
            self.CI = f'IN{register}'
        else:
            self.CI = f'DE{register}'
        self.show_cycle_status('run')
        super().increment_register(increment, register)

    def increment(self, increment: int, mode: str, index_register: str = None) -> None:  # noqa 252
        if increment == 1:
            self.CI = f'INC {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'DEC {build_address_mode_string(mode, index_register)}'
        self.show_cycle_status('run')
        super().increment(increment, mode, index_register)

    def branch(self, flag: str, state: bool) -> None:
        if flag == 'V' and state is True:
            self.CI = 'BVS'
        if flag == 'V' and state is False:
            self.CI = 'BVC'
        if flag == 'Z' and state is True:
            self.CI = 'BEQ'
        if flag == 'Z' and state is False:
            self.CI = 'BNE'
        if flag == 'N' and state is True:
            self.CI = 'BMI'
        if flag == 'N' and state is False:
            self.CI = 'BPL'
        if flag == 'C' and state is True:
            self.CI = 'BCS'
        if flag == 'C' and state is False:
            self.CI = 'BCC'
        self.show_cycle_status('run')
        super().branch(flag, state)

    def set_flag(self, flag: str, state: bool) -> None:
        if state is True:
            self.CI = f'SE{flag}'
        else:
            self.CI = f'CL{flag}'
        self.show_cycle_status('run')
        if self.window.animation_mode:
            self.animate_data_transfer({'path': AnimationPaths['IR']['SR'], 'data': f'{flag}:{int(state)}'}, 'S')
        super().set_flag(flag, state)

    def push_processor_status(self) -> None:
        self.CI = 'PHP'
        self.show_cycle_status('run')
        super().push_processor_status()

    def push_accumulator(self) -> None:
        self.CI = 'PHA'
        self.show_cycle_status('run')
        super().push_accumulator()

    def pull_processor_status(self) -> None:
        self.CI = 'PLP'
        self.show_cycle_status('run')
        super().pull_processor_status()

    def pull_accumulator(self) -> None:
        self.CI = 'PLP'
        self.show_cycle_status('run')
        super().pull_accumulator()

    def jump(self, mode) -> None:
        self.CI = f'JMP {mode}'
        self.show_cycle_status('run')
        super().jump(mode)

    def jump_to_subroutine(self):
        self.CI = 'JSR'
        self.show_cycle_status('run')
        super().jump_to_subroutine()

    def return_from_subroutine(self):
        self.CI = 'RTS'
        self.show_cycle_status('run')
        super().return_from_subroutine()

    def brk(self):
        self.CI = 'BRK'
        self.show_cycle_status('run')

    def return_from_interrupt(self):
        self.CI = 'RTI'
        self.show_cycle_status('run')
        super().return_from_interrupt()

    def decode_instruction(self) -> None:
        self.show_cycle_status('decode')
        super().decode_instruction()
