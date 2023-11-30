import array as ar
from operator import inv, or_, xor, and_  # noqa
from emulator.opcodes import *
from emulator.operators import unsigned_byte_addition, shl, shr, set_bit, cmp, sbb, adc, inc

START_ADDR = 0x0000

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


class Memory:
    def __init__(self, size: int) -> None:
        assert size > 2**12, size <= 2**16
        self.size = size
        self.data = ar.array('B', [0] * self.size)

    def initialise(self) -> None:
        self.data = ar.array('B', [0] * self.size)


class Register:
    def __init__(self, init=0) -> None:
        self.value = init   

    def get_value(self) -> int:
        return self.value

    def set_value(self, value) -> None:
        self.value = value
   
    
class Processor:
    def __init__(self, memory_size=2**16) -> None:
        self.memory_size = memory_size
        self.memory = Memory(memory_size)
        self.program_counter_high = Register(init=START_ADDR >> 8)      # Program counter high byte
        self.program_counter_low = Register(init=START_ADDR & 0xff)     # Program counter low byte
        self.stack_pointer = Register(init=0xff)  # Stack pointer; stack is top down, starts at 0x01ff
        # Registers
        self.accumulator = Register()          # Accumulator
        self.index_x = Register()              # Index register X
        self.index_y = Register()              # Index register Y
        self.status = Register()               # Status register
        # ALU with two virtual registers for the operands and one for the result
        self.alu_op_1 = Register()
        self.alu_op_2 = Register()
        self.alu_res = Register()
        # Cycle counter
        self.cycles = 0
        # Current instruction in disassembled form
        self.current_instruction = ''

    @property
    def PC(self):
        return (self.program_counter_high.value << 8) + self.program_counter_low.value
    @ PC.setter
    def PC(self, value):
        assert 0 <= value < 0x10000
        self.program_counter_high.set_value(value >> 8)
        self.program_counter_low.set_value(value & 0xff)

    @property
    def PCH(self):
        return self.program_counter_high.get_value

    @ PCH.setter
    def PCH(self, value):
        self.program_counter_high.set_value(value)

    @property
    def PCL(self):
        return self.program_counter_low.value

    @ PCL.setter
    def PCL(self, value):
        self.program_counter_low.set_value(value)

    @property
    def SP(self):
        return self.stack_pointer.value

    @ SP.setter
    def SP(self, value):
        self.stack_pointer.set_value(value)

    @property
    def A(self):
        return self.accumulator.value

    @ A.setter
    def A(self, value):
        self.accumulator.set_value(value)

    @property
    def X(self):
        return self.index_x.value    

    @ X.setter
    def X(self, value):
        self.index_x.set_value(value)

    @property
    def Y(self):
        return self.index_y.value

    @ Y.setter
    def Y(self, value):
        self.index_y.set_value(value)

    @property
    def C(self):
        return self.status.value & 1

    @ C.setter
    def C(self, value):
        self.status.value = set_bit(self.status.value, 0, value)

    @property
    def Z(self):
        return (self.status.value >> 1) & 1

    @ Z.setter
    def Z(self, value):
        self.status.value = set_bit(self.status.value, 1, value)
    
    @property
    def I(self):
        return (self.status.value >> 2) & 1

    @ I.setter
    def I(self, value):
        self.status.value = set_bit(self.status.value, 2, value)
    
    @property
    def D(self):
        return (self.status.value >> 3) & 1

    @ D.setter
    def D(self, value):
        self.status.value = set_bit(self.status.value, 3, value)
    
    @property
    def B(self):
        return (self.status.value >> 4) & 1

    @ B.setter
    def B(self, value):
        self.status.value = set_bit(self.status.value, 4, value)

    @property
    def V(self):
        return (self.status.value >> 6) & 1

    @ V.setter
    def V(self, value):
        self.status.value = set_bit(self.status.value, 6, value)

    @property
    def N(self):
        return (self.status.value >> 7) & 1

    @ N.setter
    def N(self, value):
        self.status.value = set_bit(self.status.value, 7, value)
    
    @property
    def CI(self):
        return self.current_instruction

    @ CI.setter
    def CI(self, value):
        self.current_instruction = value

    @property
    def OP1(self):
        return self.alu_op_1.value

    @ OP1.setter
    def OP1(self, value):
        self.alu_op_1.set_value(value)

    @property
    def OP2(self):
        return self.alu_op_2.value

    @OP2.setter
    def OP2(self, value):
        self.alu_op_2.set_value(value)

    @property
    def RES(self):
        return self.alu_res.value

    @RES.setter
    def RES(self, value):
        self.alu_res.set_value(value)

    def reset(self) -> None:
        # Reset vector is at $fffc, $fffd
        self.PC = (self.memory.data[0xfffc] << 8) + self.memory.data[0xfffd]
        self.SP = 0xff                 
        self.A = self.X = self.Y = 0
        self.C = self.Z = self.I = self.D = self.B = self.V = self.N = 0
        self.cycles = 0
        self.CI = ''

    def cycle(self) -> None:
        self.cycles += 1

    # Atomic operations
    def copy_byte(self, from_register: str, to_register: str) -> None:
        setattr(self, to_register, self.__getattribute__(from_register))

    def copy_constant(self, value: int, register: str):
        setattr(self, register, value)

    # Fetch byte from address, consumes one cycle
    def fetch_byte(self, address: int) -> int:
        assert address >= 0, address < self.memory_size
        self.cycle()
        return self.memory.data[address]
    
    # Fetches byte in memory location PC, consumes one cycle, increments PC
    def fetch_byte_at_pc(self) -> int:
        byte = self.fetch_byte(self.PC)
        self.PC += 1
        return byte

    def fetch_byte_to_register(self, address: int, register: str) -> None:
        byte = self.fetch_byte(address)
        setattr(self, register, byte)
    
    # Write value to address, consumes one cycle
    def put_byte(self, address: int, value: int) -> None:
        assert 0 <= address < self.memory_size
        self.cycle()
        self.memory.data[address] = value

    def put_byte_from_register(self, address: int, register: str) -> None:
        self.put_byte(address, self.__getattribute__(register))

    # Set Z and N flags according to value in register (default: RES, i.e. result of ALU)
    def set_zero_and_negative_status_flags(self, register:str = 'RES') -> None:
        value = self.__getattribute__(register)
        self.Z = int(value == 0) 
        self.N = int(value >= 128)

    # ALU
    def alu_operation(self, operator):
        if operator == 'adc':
            if self.D:
                raise NotImplementedError
            self.RES, self.C, self.V = adc(self.OP1, self.OP2, self.C)
        elif operator == 'sbb':
            if self.D:
                raise NotImplementedError
            self.RES, self.C, self.V = sbb(self.OP1, self.OP2, 1-self.C)
        elif operator == 'cmp':
            self.Z, self.C, self.N = cmp(self.OP1, self.OP2)
        elif operator == 'shl':
            self.RES, self.C = shl(self.OP1, 0)
        elif operator == 'shr':
            self.RES, self.C = shr(self.OP1, 0)
        elif operator == 'rol':
            self.RES, self.C = shl(self.OP1, self.OP2)
        elif operator == 'ror':
            self.RES, self.C = shr(self.OP1, self.OP2)
        elif operator == 'inc':
            self.RES = inc(self.OP1, self.OP2)
        else:
            self.RES = globals()[operator](self.OP1, self.OP2)

    # Stack operations
    def add_to_stack_pointer(self, increment:int) -> None:
        self.SP = (self.SP + increment) % 0x100

    # Push byte to stack
    def push_to_stack(self, byte:int) -> None:
        assert 0 <= byte <= 0xff
        self.put_byte(0x100+self.SP, byte)

    def push_pc_to_stack(self, word:int) -> None:
        assert 0 <= word <= 0xffff
        self.put_byte(0x100+self.SP, word & 0xff)
        self.put_byte(0x100+self.SP-1, word >> 8)

    # Pull byte from stack
    def pull_from_stack(self) -> int:
        byte = self.fetch_byte(0x100+self.SP)
        return byte
    
    def pull_pc_from_stack(self) -> int:
        low_byte = self.fetch_byte(0x100+self.SP)
        high_byte = self.fetch_byte(0x100+self.SP-1)
        return low_byte + (high_byte << 8)

    # Address modes to be called by name
    def immediate(self) -> int:
        # address = self.PC
        # self.PC += 1
        value = self.fetch_byte_at_pc()
        self.CI = self.CI[:3] + f' #{value:02X}'
        return value
       
    def zero_page(self) -> int:
        address = self.fetch_byte_at_pc()
        self.CI = self.CI[:3] + f' ${address:02X}'
        return address
    
    def zero_page_indexed(self, register, penalty_cycle=False) -> int:
        self.cycle()
        address = unsigned_byte_addition(self.fetch_byte_at_pc(), self.__getattribute__(register))
        self.CI = self.CI[:3] + f' ${address:02X},{register}'
        return address
    
    def absolute(self) -> int:
        address = self.fetch_byte_at_pc()
        address += self.fetch_byte_at_pc() << 8
        self.CI = self.CI[:3] + f' ${address:04X}'
        return address
    
    def absolute_indexed(self, register, penalty_cycle=False) -> int:
        address = self.fetch_byte_at_pc()
        address += self.__getattribute__(register)
        if penalty_cycle or address > 0xff:
            self.cycle()
        address += self.fetch_byte_at_pc() << 8
        self.CI = self.CI[:3] + f' ${address:04X},{register}'
        return address       
    
    def indexed_indirect_x(self) -> int:
        index = self.fetch_byte_at_pc()
        index = unsigned_byte_addition(index, self.X)
        self.cycle()
        address = self.fetch_byte(index) + (self.fetch_byte(index+1) << 8)
        self.CI = self.CI[:3] + f' (${address:02X},X)'
        return address
    
    def indirect_indexed_y(self) -> int:
        index = self.fetch_byte_at_pc()
        address = self.fetch_byte(index)
        address += self.Y
        if address > 0xff:
            self.cycle()
        address += self.fetch_byte(index+1) << 8
        self.CI = self.CI[:3] + f' (${address:02X}),Y'
        return address
    
    def indirect(self) -> int:
        index_low = self.fetch_byte_at_pc()
        index_high = self.fetch_byte_at_pc()  
        index = (index_high<<8) + index_low
        address_low = self.fetch_byte(index)
        address_high = self.fetch_byte(index+1)
        address = (address_high<<8) + address_low 
        self.CI = self.CI[:3] + f' (${address:04X})'
        return address

    def get_address(self, mode:str, index_register: str = None, penalty_cycle= False) -> int:
        if index_register is None:
            return self.__getattribute__(mode)()
        return self.__getattribute__(mode)(index_register, penalty_cycle)   
    
    # Processor instruction by type
    # Load value from memory to register, using mode with index_register
    def load_register(self, register: str, mode: str, index_register: str=None) -> None:
        self.CI = f'LD{register} {build_address_mode_string(mode, index_register)}'
        if mode == 'immediate':
            value = self.immediate()
            setattr(self, register, value)
        else:
            address = self.get_address(mode, index_register)
            self.fetch_byte_to_register(address, register)
        self.set_zero_and_negative_status_flags(register)

    # Store value from register to memory, using mode with index_register
    def store_register(self, register: str, mode:str, index_register: str=None) -> None:
        self.CI = f'ST{register}'

        address = self.get_address(mode, index_register, penalty_cycle=True) 
        self.put_byte(address, self.__getattribute__(register))

    # Transfer value from register source to register destination
    def transfer_register(self, source: str, destination: str) -> None:
        self.CI = f'T{source}{destination}'

        setattr(self, destination, self.__getattribute__(source))
        self.cycle()
        self.set_zero_and_negative_status_flags(destination)

    # Add the content of a memory location to the accumulator together with the carry bit.
    def add_with_carry(self, mode: str, index_register:str=None) -> None:
        self.CI = f'ADC {build_address_mode_string(mode, index_register)}'
        self.copy_byte('A', 'OP1')
        if mode == 'immediate':
            value = self.immediate()
            setattr(self, 'OP2', value)
        else:
            address = self.get_address(mode, index_register)
            self.fetch_byte_to_register(address, 'OP2')
        self.alu_operation('adc')
        self.copy_byte('RES', 'A')
        self.set_zero_and_negative_status_flags()

    # Subtract the content of a memory location from the accumulator together with the inverse of the carry bit.
    def subtract_with_carry(self, mode: str, index_register:str=None) -> None:
        self.CI = f'SBC {build_address_mode_string(mode, index_register)}'
        self.copy_byte('A', 'OP1')
        if mode == 'immediate':
            value = self.immediate()
            setattr(self, 'OP2', value)
        else:
            address = self.get_address(mode, index_register)
            self.fetch_byte_to_register(address, 'OP2')
        self.alu_operation('sbb')
        self.copy_byte('RES', 'A')
        self.set_zero_and_negative_status_flags()

    # Bitwise logical operation with accumulator and memory location.
    def logical_operation(self, operator:str, mode: str, index_register:str=None) -> None:
        if operator == 'and_':
            self.CI = f'AND {build_address_mode_string(mode, index_register)}'
        if operator == 'or_':
            self.CI = f'ORA {build_address_mode_string(mode, index_register)}'
        if operator == 'xor':
            self.CI = f'EOR {build_address_mode_string(mode, index_register)}'

        self.copy_byte('A', 'OP2')
        if mode == 'immediate':
            value = self.immediate()
            setattr(self, 'OP2', value)
        else:
            address = self.get_address(mode, index_register)
            self.fetch_byte_to_register(address, 'OP1')
        self.alu_operation(operator)
        self.copy_byte('RES', 'A')
        self.set_zero_and_negative_status_flags()

    # Compare register with memory location
    def compare(self, register:str, mode: str, index_register:str=None) -> None:
        if register == 'A':
            self.CI = f'CMP {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'CP{register} {build_address_mode_string(mode, index_register)}'

        self.copy_byte(register, 'OP1')
        if mode == 'immediate':
            value = self.immediate()
            setattr(self, 'OP2', value)
        else:
            address = self.get_address(mode, index_register)
            self.fetch_byte_to_register(address, 'OP2')
        self.alu_operation('cmp')

    # Shift and rotate
    def shift_accumulator(self, left: bool = True) -> None:
        if left:
            self.CI = 'ASL'
            operator = 'shl'
        else:
            self.CI = 'LSR'
            operator = 'shr'

        self.copy_byte('A', 'OP1')
        self.copy_constant(0, 'OP2')
        self.alu_operation(operator)
        self.copy_byte('RES', 'A')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def shift_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        address = self.get_address(mode, index_register, penalty_cycle=True)
        if left:
            self.CI = f'ASL {build_address_mode_string(mode, index_register)}'
            operator = 'shl'
        else:
            self.CI = f'LSR {build_address_mode_string(mode, index_register)}'
            operator = 'shr'
        self.fetch_byte_to_register(address, 'OP1')
        self.copy_constant(0, 'OP2')
        self.alu_operation(operator)
        self.put_byte_from_register(address, 'RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def rotate_accumulator(self, left: bool = True) -> None:
        if left:
            operator = 'rol'
        else:
            operator = 'ror'

        self.CI = operator.upper()
        self.copy_byte('A', 'OP1')
        self.copy_constant(self.C, 'OP2')
        self.alu_operation(operator)
        self.copy_byte('RES', 'A')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def rotate_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        if left:
            self.CI = f'ROL {build_address_mode_string(mode, index_register)}'
            operator = 'rol'
        else:
            self.CI = f'ROR {build_address_mode_string(mode, index_register)}'
            operator = 'ror'
        address = self.get_address(mode, index_register, penalty_cycle=True)
        self.fetch_byte_to_register(address, 'OP1')
        self.copy_constant(self.C, 'OP2')
        self.alu_operation(operator)
        self.put_byte_from_register(address, 'RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def increment_register(self, increment: int, register: str) -> None:
        if increment == 1:
            self.CI = f'IN{register}'
        else:
            self.CI = f'DE{register}'

        self.copy_byte(register, 'OP1')
        self.copy_constant(increment, 'OP2')
        self.alu_operation('inc')
        self.copy_byte('RES', register)
        self.cycle()
        self.set_zero_and_negative_status_flags()

    # Increment and decrement memory
    def increment(self, increment: int, mode: str, index_register: str = None) -> None:
        if increment == 1:
            self.CI = f'INC {build_address_mode_string(mode, index_register)}'
        else:
            self.CI = f'DEC {build_address_mode_string(mode, index_register)}'

        address = self.get_address(mode, index_register, penalty_cycle=True)
        self.fetch_byte_to_register(address, 'OP1')
        self.copy_constant(increment, 'OP2')
        self.alu_operation('inc')
        self.put_byte_from_register(address, 'RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    # Branch if flag has given state
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
        if flag == 'V' and state is True:
            self.CI = 'BPL'

        # PC before start of operation
        pc = self.PC - 1
        relative_address = self.fetch_byte_at_pc()
        flag_state = self.__getattribute__(flag)
        if flag_state == state:
            self.PC = (self.PC + relative_address - 128) % 0x10000
            self.cycle()
        # See if page boundary crossed after branch
            if pc//0xff != self.PC//0xff:
                self.cycle()
                self.cycle()    
    
    # Set or clear flag
    def set_flag(self, flag: str, state: bool) -> None:
        if state is True:
            self.CI = f'SE{flag}'
        else:
            self.CI = f'CL{flag}'

        setattr(self, flag, state)
        self.cycle()

    # Increment and decrement register
    # Stack operations
    # Push processor flags to stack
    def push_processor_status(self) -> None:
        self.CI = 'PHP'

        self.push_to_stack(self.status.value)
        self.add_to_stack_pointer(-1)
        self.cycle()

    # Push register to stack
    def push_accumulator(self) -> None:
        self.CI = 'PHA'

        self.push_to_stack(self.A)
        self.add_to_stack_pointer(-1)
        self.cycle()
    
    # Pull processors from stack
    def pull_processor_status(self) -> None:
        self.CI = 'PLP'

        self.add_to_stack_pointer(1)
        self.cycle()
        self.status.set_value(self.pull_from_stack())
        self.cycle()

    # Pull program counter from stack   
    def pull_program_counter(self) -> None:
        self.add_to_stack_pointer(2)
        self.cycle()
        self.PC = self.pull_pc_from_stack()
        self.cycle()

    # Pull register from stack
    def pull_accumulator(self) -> None:
        self.CI = 'PLP'

        self.add_to_stack_pointer(1)
        self.cycle()
        self.A = self.pull_from_stack()
        self.cycle()
    
    # Jump operations
    # Jump instruction (absolute and relative)
    def jump(self, mode) -> None:
        self.CI = f'JMP {mode}'

        address = self.get_address(mode)
        self.PC = address     

    def jump_to_subroutine(self):
        self.CI = 'JSR'

        self.push_pc_to_stack(self.PC + 1)
        self.add_to_stack_pointer(-2)
        self.cycle()
        self.jump('absolute')

    def return_from_subroutine(self):
        self.CI = 'RTS'

        self.add_to_stack_pointer(2)
        self.cycle()
        self.PC = self.pull_pc_from_stack() + 1
        self.cycle()
        self.cycle()

    # Break
    def brk(self):
        self.CI = 'BRK'

        self.push_pc_to_stack(self.PC + 1)
        self.add_to_stack_pointer(-2)
        self.push_to_stack(self.status.value)
        self.add_to_stack_pointer(-1)
        self.cycle()
        self.fetch_byte_to_register(0xfffe, 'PCL')
        self.fetch_byte_to_register(0xffff, 'PCH')
        # self.PC = self.fetch_byte(0xfffe) + (self.fetch_byte(0xffff) << 8)
        self.B = 1

    def return_from_interrupt(self):
        self.CI = 'RTI'

        self.pull_processor_status()
        self.add_to_stack_pointer(2)           
        self.PC = self.pull_pc_from_stack()

    def no_operation(self):
        pass

    def fetch_instruction(self) -> int:
        return self.fetch_byte_at_pc()

    # Run instruction at PC
    def run_instruction(self) -> None:
        op_code = self.fetch_instruction()
        self.decode(op_code)

    def decode(self, op_code: int) -> None:
        # ADC: Add with Carry
        if op_code == ADC_IMMEDIATE:
            self.add_with_carry('immediate')
        elif op_code == ADC_ZERO_PAGE:
            self.add_with_carry('zero_page')
        elif op_code == ADC_ZERO_PAGE_X:
            self.add_with_carry('zero_page_indexed', 'X')
        elif op_code == ADC_ABSOLUTE:
            self.add_with_carry('absolute')            
        elif op_code == ADC_ABSOLUTE_X:
            self.add_with_carry('absolute_indexed', 'X')             
        elif op_code == ADC_ABSOLUTE_Y:
            self.add_with_carry('absolute_indexed', 'Y')      
        elif op_code == ADC_INDIRECT_X:
            self.add_with_carry('indexed_indirect_x')                       
        elif op_code == ADC_INDIRECT_Y:
            self.add_with_carry('indirect_indexed_y')
        # AND instructions
        elif op_code == AND_IMMEDIATE:
            self.logical_operation('and_', 'immediate')
        elif op_code == AND_ZERO_PAGE:
            self.logical_operation('and_', 'zero_page')
        elif op_code == AND_ZERO_PAGE_X:
            self.logical_operation('and_', 'zero_page_indexed', 'X')
        elif op_code == AND_ABSOLUTE:
            self.logical_operation('and_', 'absolute')
        elif op_code == AND_ABSOLUTE_X:
            self.logical_operation('and_', 'absolute_indexed', 'X')
        elif op_code == AND_ABSOLUTE_Y:
            self.logical_operation('and_', 'absolute_indexed', 'Y')
        elif op_code == AND_INDIRECT_X:
            self.logical_operation('and_', 'indexed_indirect_x')
        elif op_code == AND_INDIRECT_Y:
            self.logical_operation('and_', 'indirect_indexed_y')
        # Arithmetic shift left
        elif op_code == ASL_ACCUMULATOR:
            self.shift_accumulator(left=True)
        elif op_code == ASL_ZERO_PAGE:
            self.shift_memory(left=True, mode='zero_page')
        elif op_code == ASL_ZERO_PAGE_X:
            self.shift_memory(left=True, mode='zero_page_indexed', index_register='X')
        elif op_code == ASL_ABSOLUTE:
            self.shift_memory(left=True, mode='absolute')
        elif op_code == ASL_ABSOLUTE_X:
            self.shift_memory(left=True, mode='absolute_indexed', index_register='X')       
        # Branch instructions
        elif op_code == BCC_RELATIVE:
            self.branch('C', False)
        elif op_code == BCS_RELATIVE:
            self.branch('C', True)
        elif op_code == BEQ_RELATIVE:
            self.branch('Z', True)
        elif op_code == BMI_RELATIVE:
            self.branch('N', True)
        elif op_code == BNE_RELATIVE:
            self.branch('Z', False)
        elif op_code == BPL_RELATIVE:
            self.branch('N', False)
        elif op_code == BVC:
            self.branch('V', False)
        elif op_code == BVS:
            self.branch('V', True)    
        # Break
        elif op_code == BRK:
            self.brk()
        # Clear flag instructions
        elif op_code == CLC:
            self.set_flag('C', False)
        elif op_code == CLD:
            self.set_flag('D', False)
        elif op_code == CLI:
            self.set_flag('I', False)
        elif op_code == CLV:
            self.set_flag('V', False)
        # Compare instructions
        elif op_code == CMP_IMMEDIATE:
            self.compare('A', 'immediate')
        elif op_code == CMP_ZERO_PAGE:
            self.compare('A', 'zero_page')
        elif op_code == CMP_ZERO_PAGE_X:
            self.compare('A', 'zero_page_indexed', 'X')
        elif op_code == CMP_ABSOLUTE:
            self.compare('A', 'absolute')
        elif op_code == CMP_ABSOLUTE_X:
            self.compare('A', 'absolute_indexed', 'X')
        elif op_code == CMP_ABSOLUTE_Y:
            self.compare('A', 'absolute_indexed', 'Y')
        elif op_code == CMP_INDIRECT_X:
            self.compare('A', 'indexed_indirect_x')
        elif op_code == CMP_INDIRECT_Y:
            self.compare('A', 'indirect_indexed_y')
        elif op_code == CPX_IMMEDIATE:
            self.compare('X', 'immediate')
        elif op_code == CPX_ZERO_PAGE:
            self.compare('X', 'zero_page')
        elif op_code == CPX_ABSOLUTE:
            self.compare('X', 'absolute')
        elif op_code == CPY_IMMEDIATE:
            self.compare('Y', 'immediate')
        elif op_code == CPY_ZERO_PAGE:
            self.compare('Y', 'zero_page')
        elif op_code == CPY_ABSOLUTE:
            self.compare('Y', 'absolute')
        # DEC instructions
        elif op_code == DEC_ZERO_PAGE:
            self.increment(-1, 'zero_page')
        elif op_code == DEC_ZERO_PAGE_X:
            self.increment(-1, 'zero_page_indexed', 'X')
        elif op_code == DEC_ABSOLUTE:
            self.increment(-1, 'absolute')
        elif op_code == DEC_ABSOLUTE_X:
            self.increment(-1, 'absolute_indexed', 'X')
        # Decrement registers X and Y
        elif op_code == DEX:
            self.increment_register(-1, 'X')
        elif op_code == DEY:
            self.increment_register(-1, 'Y')            
        # EOR instructions
        elif op_code == EOR_IMMEDIATE:
            self.logical_operation('xor', 'immediate')
        elif op_code == EOR_ZERO_PAGE:
            self.logical_operation('xor', 'zero_page')
        elif op_code == EOR_ZERO_PAGE_X:
            self.logical_operation('xor', 'zero_page_indexed', 'X')
        elif op_code == EOR_ABSOLUTE:
            self.logical_operation('xor', 'absolute')
        elif op_code == EOR_ABSOLUTE_X:
            self.logical_operation('xor', 'absolute_indexed', 'X')
        elif op_code == EOR_ABSOLUTE_Y:
            self.logical_operation('xor', 'absolute_indexed', 'Y')
        elif op_code == EOR_INDIRECT_X:
            self.logical_operation('xor', 'indexed_indirect_x')
        elif op_code == EOR_INDIRECT_Y:
            self.logical_operation('xor', 'indirect_indexed_y')
        # INC instructions
        elif op_code == INC_ZERO_PAGE:
            self.increment(1, 'zero_page')
        elif op_code == INC_ZERO_PAGE_X:
            self.increment(1, 'zero_page_indexed', 'X')
        elif op_code == INC_ABSOLUTE:
            self.increment(1, 'absolute')
        elif op_code == INC_ABSOLUTE_X:
            self.increment(1, 'absolute_indexed', 'X')
        # Decrement registers X and Y
        elif op_code == INX:
            self.increment_register(1, 'X')
        elif op_code == INY:
            self.increment_register(1, 'Y')
        # JMP instructions
        elif op_code == JMP_ABSOLUTE:
            self.jump('absolute')
        elif op_code == JMP_INDIRECT:
            self.jump('indirect')
        # JSR instruction
        elif op_code == JSR:
            self.jump_to_subroutine()            
        # LDA instructions
        elif op_code == LDA_IMMEDIATE:
            self.load_register('A', 'immediate')
        elif op_code == LDA_ZERO_PAGE:
            self.load_register('A', 'zero_page')
        elif op_code == LDA_ZERO_PAGE_X:
            self.load_register('A', 'zero_page_indexed', 'X')
        elif op_code == LDA_ABSOLUTE:
            self.load_register('A', 'absolute')
        elif op_code == LDA_ABSOLUTE_X:
            self.load_register('A', 'absolute_indexed', 'X')
        elif op_code == LDA_ABSOLUTE_Y:
            self.load_register('A', 'absolute_indexed', 'Y')
        elif op_code == LDA_INDIRECT_X:
            self.load_register('A', 'indexed_indirect_x')        
        elif op_code == LDA_INDIRECT_Y:
            self.load_register('A', 'indirect_indexed_y')        
        # LDX instructions
        elif op_code == LDX_IMMEDIATE:
            self.load_register('X', 'immediate')
        elif op_code == LDX_ZERO_PAGE:
            self.load_register('X', 'zero_page')
        elif op_code == LDX_ZERO_PAGE_Y:
            self.load_register('X', 'zero_page_indexed', 'Y')
        elif op_code == LDX_ABSOLUTE:
            self.load_register('X', 'absolute')
        elif op_code == LDX_ABSOLUTE_Y:
            self.load_register('X', 'absolute_indexed', 'Y')
        # LDY instructions
        elif op_code == LDY_IMMEDIATE:
            self.load_register('Y', 'immediate')
        elif op_code == LDY_ZERO_PAGE:
            self.load_register('Y', 'zero_page')
        elif op_code == LDY_ZERO_PAGE_X:
            self.load_register('Y', 'zero_page_indexed', 'X')
        elif op_code == LDY_ABSOLUTE:
            self.load_register('Y', 'absolute')
        elif op_code == LDX_ABSOLUTE_Y:
            self.load_register('Y', 'absolute_indexed', 'X')
        # Logical shift right
        elif op_code == LSR_ACCUMULATOR:
            self.shift_accumulator(left=False)
        elif op_code == LSR_ZERO_PAGE:
            self.shift_memory(left=False, mode='zero_page')
        elif op_code == LSR_ZERO_PAGE_X:
            self.shift_memory(left=False, mode='zero_page_indexed', index_register='X')
        elif op_code == LSR_ABSOLUTE:
            self.shift_memory(left=False, mode='absolute')
        elif op_code == LSR_ABSOLUTE_X:
            self.shift_memory(left=False, mode='absolute_indexed', index_register='X')       
        # NOP instruction
        elif op_code == NOP:
            self.no_operation()
        # ORA instructions
        elif op_code == ORA_IMMEDIATE:
            self.logical_operation('or_', 'immediate')
        elif op_code == ORA_ZERO_PAGE:
            self.logical_operation('or_', 'zero_page')
        elif op_code == ORA_ZERO_PAGE_X:
            self.logical_operation('or_', 'zero_page_indexed', 'X')
        elif op_code == ORA_ABSOLUTE:
            self.logical_operation('or_', 'absolute')
        elif op_code == ORA_ABSOLUTE_X:
            self.logical_operation('or_', 'absolute_indexed', 'X')
        elif op_code == ORA_ABSOLUTE_Y:
            self.logical_operation('or_', 'absolute_indexed', 'Y')
        elif op_code == ORA_INDIRECT_X:
            self.logical_operation('or_', 'indexed_indirect_x')
        elif op_code == ORA_INDIRECT_Y:
            self.logical_operation('or_', 'indirect_indexed_y')
        # Push to stack instructions
        elif op_code == PHA:
            self.push_accumulator()
        elif op_code == PHP:
            self.push_processor_status()
        # Pull from stack instruction
        elif op_code == PLA:
            self.pull_accumulator()
        elif op_code == PLP:
            self.pull_processor_status()
        # Rotate instructions
        elif op_code == ROL_ACCUMULATOR:
            self.rotate_accumulator(left=True)
        elif op_code == ROL_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=True)
        elif op_code == ROL_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_indexed', index_register='X', left=True)
        elif op_code == ROL_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=True)
        elif op_code == ROL_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_indexed', index_register='X', left=True)
        elif op_code == ROR_ACCUMULATOR:
            self.rotate_accumulator(left=False)
        elif op_code == ROR_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=False)
        elif op_code == ROR_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_indexed', index_register='X', left=False)
        elif op_code == ROR_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=False)
        elif op_code == ROR_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_indexed', index_register='X', left=False)
        # RTI instruction
        elif op_code == RTI:
            self.return_from_interrupt()
        # RTS instruction
        elif op_code == RTS:
            self.return_from_subroutine()
        # SBC instructions
        elif op_code == SBC_IMMEDIATE:
            self.subtract_with_carry('immediate')
        elif op_code == SBC_ZERO_PAGE:
            self.subtract_with_carry('zero_page')            
        elif op_code == SBC_ZERO_PAGE_X:
            self.subtract_with_carry('zero_page_indexed', 'X')
        elif op_code == SBC_ABSOLUTE:
            self.subtract_with_carry('absolute')            
        elif op_code == SBC_ABSOLUTE_X:
            self.subtract_with_carry('absolute_indexed', 'X')             
        elif op_code == SBC_ABSOLUTE_Y:
            self.subtract_with_carry('absolute_indexed', 'Y')      
        elif op_code == SBC_INDIRECT_X:
            self.subtract_with_carry('indexed_indirect_x')                       
        elif op_code == SBC_INDIRECT_Y:
            self.subtract_with_carry('indirect_indexed_y')
        # Set flag instructions
        elif op_code == SEC:
            self.set_flag('C', True)
        elif op_code == SED:
            self.set_flag('D', True)
        elif op_code == SEI:
            self.set_flag('I', True)
        # STA instructions
        elif op_code == STA_ZERO_PAGE:
            self.store_register('A', 'zero_page')
        elif op_code == STA_ZERO_PAGE_X:
            self.store_register('A', 'zero_page_indexed', 'X')
        elif op_code == STA_ABSOLUTE:
            self.store_register('A', 'absolute')
        elif op_code == STA_ABSOLUTE_X:
            self.store_register('A', 'absolute_indexed', 'X')
        elif op_code == STA_ABSOLUTE_Y:
            self.store_register('A', 'absolute_indexed', 'Y')
        elif op_code == STA_INDIRECT_X:
            self.store_register('A', 'indexed_indirect_x')
        elif op_code == STA_INDIRECT_Y:
            self.store_register('A', 'indirect_indexed_y')
        # STX instructions
        elif op_code == STX_ZERO_PAGE:
            self.store_register('X', 'zero_page')
        elif op_code == STX_ZERO_PAGE_Y:
            self.store_register('X', 'zero_page_indexed', 'Y')
        elif op_code == STX_ABSOLUTE:
            self.store_register('X', 'absolute')
        # STY instructions
        elif op_code == STY_ZERO_PAGE:
            self.store_register('Y', 'zero_page')
        elif op_code == STY_ZERO_PAGE_X:
            self.store_register('Y', 'zero_page_indexed', 'X')
        elif op_code == STY_ABSOLUTE:
            self.store_register('Y', 'absolute')
        # Transfer register to register instructions
        elif op_code == TAX:
            self.transfer_register('A', 'X')
        elif op_code == TAY:
            self.transfer_register('A', 'Y')
        elif op_code == TSX:
            self.transfer_register('S', 'X')
        elif op_code == TXA:
            self.transfer_register('X', 'A')
        elif op_code == TXS:
            self.transfer_register('X', 'S')
        elif op_code == TYA:
            self.transfer_register('Y', 'A')        
        else:
            raise Exception()


def setup_processor(instruction:list[int], data:dict=None, registers:dict=None, flags:dict=None) -> Processor:
    processor = Processor()

    if data:
        for a, v in data.items():
            processor.memory.data[a] = v

    if registers:
        for r, v in registers.items():
            processor.__setattr__(r, v)

    if flags:
        for f, v in flags.items():
            processor.__setattr__(f, v)

    address = processor.PC
    
    for byte in instruction:
        processor.memory.data[address] = byte
        address += 1
   
    return processor


if __name__ == '__main__':
    processor = Processor()
    processor.reset()
    
