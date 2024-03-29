#     6502Simulator, a didactic visual simulator of the 6502 processor
#     Copyright (C) 2024  Tobias Bäumlin
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Add with carry
ADC_IMMEDIATE = 0x69
ADC_ZERO_PAGE = 0x65
ADC_ZERO_PAGE_X = 0x75
ADC_ABSOLUTE = 0x6D
ADC_ABSOLUTE_X = 0x7D
ADC_ABSOLUTE_Y = 0x79
ADC_INDIRECT_X = 0x61
ADC_INDIRECT_Y = 0x71
# Logical AND
AND_IMMEDIATE = 0x29
AND_ZERO_PAGE = 0x25
AND_ZERO_PAGE_X = 0x35
AND_ABSOLUTE = 0x2D
AND_ABSOLUTE_X = 0x3D
AND_ABSOLUTE_Y = 0x39
AND_INDIRECT_X = 0x21
AND_INDIRECT_Y = 0x31
# Arithmetic shift left
ASL_ACCUMULATOR = 0x0A
ASL_ZERO_PAGE = 0x06
ASL_ZERO_PAGE_X = 0x16
ASL_ABSOLUTE = 0x0E
ASL_ABSOLUTE_X = 0x1E
# Branch if carry clear
BCC = 0x90
# Branch if carry set
BCS = 0xB0
# Branch if equal
BEQ = 0xF0
# Bit test
BIT_ZERO_PAGE = 0x24
BIT_ABSOLUTE = 0x2C
# Branch if minus
BMI = 0x30
# Branch if not equal
BNE = 0xD0
# Branch if positive
BPL = 0x10
# Break, force interrupt
BRK = 0x00
# Branch if overflow clear
BVC = 0x50
# Branch if overflow set
BVS = 0x70
# Clear carry flag
CLC = 0x18
# Clear decimal mode
CLD = 0xD8
# Clear interrupt disable
CLI = 0x58
# Clear overflow flag
CLV = 0xB8
# Compare accumulator
CMP_IMMEDIATE = 0xC9
CMP_ZERO_PAGE = 0xC5
CMP_ZERO_PAGE_X = 0xD5
CMP_ABSOLUTE = 0xCD
CMP_ABSOLUTE_X = 0xDD
CMP_ABSOLUTE_Y = 0xD9
CMP_INDIRECT_X = 0xC1
CMP_INDIRECT_Y = 0xD1
# Compare X register
CPX_IMMEDIATE = 0xE0
CPX_ZERO_PAGE = 0xE4
CPX_ABSOLUTE = 0xEC
# Compare Y register
CPY_IMMEDIATE = 0xC0
CPY_ZERO_PAGE = 0xC4
CPY_ABSOLUTE = 0xCC
# Decrement memory
DEC_ZERO_PAGE = 0xC6
DEC_ZERO_PAGE_X = 0xD6
DEC_ABSOLUTE = 0xCE
DEC_ABSOLUTE_X = 0xDE
# Decrement registers
DEX = 0xCA
DEY = 0x88
# Logical exclusive OR
EOR_IMMEDIATE = 0x49
EOR_ZERO_PAGE = 0x45
EOR_ZERO_PAGE_X = 0x55
EOR_ABSOLUTE = 0x4D
EOR_ABSOLUTE_X = 0x5D
EOR_ABSOLUTE_Y = 0x59
EOR_INDIRECT_X = 0x41
EOR_INDIRECT_Y = 0x51
# Increment memory
INC_ZERO_PAGE = 0xE6
INC_ZERO_PAGE_X = 0xF6
INC_ABSOLUTE = 0xEE
INC_ABSOLUTE_X = 0xFE
# Decrement registers
INX = 0xE8
INY = 0xC8
# Jump to address location
JMP_ABSOLUTE = 0x4C
JMP_INDIRECT = 0x6C
# Jump to subroutine
JSR = 0x20
# Load register from memory instructions
# Register A
LDA_IMMEDIATE = 0xA9
LDA_ZERO_PAGE = 0xA5
LDA_ZERO_PAGE_X = 0xB5
LDA_ABSOLUTE = 0xAD
LDA_ABSOLUTE_X = 0xBD
LDA_ABSOLUTE_Y = 0xB9
LDA_INDIRECT_X = 0xA1
LDA_INDIRECT_Y = 0xB1
# Register X
LDX_IMMEDIATE = 0xA2
LDX_ZERO_PAGE = 0xA6
LDX_ZERO_PAGE_Y = 0xB6
LDX_ABSOLUTE = 0xAE
LDX_ABSOLUTE_Y = 0xBE
# Register Y
LDY_IMMEDIATE = 0xA0
LDY_ZERO_PAGE = 0xA4
LDY_ZERO_PAGE_X = 0xB4
LDY_ABSOLUTE = 0xAC
LDY_ABSOLUTE_X = 0xBC
# Logical shift right
LSR_ACCUMULATOR = 0x4A
LSR_ZERO_PAGE = 0x46
LSR_ZERO_PAGE_X = 0x56
LSR_ABSOLUTE = 0x4E
LSR_ABSOLUTE_X = 0x5E
# No operation
NOP = 0xEA
# Logical inclusive OR
ORA_IMMEDIATE = 0x09
ORA_ZERO_PAGE = 0x05
ORA_ZERO_PAGE_X = 0x15
ORA_ABSOLUTE = 0x0D
ORA_ABSOLUTE_X = 0x1D
ORA_ABSOLUTE_Y = 0x19
ORA_INDIRECT_X = 0x01
ORA_INDIRECT_Y = 0x11
# Push
# Accumulator
PHA = 0x48
# processor status
PHP = 0x08
# Pull
# accumulator
PLA = 0x68
# processor status
PLP = 0x28
# Rotate left
ROL_ACCUMULATOR = 0x2A
ROL_ZERO_PAGE = 0x26
ROL_ZERO_PAGE_X = 0x36
ROL_ABSOLUTE = 0x2E
ROL_ABSOLUTE_X = 0x3E
# Rotate right
ROR_ACCUMULATOR = 0x6A
ROR_ZERO_PAGE = 0x66
ROR_ZERO_PAGE_X = 0x76
ROR_ABSOLUTE = 0x6E
ROR_ABSOLUTE_X = 0x7E
# Return from interrupt
RTI = 0x40
# Return from subroutine
RTS = 0x60
# Subtract with carry
SBC_IMMEDIATE = 0xE9
SBC_ZERO_PAGE = 0xE5
SBC_ZERO_PAGE_X = 0xF5
SBC_ABSOLUTE = 0xED
SBC_ABSOLUTE_X = 0xFD
SBC_ABSOLUTE_Y = 0xF9
SBC_INDIRECT_X = 0xE1
SBC_INDIRECT_Y = 0xF1
# Set carry flag
SEC = 0x38
# Set decimal mode
SED = 0xF8
# Set interrupt disable
SEI = 0x78
# Store register in memory instructions
# Register A
STA_ZERO_PAGE = 0x85
STA_ZERO_PAGE_X = 0x95
STA_ABSOLUTE = 0x8D
STA_ABSOLUTE_X = 0x9D
STA_ABSOLUTE_Y = 0x99
STA_INDIRECT_X = 0x81
STA_INDIRECT_Y = 0x91
# Register X
STX_ZERO_PAGE = 0x86
STX_ZERO_PAGE_Y = 0x96
STX_ABSOLUTE = 0x8E
# Register Y
STY_ZERO_PAGE = 0x84
STY_ZERO_PAGE_X = 0x94
STY_ABSOLUTE = 0x8C
# Register transfer instructions
TAX = 0xAA
TAY = 0xA8
TSX = 0xBA
TXA = 0x8A
TXS = 0x9A
TYA = 0x98
