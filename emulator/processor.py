#     6502Simulator, a didactic visual simulator of the 6502 processor
#     Copyright (C) 2024  Tobias Bäumlin
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


import array as ar
from operator import inv, or_, xor, and_  # noqa
from emulator.opcodes import *
from emulator.operators import unsigned_byte_addition, shl, shr, set_bit, cmp, sbb, adc, inc, bcd_addition_with_carry, bcd_subtraction_with_borrow


class UndefinedInstructionError(Exception):
    def __init__(self, instruction):
        super().__init__(f'UNDEF ${instruction:02x}')


class Memory:
    def __init__(self, size: int) -> None:
        assert size > 2 ** 12, size <= 2 ** 16
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
    def __init__(self, memory_size=2 ** 16) -> None:
        self.memory_size = memory_size
        self.memory = Memory(memory_size)
        # Two byte registers containing memory addresses
        # Program counter
        self.program_counter_high = Register()        # Program counter high byte
        self.program_counter_low = Register()         # Program counter low byte
        # Virtual address register holding address for next operand
        self.address_register_high = Register()
        self.address_register_low = Register()
        # Registers
        # Stack pointer; stack is top down, starts at 0x01ff
        self.stack_pointer = Register(init=0xff)
        self.accumulator = Register()
        self.index_x = Register()
        self.index_y = Register()
        self.status = Register()
        # ALU with two virtual registers holding the operands and one holding the result
        self.alu_op_1 = Register()
        self.alu_op_2 = Register()
        self.alu_res = Register()
        # Virtual instruction register
        self.instruction_register = Register()
        # Cycle counter
        self.cycles = 0
        self.byte_format = '02X'
        self.word_format = '04X'
        self.format_prefix = '$'
        # Interrupt and reset vector addresses
        self.interrupt_vector_address = 0xfffe
        self.reset_vector_address = 0xfffc
        self.nmi_vector_address = 0xfffa
        #
        self.interrupt_requested = False
        self.non_maskable_interrupt_requested = False

    @property
    def PC(self):  # noqa
        return (self.program_counter_high.value << 8) + self.program_counter_low.value

    @PC.setter
    def PC(self, value):
        assert 0 <= value < 0x10000
        self.program_counter_high.set_value(value >> 8)
        self.program_counter_low.set_value(value & 0xff)

    @property
    def PCH(self):
        return self.program_counter_high.value

    @PCH.setter
    def PCH(self, value):
        self.program_counter_high.set_value(value)

    @property
    def PCL(self):
        return self.program_counter_low.value

    @PCL.setter
    def PCL(self, value):
        self.program_counter_low.set_value(value)

    @property
    def AR(self):  # noqa
        return (self.address_register_high.value << 8) + self.address_register_low.value

    @AR.setter
    def AR(self, value):
        assert 0 <= value < 0x10000
        self.ARH = (value >> 8)
        self.ARL = (value & 0xff)

    @property
    def ARH(self):
        return self.address_register_high.value

    @ARH.setter
    def ARH(self, value):
        self.address_register_high.set_value(value)

    @property
    def ARL(self):
        return self.address_register_low.value

    @ARL.setter
    def ARL(self, value):
        self.address_register_low.set_value(value)

    @property
    def IR(self):
        return self.instruction_register.value

    @IR.setter
    def IR(self, value):
        self.instruction_register.set_value(value)

    @property
    def S(self):
        return self.stack_pointer.value

    @S.setter
    def S(self, value):
        self.stack_pointer.set_value(value)

    @property
    def A(self):
        return self.accumulator.value

    @A.setter
    def A(self, value):
        self.accumulator.set_value(value)

    @property
    def X(self):
        return self.index_x.value

    @X.setter
    def X(self, value):
        self.index_x.set_value(value)

    @property
    def Y(self):
        return self.index_y.value

    @Y.setter
    def Y(self, value):
        self.index_y.set_value(value)

    @property
    def SR(self):
        return self.status.value

    @SR.setter
    def SR(self, value):
        self.C = value & 1
        self.Z = (value >> 1) & 1
        self.I = (value >> 2) & 1
        self.D = (value >> 3) & 1
        self.B = (value >> 4) & 1
        self.V = (value >> 6) & 1
        self.N = (value >> 7) & 1

    @property
    def C(self):
        return self.status.value & 1

    @C.setter
    def C(self, value):
        self.status.value = set_bit(self.status.value, 0, value)

    @property
    def Z(self):
        return (self.status.value >> 1) & 1

    @Z.setter
    def Z(self, value):
        self.status.value = set_bit(self.status.value, 1, value)

    @property
    def I(self): # noqa e741
        return (self.status.value >> 2) & 1

    @I.setter
    def I(self, value): # noqa 8
        self.status.value = set_bit(self.status.value, 2, value)

    @property
    def D(self):
        return (self.status.value >> 3) & 1

    @D.setter
    def D(self, value):
        self.status.value = set_bit(self.status.value, 3, value)

    @property
    def B(self):
        return (self.status.value >> 4) & 1

    @B.setter
    def B(self, value):
        self.status.value = set_bit(self.status.value, 4, value)

    @property
    def V(self):
        return (self.status.value >> 6) & 1

    @V.setter
    def V(self, value):
        self.status.value = set_bit(self.status.value, 6, value)

    @property
    def N(self):
        return (self.status.value >> 7) & 1

    @N.setter
    def N(self, value):
        self.status.value = set_bit(self.status.value, 7, value)

    @property
    def OP1(self):
        return self.alu_op_1.value

    @OP1.setter
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

    def word(self, address: int) -> int:
        return self.memory.data[address] + (self.memory.data[address + 1] << 8)

    def reset(self) -> None:
        self.PC = self.word(self.reset_vector_address)
        self.S = 0xff
        self.A = self.X = self.Y = 0
        self.C = self.Z = self.I = self.D = self.B = self.V = self.N = 0
        self.OP1 = self.OP2 = self.RES = 0
        self.AR = 0
        self.cycles = 0

    def clear_memory(self) -> None:
        self.memory.initialise()

    def cycle(self) -> None:
        self.cycles += 1

    # Atomic operations
    def copy_byte(self, from_register: str, to_register: str) -> None:
        setattr(self, to_register, getattr(self, from_register))

    def copy_constant(self, value: int, register: str):
        setattr(self, register, value)

    # Fetch byte from address register, consumes one cycle
    def fetch_byte(self) -> int:
        self.cycle()
        return self.memory.data[self.AR]

    def fetch_byte_to_register(self, register: str) -> None:
        byte = self.fetch_byte()
        setattr(self, register, byte)

    # Fetches byte in memory location PC, consumes one cycle, increments PC
    def fetch_byte_at_pc(self) -> int:
        self.cycle()
        byte = self.memory.data[self.PC]
        self.PC += 1
        return byte

    def fetch_byte_at_pc_to_register(self, register: str) -> None:
        byte = self.fetch_byte_at_pc()
        setattr(self, register, byte)

    # Write value to address, consumes one cycle
    def put_byte(self, byte: int) -> None:
        self.cycle()
        self.memory.data[self.AR] = byte

    def put_byte_from_register(self, register: str) -> None:
        self.put_byte(self.__getattribute__(register))

    # Set Z and N flags according to value in register (default: RES, i.e. result of ALU)
    def set_zero_and_negative_status_flags(self, register: str = 'RES') -> None:
        value = self.__getattribute__(register)
        self.Z = int(value == 0)
        self.N = int(value >= 128)

    # ALU
    def alu_operation(self, operator):
        if operator == 'adc':
            if self.D:
                self.RES, self.C = bcd_addition_with_carry(self.OP1, self.OP2, self.C)
            self.RES, self.C, self.V = adc(self.OP1, self.OP2, self.C)
        elif operator == 'sbc':
            if self.D:
                print(self.OP1, self.OP2, self.C)
                self.RES, self.C = bcd_subtraction_with_borrow(self.OP1, self.OP2, 1-self.C)
            self.RES, self.C, self.V = sbb(self.OP1, self.OP2, 1 - self.C)
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
            self.RES = inc(self.OP1, 1)
        elif operator == 'dec':
            self.RES = inc(self.OP1, -1)
        else:
            self.RES = globals()[operator](self.OP1, self.OP2)

    # Stack operations
    def add_to_stack_pointer(self, increment: int) -> None:
        self.copy_byte('S', 'OP1')
        if increment == 1:
            self.alu_operation('inc')
        elif increment == -1:
            self.alu_operation('dec')
        self.copy_byte('RES', 'S')
        # self.S = (self.S + increment) % 0x100
        # self.cycle()

    def set_address_register_from_stack_pointer(self) -> None:
        self.AR = 0x100 + self.S

    # Push register to stack
    def push_register(self, register: str) -> None:
        self.set_address_register_from_stack_pointer()
        self.put_byte_from_register(register)
        self.add_to_stack_pointer(-1)

    def pull_register(self, register: str) -> None:
        self.add_to_stack_pointer(1)
        self.set_address_register_from_stack_pointer()
        self.fetch_byte_to_register(register)

    # Address modes to be called by name
    def immediate(self):
        self.copy_byte('PC', 'AR')
        self.PC += 1

    def zero_page(self):
        self.fetch_byte_at_pc_to_register('AR')

    def zero_page_indexed(self, register, penalty_cycle=False):  # noqa
        self.cycle()
        self.fetch_byte_at_pc_to_register('AR')
        self.AR = unsigned_byte_addition(self.AR, self.__getattribute__(register))

    def absolute(self):
        self.fetch_byte_at_pc_to_register('ARL')
        self.fetch_byte_at_pc_to_register('ARH')

    def absolute_indexed(self, register, penalty_cycle=False) -> None:
        self.fetch_byte_at_pc_to_register('ARL')
        address = self.ARL + self.__getattribute__(register)
        self.ARL = address % 0x100
        if penalty_cycle or address > 0xff:
            self.cycle()
        self.fetch_byte_at_pc_to_register('ARH')
        self.ARH = (self.ARH + address // 0x100) % 0x10000

    def indexed_indirect_x(self) -> None:
        self.fetch_byte_at_pc_to_register('AR')
        index = (self.AR + self.X) % 0x100
        self.cycle()
        self.AR = index
        self.fetch_byte_to_register('AR')
        low_byte = self.AR
        self.AR = index+1
        self.fetch_byte_to_register('AR')
        self.AR = (self.AR << 8) + low_byte

    def indirect_indexed_y(self) -> None:
        self.fetch_byte_at_pc_to_register('AR')
        index = self.AR
        self.fetch_byte_to_register('AR')
        low_byte = self.AR
        self.AR = index + 1
        self.fetch_byte_to_register('AR')
        self.AR = ((self.AR << 8) + low_byte + self.Y) % 0x10000
        if (low_byte+self.Y) > 0xff:
            self.cycle()

    def indirect(self) -> None:
        self.fetch_byte_at_pc_to_register('ARL')
        self.fetch_byte_at_pc_to_register('ARH')
        index = (self.ARH << 8) + self.ARL
        self.fetch_byte_to_register('AR')
        low_byte = self.AR
        self.AR = (index + 1) % 0x10000
        self.fetch_byte_to_register('AR')
        self.AR = (self.AR << 8) + low_byte

    def relative(self) -> None:
        self.copy_byte('PCL', 'OP2')
        # Save flags c and v and prepare for addition
        c, v = self.C, self.V
        self.C = self.V = 0
        self.alu_operation('adc')
        self.copy_byte('RES', 'PCL')
        self.cycle()
        if self.C and self.OP2 < 0x80:
            self.PCH += 1
            self.cycle()
        if not self.C and self.OP2 >= 0x80:
            self.PCH -= 1
            self.cycle()
        self.C, self.V = c, v

    def get_address(self, mode: str, index_register: str = None, penalty_cycle=False) -> None:
        if index_register is None:
            getattr(self, mode)()
        else:
            getattr(self, mode)(index_register, penalty_cycle)

    # Processor instruction by type
    # Load value from memory to register, using mode with index_register
    def load_register(self, register: str, mode: str, index_register: str = None) -> None:
        self.get_address(mode, index_register)
        self.fetch_byte_to_register(register)
        self.set_zero_and_negative_status_flags(register)

    # Store value from register to memory, using mode with index_register
    def store_register(self, register: str, mode: str, index_register: str = None) -> None:
        self.get_address(mode, index_register, penalty_cycle=True)
        self.put_byte_from_register(register)

    # Transfer value from register source to register destination
    def transfer_register(self, source: str, destination: str) -> None:
        self.copy_byte(source, destination)
        self.cycle()
        self.set_zero_and_negative_status_flags(destination)

    # Bitwise arithmetic or logical operation with accumulator and memory location:
    # ADC, SBC, AND, EOR, XOR
    def arithmetic_operation(self, operator: str, mode: str, index_register: str = None) -> None:
        self.copy_byte('A', 'OP1')
        self.get_address(mode, index_register)
        self.fetch_byte_to_register('OP2')
        self.alu_operation(operator)
        self.copy_byte('RES', 'A')
        self.set_zero_and_negative_status_flags()

    # Compare register with memory location
    def compare(self, register: str, mode: str, index_register: str = None) -> None:
        self.copy_byte(register, 'OP1')
        self.get_address(mode, index_register)
        self.fetch_byte_to_register('OP2')
        self.alu_operation('cmp')

    def bit_test(self, mode: str, index_register: str=None) -> None:  # noqa
        self.copy_byte('A', 'OP1')
        self.get_address(mode, index_register)
        self.fetch_byte_to_register('OP2')
        self.alu_operation('and_')
        self.N = (self.OP2 & 0b10000000) >> 7
        self.V = (self.OP2 & 0b01000000) >> 6
        self.Z = int(self.RES == 0)

    # Shift and rotate
    def shift_accumulator(self, left: bool = True) -> None:
        self.copy_byte('A', 'OP1')
        self.copy_constant(0, 'OP2')
        self.alu_operation('shl' if left else 'shr')
        self.copy_byte('RES', 'A')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def shift_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        self.get_address(mode, index_register, penalty_cycle=True)
        self.fetch_byte_to_register('OP1')
        self.copy_constant(0, 'OP2')
        self.alu_operation('shl' if left else 'shr')
        self.put_byte_from_register('RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def rotate_accumulator(self, left: bool = True) -> None:
        self.copy_byte('A', 'OP1')
        self.copy_byte('C', 'OP2')
        self.alu_operation('rol' if left else 'ror')
        self.copy_byte('RES', 'A')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def rotate_memory(self, mode: str, index_register=None, left: bool = True) -> None:
        self.get_address(mode, index_register, penalty_cycle=True)
        self.fetch_byte_to_register('OP1')
        self.copy_byte('C', 'OP2')
        self.alu_operation('rol' if left else 'ror')
        self.put_byte_from_register('RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    def increment_register(self, increment: int, register: str) -> None:
        self.copy_byte(register, 'OP1')
        if increment == 1:
            self.alu_operation('inc')
        elif increment == -1:
            self.alu_operation('dec')
        self.copy_byte('RES', register)
        self.cycle()
        self.set_zero_and_negative_status_flags()

    # Increment and decrement memory
    def increment(self, increment: int, mode: str, index_register: str = None) -> None:
        self.get_address(mode, index_register, penalty_cycle=True)
        self.fetch_byte_to_register('OP1')
        if increment == 1:
            self.alu_operation('inc')
        elif increment == -1:
            self.alu_operation('dec')
        self.put_byte_from_register('RES')
        self.cycle()
        self.set_zero_and_negative_status_flags()

    # Branch if flag has given state
    def branch(self, flag: str, state: bool) -> None:
        self.fetch_byte_at_pc_to_register('OP1')
        if getattr(self, flag) == state:
            self.get_address('relative')

    # Set or clear flag
    def set_flag(self, flag: str, state: bool) -> None:
        setattr(self, flag, state)
        self.cycle()

    # Stack operations
    # Push register to stack

    def push_register_to_stack(self, register: str) -> None:
        self.push_register(register)
        self.cycle()

    def pull_register_from_stack(self, register: str) -> None:
        self.pull_register(register)
        self.cycle()
        self.cycle()

    # Jump operations
    # Jump instruction (absolute and relative)
    def jump(self, mode) -> None:
        self.get_address(mode)
        self.PC = self.AR

    def jump_to_subroutine(self):
        self.PC += 1
        self.push_register('PCH')
        self.push_register('PCL')
        self.PC -= 1
        self.cycle()
        self.jump('absolute')

    def return_from_subroutine(self):
        self.pull_register('PCL')
        self.cycle()
        self.pull_register('PCH')
        self.cycle()
        self.PC += 1
        self.cycle()

    # Break
    def brk(self):
        # Break instruction has one extra cycle (actually reading the following byte and ignoring it)
        self.cycle()
        self.PC = self.PC + 1
        self.push_register('PCH')
        self.push_register('PCL')
        self.B = 1
        self.push_register('SR')
        self.AR = self.interrupt_vector_address
        self.fetch_byte_to_register('PCL')
        self.AR = self.interrupt_vector_address + 1
        self.fetch_byte_to_register('PCH')

    def return_from_interrupt(self):
        self.pull_register('SR')
        self.pull_register('PCL')
        self.pull_register('PCH')
        self.B = 0
        self.cycle()
        self.cycle()

    def no_operation(self):
        pass

    def interrupt(self):
        if self.I:
            return
        self.push_register('PCH')
        self.push_register('PCL')
        self.push_register('SR')
        self.AR = self.interrupt_vector_address
        self.fetch_byte_to_register('PCL')
        self.AR = self.interrupt_vector_address + 1
        self.fetch_byte_to_register('PCH')

    def non_maskable_interrupt(self):
        self.push_register('PCH')
        self.push_register('PCL')
        self.push_register('SR')
        self.AR = self.nmi_vector_address
        self.fetch_byte_to_register('PCL')
        self.AR = self.nmi_vector_address + 1
        self.fetch_byte_to_register('PCH')

    def fetch_instruction(self) -> None:
        self.fetch_byte_at_pc_to_register('IR')

    # Run instruction at PC
    def run_instruction(self) -> None:
        if self.interrupt_requested and not self.I:
            self.interrupt()
        if self.non_maskable_interrupt_requested:
            self.non_maskable_interrupt()
        self.interrupt_requested = False
        self.non_maskable_interrupt_requested = False
        self.fetch_instruction()
        self.decode_instruction()

    def decode_instruction(self) -> None:
        # ADC: Add with Carry
        if self.IR == ADC_IMMEDIATE:
            self.arithmetic_operation('adc', 'immediate')
        elif self.IR == ADC_ZERO_PAGE:
            self.arithmetic_operation('adc', 'zero_page')
        elif self.IR == ADC_ZERO_PAGE_X:
            self.arithmetic_operation('adc', 'zero_page_indexed', 'X')
        elif self.IR == ADC_ABSOLUTE:
            self.arithmetic_operation('adc', 'absolute')
        elif self.IR == ADC_ABSOLUTE_X:
            self.arithmetic_operation('adc', 'absolute_indexed', 'X')
        elif self.IR == ADC_ABSOLUTE_Y:
            self.arithmetic_operation('adc', 'absolute_indexed', 'Y')
        elif self.IR == ADC_INDIRECT_X:
            self.arithmetic_operation('adc', 'indexed_indirect_x')
        elif self.IR == ADC_INDIRECT_Y:
            self.arithmetic_operation('adc', 'indirect_indexed_y')
        # AND instructions
        elif self.IR == AND_IMMEDIATE:
            self.arithmetic_operation('and_', 'immediate')
        elif self.IR == AND_ZERO_PAGE:
            self.arithmetic_operation('and_', 'zero_page')
        elif self.IR == AND_ZERO_PAGE_X:
            self.arithmetic_operation('and_', 'zero_page_indexed', 'X')
        elif self.IR == AND_ABSOLUTE:
            self.arithmetic_operation('and_', 'absolute')
        elif self.IR == AND_ABSOLUTE_X:
            self.arithmetic_operation('and_', 'absolute_indexed', 'X')
        elif self.IR == AND_ABSOLUTE_Y:
            self.arithmetic_operation('and_', 'absolute_indexed', 'Y')
        elif self.IR == AND_INDIRECT_X:
            self.arithmetic_operation('and_', 'indexed_indirect_x')
        elif self.IR == AND_INDIRECT_Y:
            self.arithmetic_operation('and_', 'indirect_indexed_y')
        # Arithmetic shift left
        elif self.IR == ASL_ACCUMULATOR:
            self.shift_accumulator(left=True)
        elif self.IR == ASL_ZERO_PAGE:
            self.shift_memory(left=True, mode='zero_page')
        elif self.IR == ASL_ZERO_PAGE_X:
            self.shift_memory(left=True, mode='zero_page_indexed', index_register='X')
        elif self.IR == ASL_ABSOLUTE:
            self.shift_memory(left=True, mode='absolute')
        elif self.IR == ASL_ABSOLUTE_X:
            self.shift_memory(left=True, mode='absolute_indexed', index_register='X')
        # Branch instructions
        elif self.IR == BCC:
            self.branch('C', False)
        elif self.IR == BCS:
            self.branch('C', True)
        elif self.IR == BEQ:
            self.branch('Z', True)
        elif self.IR == BMI:
            self.branch('N', True)
        elif self.IR == BNE:
            self.branch('Z', False)
        elif self.IR == BPL:
            self.branch('N', False)
        elif self.IR == BVC:
            self.branch('V', False)
        elif self.IR == BVS:
            self.branch('V', True)
        elif self.IR == BIT_ZERO_PAGE:
            self.bit_test(mode='zero_page')
        elif self.IR == BIT_ABSOLUTE:
            self.bit_test(mode='absolute')
        # Break
        elif self.IR == BRK:
            self.brk()
        # Clear flag instructions
        elif self.IR == CLC:
            self.set_flag(flag='C', state=False)
        elif self.IR == CLD:
            self.set_flag(flag='D', state=False)
        elif self.IR == CLI:
            self.set_flag(flag='I', state=False)
        elif self.IR == CLV:
            self.set_flag(flag='V', state=False)
        # Compare instructions
        elif self.IR == CMP_IMMEDIATE:
            self.compare('A', 'immediate')
        elif self.IR == CMP_ZERO_PAGE:
            self.compare('A', 'zero_page')
        elif self.IR == CMP_ZERO_PAGE_X:
            self.compare('A', 'zero_page_indexed', 'X')
        elif self.IR == CMP_ABSOLUTE:
            self.compare('A', 'absolute')
        elif self.IR == CMP_ABSOLUTE_X:
            self.compare('A', 'absolute_indexed', 'X')
        elif self.IR == CMP_ABSOLUTE_Y:
            self.compare('A', 'absolute_indexed', 'Y')
        elif self.IR == CMP_INDIRECT_X:
            self.compare('A', 'indexed_indirect_x')
        elif self.IR == CMP_INDIRECT_Y:
            self.compare('A', 'indirect_indexed_y')
        elif self.IR == CPX_IMMEDIATE:
            self.compare('X', 'immediate')
        elif self.IR == CPX_ZERO_PAGE:
            self.compare('X', 'zero_page')
        elif self.IR == CPX_ABSOLUTE:
            self.compare('X', 'absolute')
        elif self.IR == CPY_IMMEDIATE:
            self.compare('Y', 'immediate')
        elif self.IR == CPY_ZERO_PAGE:
            self.compare('Y', 'zero_page')
        elif self.IR == CPY_ABSOLUTE:
            self.compare('Y', 'absolute')
        # DEC instructions
        elif self.IR == DEC_ZERO_PAGE:
            self.increment(-1, 'zero_page')
        elif self.IR == DEC_ZERO_PAGE_X:
            self.increment(-1, 'zero_page_indexed', 'X')
        elif self.IR == DEC_ABSOLUTE:
            self.increment(-1, 'absolute')
        elif self.IR == DEC_ABSOLUTE_X:
            self.increment(-1, 'absolute_indexed', 'X')
        # Decrement registers X and Y
        elif self.IR == DEX:
            self.increment_register(-1, 'X')
        elif self.IR == DEY:
            self.increment_register(-1, 'Y')
        # EOR instructions
        elif self.IR == EOR_IMMEDIATE:
            self.arithmetic_operation('xor', 'immediate')
        elif self.IR == EOR_ZERO_PAGE:
            self.arithmetic_operation('xor', 'zero_page')
        elif self.IR == EOR_ZERO_PAGE_X:
            self.arithmetic_operation('xor', 'zero_page_indexed', 'X')
        elif self.IR == EOR_ABSOLUTE:
            self.arithmetic_operation('xor', 'absolute')
        elif self.IR == EOR_ABSOLUTE_X:
            self.arithmetic_operation('xor', 'absolute_indexed', 'X')
        elif self.IR == EOR_ABSOLUTE_Y:
            self.arithmetic_operation('xor', 'absolute_indexed', 'Y')
        elif self.IR == EOR_INDIRECT_X:
            self.arithmetic_operation('xor', 'indexed_indirect_x')
        elif self.IR == EOR_INDIRECT_Y:
            self.arithmetic_operation('xor', 'indirect_indexed_y')
        # INC instructions
        elif self.IR == INC_ZERO_PAGE:
            self.increment(1, 'zero_page')
        elif self.IR == INC_ZERO_PAGE_X:
            self.increment(1, 'zero_page_indexed', 'X')
        elif self.IR == INC_ABSOLUTE:
            self.increment(1, 'absolute')
        elif self.IR == INC_ABSOLUTE_X:
            self.increment(1, 'absolute_indexed', 'X')
        # Decrement registers X and Y
        elif self.IR == INX:
            self.increment_register(1, 'X')
        elif self.IR == INY:
            self.increment_register(1, 'Y')
        # JMP instructions
        elif self.IR == JMP_ABSOLUTE:
            self.jump('absolute')
        elif self.IR == JMP_INDIRECT:
            self.jump('indirect')
        # JSR instruction
        elif self.IR == JSR:
            self.jump_to_subroutine()
            # LDA instructions
        elif self.IR == LDA_IMMEDIATE:
            self.load_register('A', 'immediate')
        elif self.IR == LDA_ZERO_PAGE:
            self.load_register('A', 'zero_page')
        elif self.IR == LDA_ZERO_PAGE_X:
            self.load_register('A', 'zero_page_indexed', 'X')
        elif self.IR == LDA_ABSOLUTE:
            self.load_register('A', 'absolute')
        elif self.IR == LDA_ABSOLUTE_X:
            self.load_register('A', 'absolute_indexed', 'X')
        elif self.IR == LDA_ABSOLUTE_Y:
            self.load_register('A', 'absolute_indexed', 'Y')
        elif self.IR == LDA_INDIRECT_X:
            self.load_register('A', 'indexed_indirect_x')
        elif self.IR == LDA_INDIRECT_Y:
            self.load_register('A', 'indirect_indexed_y')
            # LDX instructions
        elif self.IR == LDX_IMMEDIATE:
            self.load_register('X', 'immediate')
        elif self.IR == LDX_ZERO_PAGE:
            self.load_register('X', 'zero_page')
        elif self.IR == LDX_ZERO_PAGE_Y:
            self.load_register('X', 'zero_page_indexed', 'Y')
        elif self.IR == LDX_ABSOLUTE:
            self.load_register('X', 'absolute')
        elif self.IR == LDX_ABSOLUTE_Y:
            self.load_register('X', 'absolute_indexed', 'Y')
        # LDY instructions
        elif self.IR == LDY_IMMEDIATE:
            self.load_register('Y', 'immediate')
        elif self.IR == LDY_ZERO_PAGE:
            self.load_register('Y', 'zero_page')
        elif self.IR == LDY_ZERO_PAGE_X:
            self.load_register('Y', 'zero_page_indexed', 'X')
        elif self.IR == LDY_ABSOLUTE:
            self.load_register('Y', 'absolute')
        elif self.IR == LDX_ABSOLUTE_Y:
            self.load_register('Y', 'absolute_indexed', 'X')
        # Logical shift right
        elif self.IR == LSR_ACCUMULATOR:
            self.shift_accumulator(left=False)
        elif self.IR == LSR_ZERO_PAGE:
            self.shift_memory(left=False, mode='zero_page')
        elif self.IR == LSR_ZERO_PAGE_X:
            self.shift_memory(left=False, mode='zero_page_indexed', index_register='X')
        elif self.IR == LSR_ABSOLUTE:
            self.shift_memory(left=False, mode='absolute')
        elif self.IR == LSR_ABSOLUTE_X:
            self.shift_memory(left=False, mode='absolute_indexed', index_register='X')
            # NOP instruction
        elif self.IR == NOP:
            self.no_operation()
        # ORA instructions
        elif self.IR == ORA_IMMEDIATE:
            self.arithmetic_operation('or_', 'immediate')
        elif self.IR == ORA_ZERO_PAGE:
            self.arithmetic_operation('or_', 'zero_page')
        elif self.IR == ORA_ZERO_PAGE_X:
            self.arithmetic_operation('or_', 'zero_page_indexed', 'X')
        elif self.IR == ORA_ABSOLUTE:
            self.arithmetic_operation('or_', 'absolute')
        elif self.IR == ORA_ABSOLUTE_X:
            self.arithmetic_operation('or_', 'absolute_indexed', 'X')
        elif self.IR == ORA_ABSOLUTE_Y:
            self.arithmetic_operation('or_', 'absolute_indexed', 'Y')
        elif self.IR == ORA_INDIRECT_X:
            self.arithmetic_operation('or_', 'indexed_indirect_x')
        elif self.IR == ORA_INDIRECT_Y:
            self.arithmetic_operation('or_', 'indirect_indexed_y')
        # Push to stack instructions
        elif self.IR == PHA:
            self.push_register_to_stack('A')
        elif self.IR == PHP:
            self.push_register_to_stack('SR')
        # Pull from stack instruction
        elif self.IR == PLA:
            self.pull_register_from_stack('A')
        elif self.IR == PLP:
            self.pull_register_from_stack('SR')
        # Rotate instructions
        elif self.IR == ROL_ACCUMULATOR:
            self.rotate_accumulator(left=True)
        elif self.IR == ROL_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=True)
        elif self.IR == ROL_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_indexed', index_register='X', left=True)
        elif self.IR == ROL_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=True)
        elif self.IR == ROL_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_indexed', index_register='X', left=True)
        elif self.IR == ROR_ACCUMULATOR:
            self.rotate_accumulator(left=False)
        elif self.IR == ROR_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=False)
        elif self.IR == ROR_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_indexed', index_register='X', left=False)
        elif self.IR == ROR_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=False)
        elif self.IR == ROR_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_indexed', index_register='X', left=False)
        # RTI instruction
        elif self.IR == RTI:
            print('RTI')
            self.return_from_interrupt()
        # RTS instruction
        elif self.IR == RTS:
            self.return_from_subroutine()
        # SBC instructions
        elif self.IR == SBC_IMMEDIATE:
            self.arithmetic_operation('sbc', 'immediate')
        elif self.IR == SBC_ZERO_PAGE:
            self.arithmetic_operation('sbc', 'zero_page')
        elif self.IR == SBC_ZERO_PAGE_X:
            self.arithmetic_operation('sbc', 'zero_page_indexed', 'X')
        elif self.IR == SBC_ABSOLUTE:
            self.arithmetic_operation('sbc', 'absolute')
        elif self.IR == SBC_ABSOLUTE_X:
            self.arithmetic_operation('sbc', 'absolute_indexed', 'X')
        elif self.IR == SBC_ABSOLUTE_Y:
            self.arithmetic_operation('sbc', 'absolute_indexed', 'Y')
        elif self.IR == SBC_INDIRECT_X:
            self.arithmetic_operation('sbc', 'indexed_indirect_x')
        elif self.IR == SBC_INDIRECT_Y:
            self.arithmetic_operation('sbc', 'indirect_indexed_y')
        # Set flag instructions
        elif self.IR == SEC:
            self.set_flag('C', True)
        elif self.IR == SED:
            self.set_flag('D', True)
        elif self.IR == SEI:
            self.set_flag('I', True)
        # STA instructions
        elif self.IR == STA_ZERO_PAGE:
            self.store_register('A', 'zero_page')
        elif self.IR == STA_ZERO_PAGE_X:
            self.store_register('A', 'zero_page_indexed', 'X')
        elif self.IR == STA_ABSOLUTE:
            self.store_register('A', 'absolute')
        elif self.IR == STA_ABSOLUTE_X:
            self.store_register('A', 'absolute_indexed', 'X')
        elif self.IR == STA_ABSOLUTE_Y:
            self.store_register('A', 'absolute_indexed', 'Y')
        elif self.IR == STA_INDIRECT_X:
            self.store_register('A', 'indexed_indirect_x')
        elif self.IR == STA_INDIRECT_Y:
            self.store_register('A', 'indirect_indexed_y')
        # STX instructions
        elif self.IR == STX_ZERO_PAGE:
            self.store_register('X', 'zero_page')
        elif self.IR == STX_ZERO_PAGE_Y:
            self.store_register('X', 'zero_page_indexed', 'Y')
        elif self.IR == STX_ABSOLUTE:
            self.store_register('X', 'absolute')
        # STY instructions
        elif self.IR == STY_ZERO_PAGE:
            self.store_register('Y', 'zero_page')
        elif self.IR == STY_ZERO_PAGE_X:
            self.store_register('Y', 'zero_page_indexed', 'X')
        elif self.IR == STY_ABSOLUTE:
            self.store_register('Y', 'absolute')
        # Transfer register to register instructions
        elif self.IR == TAX:
            self.transfer_register('A', 'X')
        elif self.IR == TAY:
            self.transfer_register('A', 'Y')
        elif self.IR == TSX:
            self.transfer_register('S', 'X')
        elif self.IR == TXA:
            self.transfer_register('X', 'A')
        elif self.IR == TXS:
            self.transfer_register('X', 'S')
        elif self.IR == TYA:
            self.transfer_register('Y', 'A')
        else:
            self.no_operation()
            # raise UndefinedInstructionError(self.IR)


def setup_processor(instruction: list[int], data: dict = None, registers: dict = None, flags: dict = None) -> Processor:
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
