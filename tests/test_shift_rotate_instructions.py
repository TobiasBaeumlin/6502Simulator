import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *


def test_shift_memory_instruction(instruction: list[int], address: int, value: int, left: bool, num_cycles: int = 0,
                                  data: dict = None, register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)
    pc = processor.PC
    if left:
        result = (value << 1) % 0x100
        carry = bool((value & 0x80) >> 7)
    else:
        result = (value >> 1) % 0x100
        carry = bool(value & 1)

    processor.run_instruction()  # noqa

    assert processor.memory.data[address] == result
    assert processor.C == carry
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == pc + len(instruction)


def test_shift_accumulator_instruction(instruction: list[int], left: bool, num_cycles: int = 0, data: dict = None,
                                       register_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data)

    pc = processor.PC
    if left:
        result = (processor.A << 1) % 0x100
        carry = bool((processor.A & 0x80) >> 7)
    else:
        result = (processor.A >> 1) % 0x100
        carry = bool(processor.A & 1)

    processor.run_instruction()  # noqa

    assert processor.A == result
    assert processor.C == carry
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == pc + len(instruction)


def test_rotate_memory_instruction(instruction: list[int], address: int, value: int, left: bool, num_cycles: int = 0,
                                   data: dict = None, register_data: dict = None, flags_data: dict = None) -> None:
    processor = setup_processor(instruction=instruction, data=data, registers=register_data, flags=flags_data)

    pc = processor.PC
    if left:
        result = ((value << 1) | int(processor.C)) % 0x100
        carry = bool(value & 0x80)
    else:
        result = ((value >> 1) | int(processor.C) << 7) % 0x100
        carry = bool(value & 1)

    processor.run_instruction() # noqa

    assert processor.memory.data[address] == result
    assert processor.C == carry
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == pc + len(instruction)


def test_rotate_accumulator_instruction(instruction: list[int], left: bool, num_cycles: int = 0, data: dict = None,
                                        register_data: dict = None, flags_data: dict = None) -> None:
    processor = setup_processor(instruction, data, register_data, flags=flags_data)

    pc = processor.PC
    if left:
        result = ((processor.A << 1) | int(processor.C)) % 0x100
        carry = bool((processor.A & 0x80) >> 7)
    else:
        result = ((processor.A >> 1) | int(processor.C) << 7) % 0x100
        carry = bool(processor.A & 1)

    processor.run_instruction()  # noqa

    assert processor.A == result
    assert processor.C == carry
    assert processor.cycles == num_cycles
    assert processor.N == (result > 127)
    assert processor.Z == (result == 0)
    assert processor.PC == pc + len(instruction)


class ProcessorTest(unittest.TestCase):
    # Shift accumulator
    @staticmethod
    def test_shift_accumulator_left():
        test_shift_accumulator_instruction([ASL_ACCUMULATOR], left=True, num_cycles=2, register_data={'A': 0b11000001})

    @staticmethod
    def test_shift_accumulator_right():
        test_shift_accumulator_instruction([LSR_ACCUMULATOR], left=False, num_cycles=2, register_data={'A': 0b11111111})
        # Shift memory

    @staticmethod
    def test_shift_memory_left_zero_page():
        test_shift_memory_instruction([ASL_ZERO_PAGE, 0x80], address=0x80, value=0b11000001, left=True, num_cycles=5,
                                      data={0x80: 0b11000001})

    @staticmethod
    def test_shift_memory_left_zero_page_x():
        test_shift_memory_instruction([ASL_ZERO_PAGE_X, 0x0], address=0x10, value=0b00010001, left=True, num_cycles=6,
                                      data={0x10: 0b00010001}, register_data={'X': 0x10})

    @staticmethod
    def test_shift_memory_left_absolute():
        test_shift_memory_instruction([ASL_ABSOLUTE, 0x0, 0xa0], address=0xa000, value=0b11000001, left=True,
                                      num_cycles=6,
                                      data={0xa000: 0b11000001})

    @staticmethod
    def test_shift_memory_left_absolute_x():
        test_shift_memory_instruction([ASL_ABSOLUTE_X, 0x0, 0xa], address=0x0a10, value=0b00010001, left=True,
                                      num_cycles=7,
                                      data={0x0a10: 0b00010001}, register_data={'X': 0x10})

    @staticmethod
    def test_shift_memory_right_zero_page():
        test_shift_memory_instruction([LSR_ZERO_PAGE, 0xff], address=0xff, value=0b11111111, left=False, num_cycles=5,
                                      data={0xff: 0b11111111})

    @staticmethod
    def test_shift_memory_right_zero_page_x():
        test_shift_memory_instruction([LSR_ZERO_PAGE_X, 0x0], address=0x10, value=0b00010001, left=False, num_cycles=6,
                                      data={0x10: 0b00010001}, register_data={'X': 0x10})

    @staticmethod
    def test_shift_memory_right_absolute():
        test_shift_memory_instruction([LSR_ABSOLUTE, 0x0, 0xa0], address=0xa000, value=0b11000001, left=False,
                                      num_cycles=6,
                                      data={0xa000: 0b11000001})

    @staticmethod
    def test_shift_memory_right_absolute_x():
        test_shift_memory_instruction([LSR_ABSOLUTE_X, 0x0, 0xa], address=0x0a10, value=0b00010001, left=False,
                                      num_cycles=7,
                                      data={0x0a10: 0b00010001}, register_data={'X': 0x10})

        # Rotate accumulator

    @staticmethod
    def test_rotate_accumulator_left():
        test_rotate_accumulator_instruction([ROL_ACCUMULATOR], left=True, num_cycles=2, register_data={'A': 0b10000000},
                                            flags_data={'C': 1})

    @staticmethod
    def test_rotate_accumulator_right():
        test_rotate_accumulator_instruction([ROR_ACCUMULATOR], left=False, num_cycles=2,
                                            register_data={'A': 0b00010000}, flags_data={'C': 1})

    # Rotate memory

    @staticmethod
    def test_rotate_memory_left_zero_page():
        test_rotate_memory_instruction([ROL_ZERO_PAGE, 0xf], address=0xf, value=0b11000001, left=True, num_cycles=5,
                                       data={0xf: 0b11000001}, flags_data={'C': True})

    @staticmethod
    def test_rotate_memory_left_zero_page_x():
        test_rotate_memory_instruction([ROL_ZERO_PAGE_X, 0x0], address=0x10, value=0b00010001, left=True, num_cycles=6,
                                       data={0x10: 0b00010001}, register_data={'X': 0x10}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_left_absolute():
        test_rotate_memory_instruction([ROL_ABSOLUTE, 0x0, 0xa0], address=0xa000, value=0b11000001, left=True,
                                       num_cycles=6,
                                       data={0xa000: 0b11000001}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_left_absolute_x():
        test_rotate_memory_instruction([ROL_ABSOLUTE_X, 0x0, 0xa], address=0x0a10, value=0b00010001, left=True,
                                       num_cycles=7,
                                       data={0x0a10: 0b00010001}, register_data={'X': 0x10}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_right_zero_page():
        test_rotate_memory_instruction([ROR_ZERO_PAGE, 0xff], address=0xff, value=0b11111111, left=False, num_cycles=5,
                                       data={0xff: 0b11111111}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_right_zero_page_x():
        test_rotate_memory_instruction([ROR_ZERO_PAGE_X, 0x0], address=0x10, value=0b00010001, left=False, num_cycles=6,
                                       data={0x10: 0b00010001}, register_data={'X': 0x10}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_right_absolute():
        test_rotate_memory_instruction([ROR_ABSOLUTE, 0x0, 0xa0], address=0xa000, value=0b11000001, left=False,
                                       num_cycles=6,
                                       data={0xa000: 0b11000001}, flags_data={'C': 1})

    @staticmethod
    def test_rotate_memory_right_absolute_x():
        test_rotate_memory_instruction([ROR_ABSOLUTE_X, 0x0, 0xa], address=0x0a10, value=0b00010001, left=False,
                                       num_cycles=7,
                                       data={0x0a10: 0b00010001}, register_data={'X': 0x10}, flags_data={'C': 1})


if __name__ == '__main__':
    unittest.main()
