import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *


def test_load_instruction(
        instruction: list[int], register: str, value: int, num_cycles: int,
        data: dict = None, register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)
    processor.run_instruction() # noqa

    assert processor.__getattribute__(register) == value
    assert processor.cycles == num_cycles
    assert processor.N == (value > 127)
    assert processor.Z == (value == 0)
    assert processor.PC == len(instruction)
   

class ProcessorTest(unittest.TestCase):
    @staticmethod
    def test_lda_immediate():
        test_load_instruction(instruction=[LDA_IMMEDIATE, 42], register='A', value=42, num_cycles=2)

    @staticmethod
    def test_lda_zero_page():
        test_load_instruction(instruction=[LDA_ZERO_PAGE, 0x10], register='A', value=138, num_cycles=3,
                              data={0x0010: 138}, register_data={'X': 0x20})

    @staticmethod
    def test_lda_zero_page_x():
        test_load_instruction(instruction=[LDA_ZERO_PAGE_X, 0x10], register='A', value=42, num_cycles=4, 
                              data={0x0030: 42}, register_data={'X': 0x20})

    @staticmethod
    def test_lda_absolute():
        test_load_instruction(instruction=[LDA_ABSOLUTE, 0x10, 0x20], register='A', value=0xf0, num_cycles=4,
                              data={0x2010: 0xf0})

    @staticmethod
    def test_lda_absolute_x_same_page():
        test_load_instruction(instruction=[LDA_ABSOLUTE_X, 0x00, 0x30], register='A', value=0x00, num_cycles=4,
                              data={0x3050: 0xf0}, register_data={'X': 0x40})

    @staticmethod
    def test_lda_absolute_x_cross_page_boundary():
        test_load_instruction(instruction=[LDA_ABSOLUTE_X, 0xf0, 0x30], register='A', value=42, num_cycles=5,
                              data={0x3180: 42}, register_data={'X': 0x90})

    @staticmethod
    def test_lda_absolute_y_same_page():
        test_load_instruction(instruction=[LDA_ABSOLUTE_Y, 0x0a, 0x30], register='A', value=42, num_cycles=4,
                              data={0x309a: 42}, register_data={'Y': 0x90})

    @staticmethod
    def test_lda_absolute_y_cross_page_boundary():
        test_load_instruction(instruction=[LDA_ABSOLUTE_Y, 0xf0, 0x30], register='A', value=42, num_cycles=5,
                              data={0x3180: 42}, register_data={'Y': 0x90})

    @staticmethod
    def test_lda_indirect_x():
        test_load_instruction(instruction=[LDA_INDIRECT_X, 0x20], register='A', value=201, num_cycles=6,
                              data={0x0024: 0x80, 0x0025: 0x31, 0x3180: 201}, register_data={'X': 0x04})

    @staticmethod
    def test_lda_indirect_y_same_page():
        test_load_instruction(instruction=[LDA_INDIRECT_Y, 0x86], register='A', value=201, num_cycles=5,
                              data={0x0086: 0x28, 0x0087: 0x40, 0x4038: 201}, register_data={'Y': 0x10})

    @staticmethod
    def test_lda_indirect_y_cross_page_boundary():
        test_load_instruction(instruction=[LDA_INDIRECT_Y, 0x86], register='A', value=0, num_cycles=6,
                              data={0x0086: 0x28, 0x0087: 0x40, 0x4038: 0}, register_data={'Y': 0xf0})
        
    @staticmethod
    def test_ldx_immediate():
        test_load_instruction(instruction=[LDX_IMMEDIATE, 0xff], register='X', value=0xff, num_cycles=2)

    @staticmethod
    def test_ldx_zero_page():
        test_load_instruction(instruction=[LDX_ZERO_PAGE, 0xaa], register='X', value=138, num_cycles=3, 
                              data={0x00aa: 138}, register_data={'X': 0x20})

    @staticmethod
    def test_ldx_zero_page_y():
        test_load_instruction(instruction=[LDX_ZERO_PAGE_Y, 0xF0], register='X', value=42, num_cycles=4, 
                              data={0x0010: 42}, register_data={'Y': 0x20})

    @staticmethod
    def test_ldx_absolute():
        test_load_instruction(instruction=[LDX_ABSOLUTE, 0x10, 0x20], register='X', value=0xf0, num_cycles=4,
                              data={0x2010: 0xf0})

    @staticmethod
    def test_ldx_absolute_y_same_page():
        test_load_instruction(instruction=[LDX_ABSOLUTE_Y, 0x00, 0x30], register='X', value=0x00, num_cycles=4,
                              data={0x3050: 0xf0}, register_data={'Y': 0x40})

    @staticmethod
    def test_ldx_absolute_y_cross_page_boundary():
        test_load_instruction(instruction=[LDX_ABSOLUTE_Y, 0xf0, 0x30], register='X', value=42, num_cycles=5,
                              data={0x3180: 42}, register_data={'Y': 0x90})


if __name__ == '__main__':
    unittest.main()
