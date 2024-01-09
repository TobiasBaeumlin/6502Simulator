import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *

START_ADDR = 0x00


def test_store_instruction(
        instruction: list[int], destination: int, value: int, num_cycles: int,
        data: dict = None, register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)
    processor.run_instruction()

    assert processor.memory.data[destination] == value
    assert processor.cycles == num_cycles
    assert processor.PC == START_ADDR + len(instruction)


class ProcessorTest(unittest.TestCase):
    @staticmethod
    def test_sta_zero_page():
        test_store_instruction(instruction=[STA_ZERO_PAGE, 0xff], destination=0xff, value=0x42, num_cycles=3,
                               register_data={'A': 0x42})

    @staticmethod
    def test_sta_zero_page_x():
        test_store_instruction(instruction=[STA_ZERO_PAGE_X, 0xf0], destination=0x10, value=0x42, num_cycles=4,
                               register_data={'A': 0x42, 'X': 0x20})

    @staticmethod
    def test_sta_absolute():
        test_store_instruction(instruction=[STA_ABSOLUTE, 0xf0, 0x10], destination=0x10f0, value=0x42, num_cycles=4,
                               register_data={'A': 0x42})

    @staticmethod
    def test_sta_absolute_x():
        test_store_instruction(instruction=[STA_ABSOLUTE_X, 0xf0, 0x10], destination=0x10f1, value=0x42, num_cycles=5,
                               register_data={'A': 0x42, 'X': 0x01})

    @staticmethod
    def test_sta_absolute_y():
        test_store_instruction(instruction=[STA_ABSOLUTE_Y, 0xf0, 0x10], destination=0x10fa, value=0x42, num_cycles=5,
                               register_data={'A': 0x42, 'Y': 0x0a})

    @staticmethod
    def test_sta_indirect_x():
        test_store_instruction(instruction=[STA_INDIRECT_X, 0x70], destination=0x3032, value=0x42, num_cycles=6,
                               data={0x75: 0x32, 0x76: 0x30}, register_data={'A': 0x42, 'X': 0x05})

    @staticmethod
    def test_sta_indirect_y():
        test_store_instruction(instruction=[STA_INDIRECT_Y, 0xf0], destination=0x110a, value=0x42, num_cycles=6,
                               data={0xf0: 0xfa, 0xf1: 0x10}, register_data={'A': 0x42, 'Y': 0x10})

    @staticmethod
    def test_stx_zero_page():
        test_store_instruction(instruction=[STX_ZERO_PAGE, 0xf0], destination=0xf0, value=0x42, num_cycles=3,
                               register_data={'X': 0x42})

    @staticmethod
    def test_stx_zero_page_y():
        test_store_instruction(instruction=[STX_ZERO_PAGE_Y, 0x30], destination=0x50, value=0x42, num_cycles=4,
                               register_data={'X': 0x42, 'Y': 0x20})

    @staticmethod
    def test_stx_absolute():
        test_store_instruction(instruction=[STX_ABSOLUTE, 0xaa, 0xd0], destination=0xd0aa, value=0x42, num_cycles=4,
                               register_data={'X': 0x42})

    @staticmethod
    def test_sty_zero_page():
        test_store_instruction(instruction=[STY_ZERO_PAGE, 0x00], destination=0x00, value=0x42, num_cycles=3,
                               register_data={'Y': 0x42})

    @staticmethod
    def test_sty_zero_page_x():
        test_store_instruction(instruction=[STY_ZERO_PAGE_X, 0xe0], destination=0x50, value=0x42, num_cycles=4,
                               register_data={'Y': 0x42, 'X': 0x70})

    @staticmethod
    def test_sty_absolute():
        test_store_instruction(instruction=[STY_ABSOLUTE, 0xaa, 0xd0], destination=0xd0aa, value=0x42, num_cycles=4,
                               register_data={'Y': 0x42})


if __name__ == '__main__':
    unittest.main()
