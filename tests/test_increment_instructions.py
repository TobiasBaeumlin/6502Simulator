import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *


def test_increment_memory_instruction(
        instruction: list[int], address: int, value: int, increment: int, num_cycles: int = 0,
        data: dict = None, register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)  
    result = (value + increment) % 256
    
    processor.run_instruction()

    assert processor.memory.data[address] == result   
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == len(instruction)


def test_increment_register_instruction(
        instruction: list[int], register: str, value: int, increment: int, num_cycles: int = 0,
        data: dict = None, register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)  
    result = (value + increment) % 256
    
    processor.run_instruction()

    assert processor.__getattribute__(register) == result  
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == len(instruction)


class ProcessorTest(unittest.TestCase):
    # Increment memory location

    @staticmethod
    def test_inc_zero_page():
        test_increment_memory_instruction(instruction=[INC_ZERO_PAGE, 0xfa], address=0xfa, value=0x1f, increment=1,
                                          data={0xfa: 0x1f}, num_cycles=5)

    @staticmethod
    def test_inc_zero_page_x():
        test_increment_memory_instruction(instruction=[INC_ZERO_PAGE_X, 0xf0], address=0x10, value=0xff, increment=1, 
                                          data={0x10: 0xff}, register_data={'X': 0x20}, num_cycles=6)

    @staticmethod
    def test_inc_absolute():
        test_increment_memory_instruction(instruction=[INC_ABSOLUTE, 0x0, 0x20], address=0x2000, value=0x1f,
                                          increment=1, data={0x2000: 0x1f}, num_cycles=6)

    @staticmethod
    def test_inc_absolute_x():
        test_increment_memory_instruction(instruction=[INC_ABSOLUTE_X, 0x0, 0x20], address=0x2060, value=0x7f,
                                          increment=1, data={0x2060: 0x7f}, register_data={'X': 0x60}, num_cycles=7)

    @staticmethod
    def test_dec_zero_page():
        test_increment_memory_instruction(instruction=[DEC_ZERO_PAGE, 0xfa], address=0xfa, value=0x1f, increment=-1, 
                                          data={0xfa: 0x1f}, num_cycles=5)

    @staticmethod
    def test_dec_zero_page_x():
        test_increment_memory_instruction(instruction=[DEC_ZERO_PAGE_X, 0xf0], address=0x10, value=0xff, increment=-1, 
                                          data={0x10: 0xff}, register_data={'X': 0x20}, num_cycles=6)

    @staticmethod
    def test_dec_absolute():
        test_increment_memory_instruction(instruction=[DEC_ABSOLUTE, 0x0, 0x20], address=0x2000, value=0x1f,
                                          increment=-1, data={0x2000: 0x1f}, num_cycles=6)

    @staticmethod
    def test_dec_absolute_x():
        test_increment_memory_instruction(instruction=[DEC_ABSOLUTE_X, 0x0, 0x20], address=0x2060, value=0x7f,
                                          increment=-1, data={0x2060: 0x7f}, register_data={'X': 0x60}, num_cycles=7)

    @staticmethod
    def test_inx():
        test_increment_register_instruction(instruction=[INX], register='X', value=0xff, increment=1, num_cycles=2, 
                                            register_data={'X': 0xff})

    @staticmethod
    def test_iny():
        test_increment_register_instruction(instruction=[INY], register='Y', value=0x0, increment=1, num_cycles=2, 
                                            register_data={'Y': 0x0})

    @staticmethod
    def test_dex():
        test_increment_register_instruction(instruction=[DEX], register='X', value=0xff, increment=-1, num_cycles=2, 
                                            register_data={'X': 0xff})

    @staticmethod
    def test_dey():
        test_increment_register_instruction(instruction=[DEY], register='Y', value=0x0, increment=-1, num_cycles=2, 
                                            register_data={'Y': 0x0})


if __name__ == '__main__':
    unittest.main()
