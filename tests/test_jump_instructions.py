import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *

def test_jump_instruction(instruction:list[int], target, num_cycles:int, data={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    processor.run_instruction()
    
    assert processor.PC == target
    assert processor.cycles == num_cycles

def test_jump_to_subroutine_instruction(instruction:list[int], target, num_cycles:int, data={}) -> None:
    processor = setup_processor(instruction, data=data)
    
    return_point = processor.PC + 2
    sp = processor.SP
    processor.run_instruction()
    
    assert processor.PC == target
    assert processor.SP == sp - 2
    assert processor.memory.data[0x0100+sp] + (processor.memory.data[0x0100+sp-1] << 8) == return_point
    assert processor.cycles == num_cycles

def test_return_from_subroutine_instruction(instruction:list[int], return_point, num_cycles:int, data:dict={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    sp = processor.SP
    processor.run_instruction()
    
    assert processor.PC == return_point
    assert processor.SP == sp + 2
    assert processor.cycles == num_cycles

def test_break(instruction:list[int], num_cycles, data, register_data):
    processor = setup_processor(instruction, data=data, registers=register_data)
        
    return_point = processor.PC + 2
    sp = processor.SP
    processor.run_instruction()
    
    assert processor.PC == processor.memory.data[0xfffe] + (processor.memory.data[0xffff] << 8)
    assert processor.SP == sp - 3
    assert processor.memory.data[0x0100+sp] + (processor.memory.data[0x0100+sp-1] << 8) == return_point
    assert processor.cycles == num_cycles

def test_return_from_interrupt(instruction:list[int], return_point, num_cycles:int, data:dict={}, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data=data, registers=register_data)
    
    sp = processor.SP
    processor.run_instruction()
    
    assert processor.PC == return_point
    assert processor.SP == sp + 3
    assert processor.cycles == num_cycles


class ProcessorTest(unittest.TestCase):       
    def test_jump_absolute(self):
        test_jump_instruction([JMP_ABSOLUTE, 0xb0, 0x1e], target=0x1eb0, num_cycles=3)

    def test_jump_relative(self):
        test_jump_instruction([JMP_INDIRECT, 0x20, 0x01], data={0x0120: 0xfc, 0x0121: 0xba}, target=0xbafc, num_cycles=5)

    def test_jump_to_subroutine(self):
        test_jump_to_subroutine_instruction([JSR, 0x01, 0xa0], target=0xa001, num_cycles=6)

    def test_return_from_subroutine(self):
        test_return_from_subroutine_instruction([RTS], return_point=0x2003, num_cycles=6, 
                                                data={0x01fe:0x20, 0x01ff:0x02}, register_data={'SP': 0xfd})

    def test_break(self):
        test_break([BRK], num_cycles=7, data={0xfffe: 0x05, 0xffff: 0x04}, register_data={'PC': 0x0200})

    def test_return_from_interrupt(self):
        test_return_from_interrupt([RTI], return_point=0x8000, num_cycles=6, data={0x1fd:0b11011101, 0x01fe:0x80, 0x1ff:0x00}, 
                                   register_data={'SP': 0xfc})

    def test_can_return_from_subroutine(self):
        data = {
            # Program starts at 0x0200
            0x0200: JSR, 
            0x0201: 0x00, 
            0x0202: 0x80,
            0x0203: LDX_IMMEDIATE,
            0x0204: 0x43,
            # Subroutine at 0x8000
            0x8000: LDA_IMMEDIATE, 
            0x8001: 0x42, 
            0x8002: RTS
            }
        register_data = {'A': 0x10, 'SP': 0xa0, 'PC':0x0200}
        processor = setup_processor(data=data, registers=register_data)
        for _ in range(4):
            processor.run_instruction()
        assert processor.A == 0x42
        assert processor.X == 0x43

if __name__ == '__main__':
    unittest.main()