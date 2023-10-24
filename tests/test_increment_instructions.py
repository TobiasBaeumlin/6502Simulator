import unittest
from emulator.processor import setup_processor, START_ADDR
from emulator.operators import signed_addition_overflow, signed_subtraction_overflow
from emulator.opcodes import *


def test_increment_memory_instruction(instruction:list[int], address:int, value:int, increment:int, num_cycles:int=0, data:dict={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data, register_data)  
    result = (value + increment) % 256
    
    processor.run_instruction()

    assert processor.memory.data[address] == result   
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == START_ADDR + len(instruction)
   
def test_increment_register_instruction(instruction:list[int], register:str, value:int, increment:int, num_cycles:int=0, data:dict={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data, register_data)  
    result = (value + increment) % 256
    
    processor.run_instruction()

    assert processor.__getattribute__(register) == result  
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == START_ADDR + len(instruction)


class ProcessorTest(unittest.TestCase):
    ## Increment memory location
    def test_inc_zero_page(self):
        test_increment_memory_instruction(instruction=[INC_ZERO_PAGE, 0xfa], address=0xfa, value=0x1f, increment=1,
                                          data={0xfa:0x1f}, num_cycles=5)
    def test_inc_zero_page_x(self):
        test_increment_memory_instruction(instruction=[INC_ZERO_PAGE_X, 0xf0], address=0x10, value=0xff, increment=1, 
                                          data={0x10:0xff}, register_data={'X': 0x20}, num_cycles=6)
    def test_inc_absolute(self):
        test_increment_memory_instruction(instruction=[INC_ABSOLUTE, 0x0, 0x20], address=0x2000, value=0x1f, increment=1, 
                                          data={0x2000:0x1f}, num_cycles=6)
    def test_inc_absolute_x(self):
        test_increment_memory_instruction(instruction=[INC_ABSOLUTE_X, 0x0, 0x20], address=0x2060, value=0x7f, increment=1, 
                                          data={0x2060:0x7f}, register_data={'X': 0x60}, num_cycles=7)
    def test_dec_zero_page(self):
        test_increment_memory_instruction(instruction=[DEC_ZERO_PAGE, 0xfa], address=0xfa, value=0x1f, increment=-1, 
                                          data={0xfa:0x1f}, num_cycles=5)
    def test_dec_zero_page_x(self):
        test_increment_memory_instruction(instruction=[DEC_ZERO_PAGE_X, 0xf0], address=0x10, value=0xff, increment=-1, 
                                          data={0x10:0xff}, register_data={'X': 0x20}, num_cycles=6)
    def test_dec_absolute(self):
        test_increment_memory_instruction(instruction=[DEC_ABSOLUTE, 0x0, 0x20], address=0x2000, value=0x1f, increment=-1, 
                                          data={0x2000:0x1f}, num_cycles=6)
    def test_dec_absolute_x(self):
        test_increment_memory_instruction(instruction=[DEC_ABSOLUTE_X, 0x0, 0x20], address=0x2060, value=0x7f, increment=-1, 
                                          data={0x2060:0x7f}, register_data={'X': 0x60}, num_cycles=7)
    def test_inx(self):
        test_increment_register_instruction(instruction=[INX], register='X', value=0xff, increment=1, num_cycles=2, 
                                            register_data={'X':0xff})
    def test_iny(self):
        test_increment_register_instruction(instruction=[INY], register='Y', value=0x0, increment=1, num_cycles=2, 
                                            register_data={'Y':0x0})
    def test_dex(self):
        test_increment_register_instruction(instruction=[DEX], register='X', value=0xff, increment=-1, num_cycles=2, 
                                            register_data={'X':0xff})
    def test_dey(self):
        test_increment_register_instruction(instruction=[DEY], register='Y', value=0x0, increment=-1, num_cycles=2, 
                                            register_data={'Y':0x0})

 
 
if __name__ == '__main__':
    unittest.main()
