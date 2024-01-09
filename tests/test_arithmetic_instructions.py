import unittest
from emulator.processor import setup_processor
from emulator.operators import signed_addition_overflow, signed_subtraction_overflow
from emulator.opcodes import *


def test_adc_instruction(instruction: list[int], result: int, summand: int, num_cycles: int,
                         data: dict = None, register_data: dict = None, carry: int = 0) -> None:
    processor = setup_processor(instruction, data, register_data, flags={'C': carry})

    a = processor.A
    b = summand
    c = int(processor.C)

    processor.run_instruction()

    assert processor.A == result
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.C == (a + b + c > 255)
    assert processor.V == signed_addition_overflow(a, b + c)
    assert processor.PC == len(instruction)


def test_sbc_instruction(instruction: list[int], result: int, subtrahend: int, num_cycles: int, data: dict = None,
                         register_data: dict = None, carry: int = 0) -> None:
    processor = setup_processor(instruction, data, register_data, flags={'C': carry})

    a = processor.A
    b = subtrahend
    c = 1 - processor.C

    processor.run_instruction()

    assert processor.A == result
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.C == (a - b - c < 0)
    assert processor.V == signed_subtraction_overflow(a, b + c)
    assert processor.PC == len(instruction)


class ProcessorTest(unittest.TestCase):
    # Addition
    @staticmethod
    def test_adc_immediate():
        test_adc_instruction(instruction=[ADC_IMMEDIATE, 0xf0], register_data={'A': 0x0f}, result=0x0,
                             summand=0xf0, num_cycles=2, carry=1)

    @staticmethod
    def test_adc_zero_page():
        test_adc_instruction(instruction=[ADC_ZERO_PAGE, 0x0a], register_data={'A': 0xf0}, data={0x0a: 0x20},
                             result=0x10, summand=0x20, num_cycles=3)

    @staticmethod
    def test_adc_zero_page_x():
        test_adc_instruction(instruction=[ADC_ZERO_PAGE_X, 0x0a], register_data={'A': 0xf0, 'X': 0xf0},
                             data={0xfa: 0x20},
                             result=0x10, summand=0x20, num_cycles=4)

    @staticmethod
    def test_adc_absolute():
        test_adc_instruction(instruction=[ADC_ABSOLUTE, 0x0a, 0x20], register_data={'A': 0xf0}, data={0x200a: 0x10},
                             result=0x0, summand=0x10, num_cycles=4)

    @staticmethod
    def test_adc_absolute_x_same_page():
        test_adc_instruction(instruction=[ADC_ABSOLUTE_X, 0x0a, 0x20], register_data={'A': 0xf0, 'X': 0x01},
                             data={0x200b: 0x10},
                             result=0x0, summand=0x10, num_cycles=4)

    @staticmethod
    def test_adc_absolute_x_cross_page_boundary():
        test_adc_instruction(instruction=[ADC_ABSOLUTE_X, 0x10, 0x20], register_data={'A': 0x01, 'X': 0xf0},
                             data={0x2100: 0x01},
                             result=0x03, summand=0x10, num_cycles=5, carry=1)

    @staticmethod
    def test_adc_absolute_y_same_page():
        test_adc_instruction(instruction=[ADC_ABSOLUTE_Y, 0x0a, 0x20], register_data={'A': 0xf0, 'Y': 0x01},
                             data={0x200b: 0x10},
                             result=0x0, summand=0x10, num_cycles=4)

    @staticmethod
    def test_adc_absolute_y_cross_page_boundary():
        test_adc_instruction(instruction=[ADC_ABSOLUTE_Y, 0x10, 0x20], register_data={'A': 0x01, 'Y': 0xf0},
                             data={0x2100: 0x01},
                             result=0x03, summand=0x10, num_cycles=5, carry=1)

    @staticmethod
    def test_adc_indirect_x():
        test_adc_instruction(instruction=[ADC_INDIRECT_X, 0x40], register_data={'A': 0x01, 'X': 0xf0},
                             data={0x30: 0x00, 0x31: 0x21, 0x2100: 0x01},
                             result=0x03, summand=0x10, num_cycles=6, carry=1)

    @staticmethod
    def test_adc_indirect_y_same_page():
        test_adc_instruction(instruction=[ADC_INDIRECT_Y, 0x30], register_data={'A': 0xff, 'Y': 0xf0},
                             data={0x30: 0x00, 0x31: 0x21, 0x21f0: 0x01},
                             result=0x00, summand=0x10, num_cycles=5)

    # Subtraction
    @staticmethod
    def test_sbc_immediate():
        test_sbc_instruction(instruction=[SBC_IMMEDIATE, 0x0f], register_data={'A': 0x0f}, result=0xff,
                             subtrahend=0x0f, num_cycles=2, carry=0)

    @staticmethod
    def test_sbc_zero_page():
        test_sbc_instruction(instruction=[SBC_ZERO_PAGE, 0x0a], register_data={'A': 0xf0}, data={0x0a: 0x20},
                             result=0xd0, subtrahend=0x20, num_cycles=3, carry=1)

    @staticmethod
    def test_sbc_zero_page_x():
        test_sbc_instruction(instruction=[SBC_ZERO_PAGE_X, 0x0a], register_data={'A': 0xf0, 'X': 0xf0},
                             data={0xfa: 0x20},
                             result=0xcf, subtrahend=0x20, num_cycles=4, carry=0)

    @staticmethod
    def test_sbc_absolute():
        test_sbc_instruction(instruction=[SBC_ABSOLUTE, 0x0a, 0x20], register_data={'A': 0xf0}, data={0x200a: 0xf0},
                             result=0x0, subtrahend=0xf0, num_cycles=4, carry=1)

    @staticmethod
    def test_sbc_absolute_x_same_page():
        test_sbc_instruction(instruction=[SBC_ABSOLUTE_X, 0x0a, 0x20], register_data={'A': 0xf0, 'X': 0x01},
                             data={0x200b: 0xf0},
                             result=0xff, subtrahend=0xf0, num_cycles=4, carry=0)

    @staticmethod
    def test_sbc_absolute_x_cross_page_boundary():
        test_sbc_instruction(instruction=[SBC_ABSOLUTE_X, 0x10, 0x20], register_data={'A': 0x01, 'X': 0xf0},
                             data={0x2100: 0x01},
                             result=0x0, subtrahend=0x01, num_cycles=5, carry=1)

    @staticmethod
    def test_sbc_absolute_y_same_page():
        test_sbc_instruction(instruction=[SBC_ABSOLUTE_Y, 0x0a, 0x20], register_data={'A': 0xf0, 'Y': 0x01},
                             data={0x200b: 0x10},
                             result=0xdf, subtrahend=0x10, num_cycles=4, carry=0)

    @staticmethod
    def test_sbc_absolute_y_cross_page_boundary():
        test_sbc_instruction(instruction=[SBC_ABSOLUTE_Y, 0x10, 0x20], register_data={'A': 0xa1, 'Y': 0xf0},
                             data={0x2100: 0x01},
                             result=0xa0, subtrahend=0x01, num_cycles=5, carry=1)

    @staticmethod
    def test_sbc_indirect_x():
        test_sbc_instruction(instruction=[SBC_INDIRECT_X, 0x40], register_data={'A': 0x01, 'X': 0xf0},
                             data={0x30: 0x00, 0x31: 0x21, 0x2100: 0x01},
                             result=0x0, subtrahend=0x01, num_cycles=6, carry=1)

    @staticmethod
    def test_sbc_indirect_y_same_page():
        test_sbc_instruction(instruction=[SBC_INDIRECT_Y, 0x30], register_data={'A': 0xff, 'Y': 0xf0},
                             data={0x30: 0x00, 0x31: 0x21, 0x21f0: 0x01},
                             result=0xfd, subtrahend=0x01, num_cycles=5, carry=0)


if __name__ == '__main__':
    unittest.main()
