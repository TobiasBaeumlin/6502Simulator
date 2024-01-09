import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *


def test_compare_instruction(instruction: list[int], n: int, z: int, c: int, num_cycles: int, data: dict = None,
                             register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)

    processor.run_instruction()

    assert processor.cycles == num_cycles
    assert processor.N == n
    assert processor.Z == z
    assert processor.C == c


class ProcessorTest(unittest.TestCase):
    # compare accumulator immediate
    @staticmethod
    def test_compare_accumulator_immediate_detects_equal():
        test_compare_instruction(instruction=[CMP_IMMEDIATE, 0xf0], register_data={'A': 0xf0}, n=0, z=1, c=1,
                                 num_cycles=2)

    @staticmethod
    def test_compare_accumulator_immediate_detects_register_smaller():
        test_compare_instruction(instruction=[CMP_IMMEDIATE, 0xf0], register_data={'A': 0xd0}, n=1, z=0, c=0,
                                 num_cycles=2)

    @staticmethod
    def test_compare_accumulator_immediate_detects_register_greater():
        test_compare_instruction(instruction=[CMP_IMMEDIATE, 0x1], register_data={'A': 0xd0}, n=1, z=0, c=1,
                                 num_cycles=2)

    # Remaining tests only test address modes and number of cycles
    # compare accumulator zero page
    @staticmethod
    def test_compare_accumulator_zero_page():
        test_compare_instruction(instruction=[CMP_ZERO_PAGE, 0x42], register_data={'A': 0xf0}, data={0x42: 0xf0}, n=0,
                                 z=1, c=1,
                                 num_cycles=3)

    # compare accumulator zero page with offset x
    @staticmethod
    def test_compare_accumulator_zero_page_x():
        test_compare_instruction(instruction=[CMP_ZERO_PAGE_X, 0x40], register_data={'A': 0xf0, 'X': 0x02},
                                 data={0x42: 0xf0}, n=0, z=1, c=1,
                                 num_cycles=4)

    # compare accumulator absolute
    @staticmethod
    def test_compare_accumulator_absolute():
        test_compare_instruction(instruction=[CMP_ABSOLUTE, 0x42, 0x20], register_data={'A': 0xf0}, data={0x2042: 0xf0},
                                 n=0, z=1, c=1,
                                 num_cycles=4)

    # compare accumulator absolute with offset x
    @staticmethod
    def test_compare_accumulator_absolute_x():
        test_compare_instruction(instruction=[CMP_ABSOLUTE_X, 0x40, 0x20], register_data={'A': 0xf0, 'X': 0x02},
                                 data={0x2042: 0xf0}, n=0, z=1, c=1,
                                 num_cycles=4)

    # compare accumulator absolute with offset y
    @staticmethod
    def test_compare_accumulator_absolute_y():
        test_compare_instruction(instruction=[CMP_ABSOLUTE_Y, 0x40, 0x20], register_data={'A': 0xf0, 'Y': 0x02},
                                 data={0x2042: 0xf0}, n=0, z=1, c=1,
                                 num_cycles=4)

    # compare accumulator indexed indirect x
    @staticmethod
    def test_compare_accumulator_indirect_x():
        test_compare_instruction(instruction=[CMP_INDIRECT_X, 0x20], register_data={'A': 0xf0, 'X': 0x10},
                                 data={0x30: 0x40, 0x31: 0x20, 0x2040: 0xf0}, n=0, z=1, c=1,
                                 num_cycles=6)

    # compare accumulator indexed indirect y
    @staticmethod
    def test_compare_accumulator_indirect_y_same_page():
        test_compare_instruction(instruction=[CMP_INDIRECT_Y, 0x40], register_data={'A': 0xf0, 'Y': 0x10},
                                 data={0x40: 0xa0, 0x41: 0x20, 0x20b0: 0xf0}, n=0, z=1, c=1,
                                 num_cycles=5)

    # compare x register
    @staticmethod
    def test_compare_register_x_immediate():
        test_compare_instruction(instruction=[CPX_IMMEDIATE, 0xf0], register_data={'X': 0xf0}, n=0, z=1, c=1,
                                 num_cycles=2)

    @staticmethod
    def test_compare_register_x_zero_page():
        test_compare_instruction(instruction=[CPX_ZERO_PAGE, 0x40], register_data={'X': 0xf0}, data={0x40: 0xf0}, n=0,
                                 z=1, c=1,
                                 num_cycles=3)

    @staticmethod
    def test_compare_register_x_absolute():
        test_compare_instruction(instruction=[CPX_ABSOLUTE, 0x42, 0x20], register_data={'X': 0xf0}, data={0x2042: 0xf0},
                                 n=0, z=1, c=1,
                                 num_cycles=4)

    # compare y register
    @staticmethod
    def test_compare_register_y_immediate():
        test_compare_instruction(instruction=[CPY_IMMEDIATE, 0xf0], register_data={'Y': 0xf0}, n=0, z=1, c=1,
                                 num_cycles=2)

    @staticmethod
    def test_compare_register_y_zero_page():
        test_compare_instruction(instruction=[CPY_ZERO_PAGE, 0x40], register_data={'Y': 0xf0}, data={0x40: 0xf0}, n=0,
                                 z=1, c=1,
                                 num_cycles=3)

    @staticmethod
    def test_compare_register_y_absolute():
        test_compare_instruction(instruction=[CPY_ABSOLUTE, 0x42, 0x20], register_data={'Y': 0xf0}, data={0x2042: 0xf0},
                                 n=0, z=1, c=1,
                                 num_cycles=4)


if __name__ == '__main__':
    unittest.main()
