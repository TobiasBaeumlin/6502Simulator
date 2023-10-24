def signed_byte_addition(a: int, b:int) -> int:
    assert -128<=a<=127, -128<=b<=127
    sum = a + b
    if sum > 127:
        return sum - 256
    if sum < -128:
        return sum + 256
    return sum


def signed_byte_subtraction(a:int, b:int) -> int:
    assert -128<=a<=127, -128<=b<=127
    return signed_byte_addition(a, -b)
 

def unsigned_byte_addition(a: int, b:int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    sum = a + b + carry_in
    if sum > 255:
        return sum - 256
    return sum


def unsigned_byte_subtraction(a: int, b:int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    difference = a - b - carry_in
    if difference < 0:
        return difference + 256
    return difference


# Calculate overflow bit (as described in http://www.righto.com/2012/12/the-6502-overflow-flag-explained.html)
def signed_addition_overflow(a: int, b: int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    result = a + b + carry_in
    return ((a^result) & (b^result) & 0x80) >> 7 


def signed_subtraction_overflow(a: int, b: int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    return signed_addition_overflow(a, ~b, carry_in)


def unsigned_addition_carry(a: int, b: int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    result = a + b + carry_in
    return int(result > 0xff)   


def unsigned_subtraction_carry(a: int, b:int, carry_in:int=0) -> int:
    assert 0<=a<=255, 0<=b<=255
    result = a - b - carry_in
    return int(result < 0)

# Shifting and rotating

def shift_left(byte: int, bit_in:int=0):
    assert 0x0<=byte<=0xff, 0<=bit_in<=1
    result = (byte << 1) | bit_in
    return  result & 0xFF, (byte&0x80) >> 7

def shift_right(byte: int, bit_in:int=0):
    assert 0x0<=byte<=0xff, 0<=bit_in<=1
    result = (byte >> 1) | (bit_in << 7)
    return  result, byte & 1
