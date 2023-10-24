import unittest
from emulator.processor import setup_processor, START_ADDR
from emulator.opcodes import *


def test_transfer_register_instruction(instruction:list[int], source:str, destination:str, num_cycles:int, register_data:dict={}) -> None:
    processor = setup_processor(instruction, {}, register_data)
    
    source_value = getattr(processor, source)
    processor.run_instruction()
    destination_value = getattr(processor, destination)

    assert destination_value == source_value
    assert getattr(processor, source) == source_value
    assert processor.N == (destination_value > 127)
    assert processor.Z == (destination_value == 0)
    assert processor.cycles == num_cycles
    assert processor.PC == START_ADDR + len(instruction)
   

class ProcessorTest(unittest.TestCase):
    def test_transfer_a_to_x(self):
        test_transfer_register_instruction([TAX], source='A', destination='X', num_cycles=2, register_data={'A':0x5, 'X':0xff})

    def test_transfer_a_to_y(self):
        test_transfer_register_instruction([TAY], source='A', destination='Y', num_cycles=2, register_data={'A':0x0, 'Y':0xfa})
 
    def test_transfer_s_to_x(self):
        test_transfer_register_instruction([TSX], source='S', destination='X', num_cycles=2, register_data={'S':0x0, 'X':0xff})    

    def test_transfer_x_to_a(self):
        test_transfer_register_instruction([TXA], source='X', destination='A', num_cycles=2, register_data={'X':0xff, 'A':0xff})  
 
    def test_transfer_x_to_s(self):
        test_transfer_register_instruction([TXS], source='X', destination='S', num_cycles=2, register_data={'X':0xaf, 'S':0x0})    
     
    def test_transfer_y_to_a(self):
        test_transfer_register_instruction([TYA], source='Y', destination='A', num_cycles=2, register_data={'Y':0x42, 'A':0xff})    
      
if __name__ == '__main__':
    unittest.main()