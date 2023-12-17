import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *

def test_push_accumulator_instruction(instruction:list[int], num_cycles:int, data={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    a = processor.A
    sp = processor.S
    processor.run_instruction()
    
    assert processor.S == sp - 1
    assert processor.memory.data[0x100+sp] == a
    assert processor.cycles == num_cycles

def test_pull_accumulator_instruction(instruction:list[int], value, num_cycles:int, data={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    sp = processor.S
    processor.run_instruction()
    
    assert processor.S == sp + 1
    assert processor.A == value
    assert processor.cycles == num_cycles

def test_push_processor_status_instruction(instruction:list[int], num_cycles:int, data={}, register_data:dict={}, flags:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data, flags=flags)
    
    status = processor.C + (processor.Z << 1) + (processor.I << 2) + (processor.D << 3) + (processor.B << 4) + (processor.V << 6) + (processor.N << 7)  
    sp = processor.S
    processor.run_instruction()
    
    assert processor.S == sp - 1
    assert processor.memory.data[0x100+sp] == status
    assert processor.cycles == num_cycles


def test_pull_processor_status_instruction(
        instruction:list[int], num_cycles:int, data={}, register_data:dict={}, flags:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    sp = processor.S
    processor.run_instruction()
    
    assert processor.S == sp+1
    assert processor.C == flags['C']
    assert processor.Z == flags['Z']
    assert processor.I == flags['I']
    assert processor.D == flags['D']    
    assert processor.B == flags['B']
    assert processor.V == flags['V']   
    assert processor.N == flags['N']   
    assert processor.cycles == num_cycles


class ProcessorTest(unittest.TestCase):
    def test_push_accumulator(self):
        test_push_accumulator_instruction([PHA], num_cycles=3, register_data={'A': 0x34})

    def test_pull_accumulator(self):
        test_pull_accumulator_instruction([PLA], value=0x42, num_cycles=4, register_data={'S': 0xfe},
                                          data={0x01ff:0x42})
    
    def test_push_processor_status(self):
        test_push_processor_status_instruction([PHP], num_cycles=3, register_data={'A': 0x34}, 
                                               flags={'N': 1,'V': 1, 'I': 1, 'Z': 1, 'C': 1})

    def test_pull_processor_status(self):
        test_pull_processor_status_instruction([PLP], num_cycles=4, register_data={'S': 0xfe},
                                               data={0x01ff: 0b11000111},
                                               flags={'N': 1,'V': 1, 'I': 1, 'D':0, 'B':0, 'Z': 1, 'C': 1})
       
 
if __name__ == '__main__':
    unittest.main()
