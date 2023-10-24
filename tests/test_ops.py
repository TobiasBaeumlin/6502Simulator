import unittest
from emulator.processor import Processor
from emulator.opcodes import *

class ProcessorTest(unittest.TestCase):
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
