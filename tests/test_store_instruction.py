import unittest
from emulator.processor import setup_processor, START_ADDR
from emulator.opcodes import *


def test_store_instruction(instruction:list[int], destination:int, value:int, num_cycles:int, data:dict={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data, register_data)
    processor.run_instruction()

    assert processor.memory.data[destination] == value
    assert processor.cycles == num_cycles
    assert processor.PC == START_ADDR + len(instruction)
   

class ProcessorTest(unittest.TestCase):
    def test_sta_zero_page(self):
        test_store_instruction(instruction=[STA_ZERO_PAGE, 0xff], destination=0xff, value=0x42, num_cycles=3, 
                               register_data={'A': 0x42})
    def test_sta_zero_page_x(self):
        test_store_instruction(instruction=[STA_ZERO_PAGE_X, 0xf0], destination=0x10, value=0x42, num_cycles=4, 
                               register_data={'A': 0x42, 'X':0x20})
    def test_sta_absolute(self):
        test_store_instruction(instruction=[STA_ABSOLUTE, 0xf0, 0x10], destination=0x10f0, value=0x42, num_cycles=4, 
                               register_data={'A': 0x42})
    def test_sta_absolute_x(self):
        test_store_instruction(instruction=[STA_ABSOLUTE_X, 0xf0, 0x10], destination=0x10f1, value=0x42, num_cycles=5, 
                               register_data={'A': 0x42, 'X': 0x01})
    def test_sta_absolute_y(self):
        test_store_instruction(instruction=[STA_ABSOLUTE_Y, 0xf0, 0x10], destination=0x10fa, value=0x42, num_cycles=5, 
                               register_data={'A': 0x42, 'Y': 0x0a})
    def test_sta_indirect_x(self):
        test_store_instruction(instruction=[STA_INDIRECT_X, 0x10], destination=0x10fa, value=0x42, num_cycles=6, 
                               data={0x1a:0xfa, 0x1b:0x10}, register_data={'A': 0x42, 'X': 0x0a})
    def test_sta_indirect_y(self):
        test_store_instruction(instruction=[STA_INDIRECT_Y, 0xf0], destination=0x110a, value=0x42, num_cycles=6, 
                               data={0xf0:0xfa, 0xf1:0x10}, register_data={'A': 0x42, 'Y': 0x10})
    def test_stx_zero_page(self):
        test_store_instruction(instruction=[STX_ZERO_PAGE, 0xf0], destination=0xf0, value=0x42, num_cycles=3, 
                               register_data={'X': 0x42})        
    def test_stx_zero_page_y(self):
        test_store_instruction(instruction=[STX_ZERO_PAGE_Y, 0x30], destination=0x50, value=0x42, num_cycles=4, 
                               register_data={'X': 0x42, 'Y':0x20})
    def test_stx_absolute(self):
        test_store_instruction(instruction=[STX_ABSOLUTE, 0xaa, 0xd0], destination=0xd0aa, value=0x42, num_cycles=4, 
                               register_data={'X': 0x42})
    def test_sty_zero_page(self):
        test_store_instruction(instruction=[STY_ZERO_PAGE, 0x00], destination=0x00, value=0x42, num_cycles=3, 
                               register_data={'Y': 0x42})        
    def test_sty_zero_page_x(self):
        test_store_instruction(instruction=[STY_ZERO_PAGE_X, 0xe0], destination=0x50, value=0x42, num_cycles=4, 
                               register_data={'Y': 0x42, 'X':0x70})
    def test_sty_absolute(self):
        test_store_instruction(instruction=[STY_ABSOLUTE, 0xaa, 0xd0], destination=0xd0aa, value=0x42, num_cycles=4, 
                               register_data={'Y': 0x42})
 
    
        
if __name__ == '__main__':
    unittest.main()