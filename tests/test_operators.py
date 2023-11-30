import unittest
from emulator.operators import *

class OperatorTest(unittest.TestCase):
    def test_signed_byte_addition(self):
        assert signed_byte_addition(10, 67) == 77
        assert signed_byte_addition(-10, 67) == 57
        assert signed_byte_addition(-10, -67) == -77
        assert signed_byte_addition(127, 10) == -119  
        assert signed_byte_addition(-128, -1) == 127


    def test_unsigned_byte_addition(self):
        assert unsigned_byte_addition(100,100) == 200
        assert unsigned_byte_addition(255,1) == 0


    def test_unsigned_byte_addition_with_carry(self):
        assert unsigned_byte_addition(100, 100, 1) == 201
        assert unsigned_byte_addition(255, 1, 1) == 1
        assert unsigned_byte_addition(200, 55, 1) == 0
       
      
    def test_signed_byte_subtraction(self):
        assert signed_byte_subtraction(10, 67) == -57
        assert signed_byte_subtraction(-10, 67) == -77
        assert signed_byte_subtraction(-10, -67) == 57
        assert signed_byte_subtraction(127, 10) == 117  
        assert signed_byte_subtraction(-128, 1) == 127


    def test_unsigned_byte_subtraction(self):
        assert unsigned_byte_subtraction(100,100) == 0
        assert unsigned_byte_subtraction(50,100) == 206
        assert unsigned_byte_subtraction(0, 255) == 1


    def test_unsigned_byte_subtraction_with_carry(self):
        assert unsigned_byte_subtraction(100, 100, 1) == 255
        assert unsigned_byte_subtraction(50, 100, 1) == 205
        assert unsigned_byte_subtraction(0, 255, 1) == 0


    def test_addition_overflow(self):
        assert signed_addition_overflow(0x50, 0x10) == False   
        assert signed_addition_overflow(0x50, 0x50) == True   
        assert signed_addition_overflow(0x50, 0x90) == False   
        assert signed_addition_overflow(0x50, 0xd0) == False   
        assert signed_addition_overflow(0xd0, 0x10) == False   
        assert signed_addition_overflow(0xd0, 0x50) == False   
        assert signed_addition_overflow(0xd0, 0x90) == True   
        assert signed_addition_overflow(0xd0, 0xd0) == False   

    def test_subtraction_overflow(self):
        assert signed_subtraction_overflow(0x50, 0xf0) == False   
        assert signed_subtraction_overflow(0x50, 0xb0) == True   
        assert signed_subtraction_overflow(0x50, 0x70) == False   
        assert signed_subtraction_overflow(0x50, 0x30) == False   
        assert signed_subtraction_overflow(0xd0, 0xf0) == False   
        assert signed_subtraction_overflow(0xd0, 0xb0) == False   
        assert signed_subtraction_overflow(0xd0, 0x70) == True   
        assert signed_subtraction_overflow(0xd0, 0x30) == False   

    def test_shift_left(self):
        assert shl(0x5) == (0xa, 0)
        assert shl(0x80) == (0, 1)
        assert shl(0x10, 1) == (0x21, 0)
        assert shl(0xf0, 1) == (0xe1, 1)
    
    def test_shift_right(self):
        assert shr(0x5) == (0x2, 1)
        assert shr(0x80) == (0x40, 0)
        assert shr(0x10, 1) == (0x88, 0)
        assert shr(0x81, 1) == (0xc0, 1)

if __name__ == '__main__':
    unittest.main()
