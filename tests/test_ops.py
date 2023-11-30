import unittest
from emulator.processor import Processor
from emulator.opcodes import *

class ProcessorTest(unittest.TestCase):
    def test_setter_getter(self):
        processor = Processor()
        processor.PC = 0x200
        assert processor.program_counter_low.value == 0x00
        assert processor.program_counter_high.value == 0x02
        processor.A = 0xff
        assert processor.accumulator.value == 0xff
        processor.C = 1
        assert processor.status.value == 0b1
        processor.C = 0
        assert processor.status.value == 0
        processor.Z = 1
        assert processor.status.value == 0b10
        processor.Z = 0
        assert processor.status.value == 0
        processor.I = 1
        assert processor.status.value == 0b100
        processor.I = 0
        assert processor.status.value == 0
        processor.D = 1
        assert processor.status.value == 0b1000
        processor.D = 0
        assert processor.status.value == 0
        processor.B = 1
        assert processor.status.value == 0b10000
        processor.B = 0
        assert processor.status.value == 0
        processor.V = 1
        assert processor.status.value == 0b1000000
        processor.V = 0
        assert processor.status.value == 0
        processor.N = 1
        assert processor.status.value == 0b10000000
        processor.N = 0
        assert processor.status.value == 0         

    def test_put(self):
        processor = Processor()
        processor.put_byte(0xff, 10)
        assert processor.memory.data[0xff] == 10
        assert processor.cycles == 1

    def test_fetch(self):
        processor = Processor()
        processor.memory.data[0x100] = 42
        assert processor.fetch_byte(0x100) == 42
        assert processor.cycles == 1

 
if __name__ == '__main__':
    unittest.main()
