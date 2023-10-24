import unittest
from operator import inv, or_, xor, and_
from emulator.processor import setup_processor, START_ADDR
from emulator.operators import signed_addition_overflow, signed_subtraction_overflow
from emulator.opcodes import *


def test_logical_instruction(instruction:list[int], operator:str, operand:int, num_cycles:int, data:dict={}, register_data:dict={}, carry:bool=False) -> None:
    processor = setup_processor(instruction, data, register_data)

    a = processor.A
    result = globals()[operator](a, operand)
    
    processor.run_instruction()

    assert processor.A == result
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == START_ADDR + len(instruction)
   

class ProcessorTest(unittest.TestCase):
    ## Addition
    def test_and_immediate(self):
        test_logical_instruction(instruction=[AND_IMMEDIATE, 0x69], operator='and_', register_data={'A': 0x0f},  operand=0x69, 
                                 num_cycles=2, carry=True)
        
    def test_and_zero_page(self):
        test_logical_instruction(instruction=[AND_ZERO_PAGE, 0x0a], operator='and_', register_data={'A': 0xf0}, operand=0x0f,
                                 data={0x0a: 0x0f}, num_cycles=3)
        
    def test_and_zero_page_x(self):
        test_logical_instruction(instruction=[AND_ZERO_PAGE_X, 0x0a], operator='and_', register_data={'A': 0xf0, 'X': 0xf0}, operand=0x20, 
                                 data={0xfa: 0x20}, num_cycles=4)
        
    def test_and_absolute(self):
        test_logical_instruction(instruction=[AND_ABSOLUTE, 0x0a, 0x20], operator='and_', register_data={'A': 0xf0}, operand=0x10,
                                 data={0x200a: 0x10}, num_cycles=4)  
         
    def test_and_absolute_x_same_page(self):
        test_logical_instruction(instruction=[AND_ABSOLUTE_X, 0x0a, 0x20], operator='and_', register_data={'A': 0xf0, 'X':0x01}, operand=0x0,
                                 data={0x200b: 0x0}, num_cycles=4) 
        
    def test_and_absolute_x_cross_page_boundary(self):
        test_logical_instruction(instruction=[AND_ABSOLUTE_X, 0x10, 0x20], operator='and_', register_data={'A': 0x01, 'X':0xf0}, operand=0x01,
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_and_absolute_y_same_page(self):
        test_logical_instruction(instruction=[AND_ABSOLUTE_Y, 0x0a, 0x20], operator='and_', register_data={'A': 0xf0, 'Y':0x01}, operand=0x10,
                                 data={0x200b: 0x10}, num_cycles=4) 
        
    def test_and_absolute_y_cross_page_boundary(self):
        test_logical_instruction(instruction=[AND_ABSOLUTE_Y, 0x10, 0x20], operator='and_', register_data={'A': 0x01, 'Y':0xf0}, operand=0x01,
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_and_indirect_x(self):
        test_logical_instruction(instruction=[AND_INDIRECT_X, 0x40], operator='and_', register_data={'A': 0x01, 'X':0xf0}, operand=0x01,
                                 data={0x30:0x00, 0x31:0x21, 0x2100: 0x01},  num_cycles=6, carry=True) 
        
    def test_and_indirect_y_same_page(self):
        test_logical_instruction(instruction=[AND_INDIRECT_Y, 0x30], operator='and_', register_data={'A': 0xff, 'Y':0xf0}, operand=0x01,
                                 data={0x30:0x00, 0x31:0x21, 0x21f0: 0x01}, num_cycles=5) 

    ## Exclusive or
    def test_eor_immediate(self):
        test_logical_instruction(instruction=[EOR_IMMEDIATE, 0xff], operator='xor', register_data={'A': 0x0f}, operand=0xff,
                                 num_cycles=2, carry=True)
        
    def test_eor_zero_page(self):
        test_logical_instruction(instruction=[EOR_ZERO_PAGE, 0x0a], operator='xor', register_data={'A': 0xf0}, operand=0x69,
                                 data={0x0a: 0x69}, num_cycles=3)
        
    def test_eor_zero_page_x(self):
        test_logical_instruction(instruction=[EOR_ZERO_PAGE_X, 0x0a], operator='xor', register_data={'A': 0xf0, 'X': 0xf0}, operand=0x20,
                                 data={0xfa: 0x20}, num_cycles=4)
        
    def test_eor_absolute(self):
        test_logical_instruction(instruction=[EOR_ABSOLUTE, 0x0a, 0x20], operator='xor', register_data={'A': 0xf0}, operand=0x10,
                                 data={0x200a: 0x10}, num_cycles=4)  
         
    def test_eor_absolute_x_same_page(self):
        test_logical_instruction(instruction=[EOR_ABSOLUTE_X, 0x0a, 0x20], operator='xor', register_data={'A': 0xf0, 'X':0x01}, operand=0x10,
                                 data={0x200b: 0x10}, num_cycles=4) 
        
    def test_eor_absolute_x_cross_page_boundary(self):
        test_logical_instruction(instruction=[EOR_ABSOLUTE_X, 0x10, 0x20], operator='xor', register_data={'A': 0x01, 'X':0xf0}, operand=0x01,
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_eor_absolute_y_same_page(self):
        test_logical_instruction(instruction=[EOR_ABSOLUTE_Y, 0x0a, 0x20], operator='xor',  register_data={'A': 0xf0, 'Y':0x01}, operand=0x10,
                                 data={0x200b: 0x10}, num_cycles=4) 
        
    def test_eor_absolute_y_cross_page_boundary(self):
        test_logical_instruction(instruction=[EOR_ABSOLUTE_Y, 0x10, 0x20], operator='xor', register_data={'A': 0x01, 'Y':0xf0}, operand=0x01,
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_eor_indirect_x(self):
        test_logical_instruction(instruction=[EOR_INDIRECT_X, 0x40], operator='xor', register_data={'A': 0x01, 'X':0xf0}, operand=0x01, 
                                 data={0x30:0x00, 0x31:0x21, 0x2100: 0x01}, num_cycles=6, carry=True) 
        
    def test_eor_indirect_y_same_page(self):
        test_logical_instruction(instruction=[EOR_INDIRECT_Y, 0x30],operator='xor',  register_data={'A': 0xff, 'Y':0xf0}, operand=0x01, 
                                 data={0x30:0x00, 0x31:0x21, 0x21f0: 0x01}, num_cycles=5) 
    
    ## Inclusive or
    def test_ora_immediate(self):
        test_logical_instruction(instruction=[ORA_IMMEDIATE, 0xf0], operator='or_', register_data={'A': 0x0f}, operand=0xff, 
                                 num_cycles=2, carry=True)
        
    def test_ora_zero_page(self):
        test_logical_instruction(instruction=[ORA_ZERO_PAGE, 0x0a], operator='or_', register_data={'A': 0xf0}, operand=0x20,
                                 data={0x0a: 0x20}, num_cycles=3)
        
    def test_ora_zero_page_x(self):
        test_logical_instruction(instruction=[ORA_ZERO_PAGE_X, 0x0a], operator='or_', register_data={'A': 0xf0, 'X': 0xf0}, operand=0x20,
                                 data={0xfa: 0x20}, num_cycles=4)
        
    def test_ora_absolute(self):
        test_logical_instruction(instruction=[ORA_ABSOLUTE, 0x0a, 0x20], operator='or_', register_data={'A': 0xf0}, operand=0x10,
                                 data={0x200a: 0x10}, num_cycles=4)  
         
    def test_ora_absolute_x_same_page(self):
        test_logical_instruction(instruction=[ORA_ABSOLUTE_X, 0x0a, 0x20], operator='or_', register_data={'A': 0xf0, 'X':0x01}, operand=0x10,
                                 data={0x200b: 0x10}, num_cycles=4) 
        
    def test_ora_absolute_x_cross_page_boundary(self):
        test_logical_instruction(instruction=[ORA_ABSOLUTE_X, 0x10, 0x20], operator='or_', register_data={'A': 0xff, 'X':0xf0}, operand=0x01, 
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_ora_absolute_y_same_page(self):
        test_logical_instruction(instruction=[ORA_ABSOLUTE_Y, 0x0a, 0x20], operator='or_', register_data={'A': 0xf0, 'Y':0x01}, operand=0x10,
                                 data={0x200b: 0x10}, num_cycles=4) 
        
    def test_ora_absolute_y_cross_page_boundary(self):
        test_logical_instruction(instruction=[ORA_ABSOLUTE_Y, 0x10, 0x20], operator='or_', register_data={'A': 0x01, 'Y':0xf0}, operand=0x01,
                                 data={0x2100: 0x01}, num_cycles=5, carry=True) 
        
    def test_ora_indirect_x(self):
        test_logical_instruction(instruction=[ORA_INDIRECT_X, 0x40], operator='or_', register_data={'A': 0x0, 'X':0xf0}, operand=0x01,
                                 data={0x30:0x00, 0x31:0x21, 0x2100: 0x01}, num_cycles=6, carry=True) 
        
    def test_ora_indirect_y_same_page(self):
        test_logical_instruction(instruction=[ORA_INDIRECT_Y, 0x30], operator='or_', register_data={'A': 0xff, 'Y':0xf0}, operand=0x0,
                                 data={0x30:0x00, 0x31:0x21, 0x21f0: 0x0}, num_cycles=5) 

if __name__ == '__main__':
    unittest.main()
