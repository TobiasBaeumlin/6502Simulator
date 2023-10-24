import array as ar
from operator import inv, or_, xor, and_
from emulator.opcodes import *
from emulator.operators import (unsigned_byte_addition, signed_addition_overflow, unsigned_byte_subtraction, 
                                signed_subtraction_overflow, unsigned_addition_carry, unsigned_subtraction_carry,
                                shift_left, shift_right)

START_ADDR = 0xfffc

class Memory():
    def __init__(self, size: int) -> None:
        assert size > 2**12, size <= 2**16
        self.size = size
        self.initialise()

    def initialise(self) -> None:
        self.data = ar.array('B', [0] * self.size)

   
class Processor:
    def __init__(self, memory_size=2**16) -> None:
        self.memory_size = memory_size
        self.memory = Memory(memory_size)
        self.PC = START_ADDR    # Program counter
        self.SP = 0xff          # Stack pointer; stack is top down, starts at 0x01ff
        # Registers
        self.A = 0              # Accumulator
        self.X = 0              # Index register X
        self.Y = 0              # Index register Y
        # Processor Status
        self.C = 0          # Carry flag
        self.Z = 0          # Zero flag
        self.I = 0          # Interrupt disable flag
        self.D = 0          # Decimal mode flag
        self.B = 0          # Break command flag
        self.V = 0          # Overflow flag
        self.N = 0          # Negative flag
        # Cycle counter
        self.cycles = 0

    def reset(self) -> None:
        self.PC = START_ADDR
        self.SP = 0xff                 
        self.A = self.X = self.Y = 0
        self.C = self.Z = self.I = self.D = self.B = self.V = self.N = 0
        self.cycles = 0
        self.memory.initialise()

    def cycle(self) -> None:
        self.cycles += 1

    ## Atomic operations
    # Fetch byte from address, consumes one cycle
    def fetch_byte(self, address: int) -> int:
        assert address >=0, address < self.memory_size
        self.cycle()
        return self.memory.data[address]
    
    # Fetches byte in memory location PC, consumes one cycle, increments PC
    def fetch_byte_at_pc(self) -> int:
        byte = self.fetch_byte(self.PC)
        self.PC += 1
        return byte
    
    # Write value to address, consumes one cycle
    def put_byte(self, address: int, value: int) -> None:
        assert address >=0, address < self.memory_size
        self.cycle()
        self.memory.data[address] = value

    # Set Z and N flags according to value in register
    def set_zero_and_negative_status_flags(self, register:str) -> int:
        value = self.__getattribute__(register)
        self.Z = int(value == 0) 
        self.N = int(value >= 128)

    # Add byte b to accumulator, considering C flag. 
    # Set C and V flag according to result 
    def add_to_accumulator_with_carry(self, b: int) -> None:
        assert 0<=b<=255
        if self.D:
            # BCD (Decimal) Mode not yet implemented
            raise Exception
        carry_in = self.C
        sum = unsigned_byte_addition(self.A, b, carry_in)
        carry = unsigned_addition_carry(self.A, b, carry_in)
        overflow = signed_addition_overflow(self.A, b, carry_in)
        self.A, self.C, self.V = sum, carry, overflow
       
    # Subtract byte b from accumulator, considering C flag (subtracting ~C). 
    # Set C and V flag according to result 
    def subtract_from_accumulator_with_carry(self, b: int) -> None:
        assert 0<=b<=255
        if self.D:
            # BCD (Decimal) Mode not yet implemented
            raise Exception
        carry_in = 1-self.C
        difference = unsigned_byte_subtraction(self.A, b, carry_in)
        carry = unsigned_subtraction_carry(self.A, b, carry_in)
        overflow = signed_subtraction_overflow(self.A, b, carry_in)
        self.A, self.C, self.V = difference, carry, overflow
    
    ## Stack operations

    def add_to_stack_pointer(self, increment:int) -> None:
        self.SP = (self.SP + increment) % 0x100

    # Push byte to stack
    def push_to_stack(self, byte:int) -> None:
        assert 0 <= byte <= 0xff
        self.put_byte(0x100+self.SP, byte)


    def push_word_to_stack(self, word:int) -> None:
        assert 0 <= word <= 0xffff
        self.put_byte(0x100+self.SP, word & 0xff)
        self.put_byte(0x100+self.SP-1, word >> 8)

    # Pull byte from stack
    def pull_from_stack(self) -> int:
        byte = self.fetch_byte(0x100+self.SP)
        return byte
    
    def pull_word_from_stack(self) -> int:
        low_byte = self.fetch_byte(0x100+self.SP)
        high_byte = self.fetch_byte(0x100+self.SP-1)
        return low_byte + (high_byte << 8)

    # Address modes to be called by name
    def immediate(self) -> int:
        address = self.PC
        self.PC += 1
        return address
       
    def zero_page(self) -> int:
        return self.fetch_byte_at_pc()
    
    def zero_page_offset(self, register, penalty_cycle=False) -> int:
        self.cycle()
        return unsigned_byte_addition(self.fetch_byte_at_pc(), self.__getattribute__(register))
    
    def absolute(self) -> int:
        address = self.fetch_byte_at_pc()
        address += self.fetch_byte_at_pc() << 8
        return address
    
    def absolute_offset(self, register, penalty_cycle=False) -> int:
        address = self.fetch_byte_at_pc()
        address += self.__getattribute__(register)
        if penalty_cycle or address > 0xff:
            self.cycle()
        address += self.fetch_byte_at_pc() << 8
        return address       
    
    def indexed_indirect_x(self) -> int:
        index = self.fetch_byte_at_pc()
        index = unsigned_byte_addition(index, self.X)
        self.cycle()
        address = self.fetch_byte(index) + (self.fetch_byte(index+1) << 8)
        return address
    
    def indirect_indexed_y(self) -> int:
        index = self.fetch_byte_at_pc()
        address = self.fetch_byte(index)
        address += self.Y
        if address > 0xff:
            self.cycle()
        address += self.fetch_byte(index+1) << 8
        return address
    
    def indirect(self) -> int:
        index_low = self.fetch_byte_at_pc()
        index_high = self.fetch_byte_at_pc()  
        index = (index_high<<8) + index_low
        address_low = self.fetch_byte(index)
        address_high = self.fetch_byte(index+1)
        return (address_high<<8) + address_low     

    def get_address(self, mode:str, offset_register:str=None, penalty_cycle=False) -> int:
        if offset_register is None:
            return self.__getattribute__(mode)()
        return self.__getattribute__(mode)(offset_register, penalty_cycle)   
    
    ## Processor instruction by type    
    # Load value from memory to register, using mode with offset_register
    def load_register(self, register: str, mode:str, offset_register=None) -> None:
        address = self.get_address(mode, offset_register)
        setattr(self, register, self.fetch_byte(address))
        self.set_zero_and_negative_status_flags(register)

    # Store value from register to memory, using mode with offset_register
    def store_register(self, register:str, mode:str, offset_register:str=None) -> None:
        address = self.get_address(mode, offset_register, penalty_cycle=True) 
        self.put_byte(address, self.__getattribute__(register))

    # Transfer value from register source to register destination
    def transfer_register(self, source: str, destination: str) -> None:
        setattr(self, destination, self.__getattribute__(source))
        self.cycle()
        self.set_zero_and_negative_status_flags(destination)

    # Add the content of a memory location to the accumulator together with the carry bit.
    def add_with_carry(self, mode: str, offset_register:str=None) -> None:
        address = self.get_address(mode, offset_register)
        value = self.fetch_byte(address) 
        self.add_to_accumulator_with_carry(value)
        self.set_zero_and_negative_status_flags('A')    

    # Subtract the content of a memory location from the accumulator together with the inverse of the carry bit.
    def subtract_with_carry(self, mode: str, offset_register:str=None) -> None:
        address = self.get_address(mode, offset_register)
        value = self.fetch_byte(address) 
        self.subtract_from_accumulator_with_carry(value)
        self.set_zero_and_negative_status_flags('A')    

    # Bitwise logical operation with accumulator and memory location.
    def logical_operation(self, operator:str, mode: str, offset_register:str=None) -> None:
        address = self.get_address(mode, offset_register)
        value = self.fetch_byte(address)
        self.A = globals()[operator](self.A, value) 
        self.set_zero_and_negative_status_flags('A')

    # Compare register with memory location
    def compare(self, register:str, mode: str, offset_register:str=None) -> None:
        address = self.get_address(mode, offset_register)
        value = self.fetch_byte(address)
        register_value = self.__getattribute__(register)
        if register_value > value:
            self.N = ((register_value-value) & 0x80) >> 7
            self.Z = 0
            self.C = 0
        if register_value == value:
            self.N = 0
            self.Z = 1
            self.C = 1   
        if register_value < value:
            self.N = ((register_value-value) & 0x80) >> 7
            self.Z = 0
            self.C = 1    

    # Branch if flag has given state
    def branch(self, flag:str, state:bool) -> None:
        # PC before start of operation
        pc = self.PC - 1
        relative_address = self.fetch_byte_at_pc()
        flag_state = self.__getattribute__(flag)
        if flag_state == state:
            self.PC += relative_address - 128
            self.cycle()
        # See if page boundary crossed after branch
            if pc//0xff != self.PC//0xff:
                self.cycle()
                self.cycle()    
    
    # Set or clear flag
    def set_flag(self, flag:str, state:bool) -> None:
        setattr(self, flag, state)
        self.cycle()

    # Increment and decrement register
    def increment_register(self, step:int, register:str) -> None:
        value = (self.__getattribute__(register) + step) % 0x100
        self.__setattr__(register, value)
        self.cycle()
        self.set_zero_and_negative_status_flags(register)

    # Increment and decrement memory
    def increment(self, step:int, mode:str, offset_register=None) -> None:
        address = self.get_address(mode, offset_register, penalty_cycle=True)
        value = (self.fetch_byte(address) + step) % 0x100
        self.cycle()
        self.put_byte(address, value)
        self.Z = int(value == 0)
        self.N = int(value > 127)

    ## Stack operations
    # Push processor flags to stack
    def push_processor_status(self) -> None:
        byte = self.C + (self.Z << 1) + (self.I << 2) + (self.D << 3) + (self.B << 4) + (self.V << 6) + (self.N << 7)
        self.push_to_stack(byte)
        self.add_to_stack_pointer(-1)
        self.cycle()

    # Push register to stack
    def push_register(self, register:str) -> None:
        self.push_to_stack(self.__getattribute__(register))
        self.add_to_stack_pointer(-1)
        self.cycle()
    
    # Pull processors from stack
    def pull_processor_status(self) -> None:
        self.add_to_stack_pointer(1)
        self.cycle()
        byte = self.pull_from_stack()
        (self.C, self.Z, self.I, self.D, self.B, self.V, self.N) = (byte&0x1, (byte&0x2) >> 1, (byte&0x4) >> 2, (byte&0x8) >> 3, (byte&0x10) >> 4, (byte&0x40) >> 6, (byte&0x80) >> 7)
        self.cycle()

    # Pull program counter from stack   
    def pull_program_counter(self) -> None:
        self.add_to_stack_pointer(2)
        self.cycle()
        self.PC = self.pull_word_from_stack()
        self.cycle()

    # Pull register from stack
    def pull_register(self, register:str) -> None:
        self.add_to_stack_pointer(1)
        self.cycle()
        self.__setattr__(register, self.pull_from_stack())
        self.cycle()
    
    ## Jump operations
    # Jump instruction (absolute and relative)
    def jump(self, mode):
        address = self.get_address(mode)
        self.PC = address     

    def jump_to_subroutine(self):
        self.push_word_to_stack(self.PC + 1)
        self.add_to_stack_pointer(-2)
        self.cycle()
        self.jump('absolute')

    def return_from_subroutine(self):
        self.add_to_stack_pointer(2)
        self.cycle()
        self.PC = self.pull_word_from_stack() + 1
        self.cycle()
        self.cycle()

    # Break
    def brk(self):
        self.push_word_to_stack(self.PC + 1)
        self.add_to_stack_pointer(-2)
        self.push_processor_status()
        self.PC = self.fetch_byte(0xfffe) + (self.fetch_byte(0xffff) << 8)
        self.B = 1

    def return_from_interrupt(self):
        self.pull_processor_status()
        self.add_to_stack_pointer(2)           
        self.PC = self.pull_word_from_stack() 

    ## Shift and rotate
    def shift_accumulator(self, left:bool=True) -> None:
        if left:
            self.A, carry = shift_left(self.A)
        else:
            self.A, carry = shift_right(self.A)
        self.cycle()
        self.C = carry
        self.set_zero_and_negative_status_flags('A')

    def shift_memory(self, mode:str, offset_register=None, left:bool=True) -> None:
        address = self.get_address(mode, offset_register, penalty_cycle=True)
        if left:
            value, carry = shift_left(self.fetch_byte(address), self.C)
        else:
            value, carry = shift_right(self.fetch_byte(address), self.C)            
        self.cycle()
        self.C = carry
        self.put_byte(address, value)
        self.Z = int(value == 0)
        self.N = int(value > 127)

    def rotate_accumulator(self, left:bool=True) -> None:
        if left:
            self.A, carry = shift_left(self.A, self.C)
        else:
            self.A, carry = shift_right(self.A, self.C)
        self.cycle()
        self.C = carry
        self.set_zero_and_negative_status_flags('A')

    def rotate_memory(self, mode:str, offset_register=None, left:bool=True) -> None:
        address = self.get_address(mode, offset_register, penalty_cycle=True)
        if left:
            value, carry = shift_left(self.fetch_byte(address), self.C)
        else:
            value, carry = shift_right(self.fetch_byte(address), self.C)            
        self.cycle()
        self.put_byte(address, value)
        self.C = carry
        self.Z = int(value == 0)
        self.N = int(value > 127)


    ## Run instruction at PC
    def run_instruction(self):
        op_code = self.fetch_byte_at_pc()
        # ADC: Add with Carry
        if op_code == ADC_IMMEDIATE:
            self.add_with_carry('immediate')
        elif op_code == ADC_ZERO_PAGE:
            self.add_with_carry('zero_page')            
        elif op_code == ADC_ZERO_PAGE_X:
            self.add_with_carry('zero_page_offset', 'X')
        elif op_code == ADC_ABSOLUTE:
            self.add_with_carry('absolute')            
        elif op_code == ADC_ABSOLUTE_X:
            self.add_with_carry('absolute_offset', 'X')             
        elif op_code == ADC_ABSOLUTE_Y:
            self.add_with_carry('absolute_offset', 'Y')      
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
            self.logical_operation('and_', 'zero_page_offset', 'X')
        elif op_code == AND_ABSOLUTE:
            self.logical_operation('and_', 'absolute')
        elif op_code == AND_ABSOLUTE_X:
            self.logical_operation('and_', 'absolute_offset', 'X')
        elif op_code == AND_ABSOLUTE_Y:
            self.logical_operation('and_', 'absolute_offset', 'Y')
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
            self.shift_memory(left=True, mode='zero_page_offset', offset_register='X')
        elif op_code == ASL_ABSOLUTE:
            self.shift_memory(left=True, mode='absolute')
        elif op_code == ASL_ABSOLUTE_X:
            self.shift_memory(left=True, mode='absolute_offset', offset_register='X')       
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
            self.compare('A', 'zero_page_offset', 'X')
        elif op_code == CMP_ABSOLUTE:
            self.compare('A', 'absolute')
        elif op_code == CMP_ABSOLUTE_X:
            self.compare('A', 'absolute_offset', 'X')
        elif op_code == CMP_ABSOLUTE_Y:
            self.compare('A', 'absolute_offset', 'Y')
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
            self.increment(-1, 'zero_page_offset', 'X')
        elif op_code == DEC_ABSOLUTE:
            self.increment(-1, 'absolute')
        elif op_code == DEC_ABSOLUTE_X:
            self.increment(-1, 'absolute_offset', 'X')
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
            self.logical_operation('xor', 'zero_page_offset', 'X')
        elif op_code == EOR_ABSOLUTE:
            self.logical_operation('xor', 'absolute')
        elif op_code == EOR_ABSOLUTE_X:
            self.logical_operation('xor', 'absolute_offset', 'X')
        elif op_code == EOR_ABSOLUTE_Y:
            self.logical_operation('xor', 'absolute_offset', 'Y')
        elif op_code == EOR_INDIRECT_X:
            self.logical_operation('xor', 'indexed_indirect_x')
        elif op_code == EOR_INDIRECT_Y:
            self.logical_operation('xor', 'indirect_indexed_y')
        # INC instructions
        elif op_code == INC_ZERO_PAGE:
            self.increment(1, 'zero_page')
        elif op_code == INC_ZERO_PAGE_X:
            self.increment(1, 'zero_page_offset', 'X')
        elif op_code == INC_ABSOLUTE:
            self.increment(1, 'absolute')
        elif op_code == INC_ABSOLUTE_X:
            self.increment(1, 'absolute_offset', 'X')
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
            self.load_register('A', 'zero_page_offset', 'X')
        elif op_code == LDA_ABSOLUTE:
            self.load_register('A', 'absolute')
        elif op_code == LDA_ABSOLUTE_X:
            self.load_register('A', 'absolute_offset', 'X')
        elif op_code == LDA_ABSOLUTE_Y:
            self.load_register('A', 'absolute_offset', 'Y')
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
            self.load_register('X', 'zero_page_offset', 'Y')
        elif op_code == LDX_ABSOLUTE:
            self.load_register('X', 'absolute')
        elif op_code == LDX_ABSOLUTE_Y:
            self.load_register('X', 'absolute_offset', 'Y')
        # LDY instructions
        elif op_code == LDY_IMMEDIATE:
            self.load_register('Y', 'immediate')
        elif op_code == LDY_ZERO_PAGE:
            self.load_register('Y', 'zero_page')
        elif op_code == LDY_ZERO_PAGE_X:
            self.load_register('Y', 'zero_page_offset', 'X')
        elif op_code == LDY_ABSOLUTE:
            self.load_register('Y', 'absolute')
        elif op_code == LDX_ABSOLUTE_Y:
            self.load_register('Y', 'absolute_offset', 'X')
        # Logical shift right
        elif op_code == LSR_ACCUMULATOR:
            self.shift_accumulator(left=False)
        elif op_code == LSR_ZERO_PAGE:
            self.shift_memory(left=False, mode='zero_page')
        elif op_code == LSR_ZERO_PAGE_X:
            self.shift_memory(left=False, mode='zero_page_offset', offset_register='X')
        elif op_code == LSR_ABSOLUTE:
            self.shift_memory(left=False, mode='absolute')
        elif op_code == LSR_ABSOLUTE_X:
            self.shift_memory(left=False, mode='absolute_offset', offset_register='X')       
        # NOP instruction
        elif op_code == NOP:
            self.no_operation()
        # ORA instructions
        elif op_code == ORA_IMMEDIATE:
            self.logical_operation('or_', 'immediate')
        elif op_code == ORA_ZERO_PAGE:
            self.logical_operation('or_', 'zero_page')
        elif op_code == ORA_ZERO_PAGE_X:
            self.logical_operation('or_', 'zero_page_offset', 'X')
        elif op_code == ORA_ABSOLUTE:
            self.logical_operation('or_', 'absolute')
        elif op_code == ORA_ABSOLUTE_X:
            self.logical_operation('or_', 'absolute_offset', 'X')
        elif op_code == ORA_ABSOLUTE_Y:
            self.logical_operation('or_', 'absolute_offset', 'Y')
        elif op_code == ORA_INDIRECT_X:
            self.logical_operation('or_', 'indexed_indirect_x')
        elif op_code == ORA_INDIRECT_Y:
            self.logical_operation('or_', 'indirect_indexed_y')
        # Push to stack instructions
        elif op_code == PHA:
            self.push_register('A')
        elif op_code == PHP:
            self.push_processor_status()
        # Pull from stack instruction
        elif op_code == PLA:
            self.pull_register('A')
        elif op_code == PLP:
            self.pull_processor_status()
        # Rotate instructions
        elif op_code == ROL_ACCUMULATOR:
            self.rotate_accumulator(left=True)
        elif op_code == ROL_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=True)
        elif op_code == ROL_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_offset', offset_register='X', left=True)
        elif op_code == ROL_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=True)
        elif op_code == ROL_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_offset', offset_register='X', left=True)
        elif op_code == ROR_ACCUMULATOR:
            self.rotate_accumulator(left=False)
        elif op_code == ROR_ZERO_PAGE:
            self.rotate_memory(mode='zero_page', left=False)
        elif op_code == ROR_ZERO_PAGE_X:
            self.rotate_memory(mode='zero_page_offset', offset_register='X', left=False)
        elif op_code == ROR_ABSOLUTE:
            self.rotate_memory(mode='absolute', left=False)
        elif op_code == ROR_ABSOLUTE_X:
            self.rotate_memory(mode='absolute_offset', offset_register='X', left=False)
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
            self.subtract_with_carry('zero_page_offset', 'X')
        elif op_code == SBC_ABSOLUTE:
            self.subtract_with_carry('absolute')            
        elif op_code == SBC_ABSOLUTE_X:
            self.subtract_with_carry('absolute_offset', 'X')             
        elif op_code == SBC_ABSOLUTE_Y:
            self.subtract_with_carry('absolute_offset', 'Y')      
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
            self.store_register('A', 'zero_page_offset', 'X')
        elif op_code == STA_ABSOLUTE:
            self.store_register('A', 'absolute')
        elif op_code == STA_ABSOLUTE_X:
            self.store_register('A', 'absolute_offset', 'X')
        elif op_code == STA_ABSOLUTE_Y:
            self.store_register('A', 'absolute_offset', 'Y')
        elif op_code == STA_INDIRECT_X:
            self.store_register('A', 'indexed_indirect_x')
        elif op_code == STA_INDIRECT_Y:
            self.store_register('A', 'indirect_indexed_y')
        # STX instructions
        elif op_code == STX_ZERO_PAGE:
            self.store_register('X', 'zero_page')
        elif op_code == STX_ZERO_PAGE_Y:
            self.store_register('X', 'zero_page_offset', 'Y')
        elif op_code == STX_ABSOLUTE:
            self.store_register('X', 'absolute')
        # STY instructions
        elif op_code == STY_ZERO_PAGE:
            self.store_register('Y', 'zero_page')
        elif op_code == STY_ZERO_PAGE_X:
            self.store_register('Y', 'zero_page_offset', 'X')
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
            
def setup_processor(instruction:list[int]=[], data:dict={}, registers:dict={}, flags:dict={}) -> Processor:
    processor = Processor()

    for a, v in data.items():
        processor.memory.data[a] = v

    for r, v in registers.items():
        processor.__setattr__(r, v)

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
    
