## Add with carry
ADC = ('add_with_carry',)            
## Logical and
AND = ('and',)              
## Arithmetic shift left
ASL = ('shift_accumulator', True) 
## Branch if carry clear
BCC = ('branch', 'C', False)
## Branch if carry set
BCS = ('branch', 'C', True)
## Branch if equal
BEQ = ('branch', 'Z', True)
## Bit test
BIT = ('bit_test',)    
## Branch if minus
BMI = ('branch', 'N', True)
## Branch if not equal
BNE = ('branch', 'Z', False)
## Branch if positive
BPL = ('branch', 'N', False)
## Break, force interrupt
BRK = ('break', )
## Branch if overflow clear
BVC = ('branch', 'V', False)
## Branch if overflow set
BVS = ('branch', 'V', True)
## Clear carry flag
CLC = ('set_flag', 'C', False)
## Clear decimal mode
CLD = ('set_flag', 'D', False)
## Clear interrupt disable
CLI = ('set_flag', 'I', False)
## Clear overflow flag
CLV = ('set_flag', 'V', False)
## Compare accumulator
CMP = ('compare', 'A')           
## Compare X register
CPX = ('compare', 'X') 
## Compare Y register
CPY = ('compare', 'Y')
## Decrement memory
DEC = ('increment', -1)
## Decrement registers
DEX = ('increment_register', -1, 'X')
DEY = ('increment_register', -1, 'Y')
## Logical exclusive OR
EOR = ('logical_operation', 'xor')
## Increment memory
INC = ('increment', 1)         
## Decrement registers
INX = ('increment_register', 1, 'X')
INY = ('increment_register', 1, 'Y')
## Jump to address location
JMP = ('jump', )
## Jump to subroutine
JSR = ('jump_to_subroutine', )
## Load register from memory instructions
# Register A
LDA = ('load_register', 'A')
# Register X
LDX = ('load_register', 'X')
# Register Y
LDY = ('load_register', 'Y')
## Logical shift right
LSR = ('shift_accumulator', False)
## No operation
NOP = ('no_operation')
## Logical inclusive OR
ORA = ('logical_operation', 'or_')
## Push to stack
# Accumulator
PHA = ('push_register', 'A')
# processor status
PHP = ('push_processor_status')
## Pull
# accumulator
PLA = ('pull_register', 'A')
# processor status
PLP = ('pull_processor_status')
## Rotate left
ROL = ('rotate', True)
## Rotate right
ROR = ('rotate', False)
## Return from interrupt
RTI = ('return_from_interrupt', )
## Return from subroutine
RTS = ('return_from_subroutine', )
## Subtract with carry
SBC = ('subtract_with_carry', )
## Set carry flag
SEC = ('set_flag', 'C', True)
## Set decimal mode
SED = ('set_flag', 'D', True)
## Set interrupt disable
SEI = ('set_flag', 'I', True)
## Store register in memory instructions
# Register A
STA = ('store_register', 'A')
# Register X
STX = ('store_register', 'X')
# Register Y
STY = ('store_register', 'Y')
## Register transfer instructions
TAX = ('transfer_register', 'A', 'X')
TAY = ('transfer_register', 'A', 'Y')
TSX = ('transfer_register', 'S', 'X')
TXA = ('transfer_register', 'X', 'A')
TXS = ('transfer_register', 'X', 'S')
TYA = ('transfer_register', 'Y', 'A')

INSTRUCTION_SET =\
                   {0: 
                        {
                            0: {0: BRK,         2: PHP,         4: BPL,         6: CLC         },
                            1: {0: JSR, 1: BIT, 2: PLP, 3: BIT, 4: BMI,         6: SEC         },
                            2: {0: RTI,         2: PHA, 3: JMP, 4: BVC,         6: CLI         },
                            3: {0: RTS,         2: PLA, 3: JMP, 4: BVC,         6: SEI         },
                            4: {        1: STY, 2: DEY, 3: STY, 4: BCC, 5: STY, 6: TYA         },
                            5: {0: LDY, 1: LDY, 2: TAY, 3: LDY, 4: BCS, 5: LDY, 6: CLV, 7: LDY },
                            6: {0: CPY, 1: CPY, 2: INY, 3: CPY, 4: BNE,         6: CLD         },
                            6: {0: CPX, 1: CPX, 2: INX, 3: CPX, 4: BEQ,         6: SED         }                           
                        },
                    1:
                        {
                            0: {0: ORA, 1: ORA, 2: ORA, 3: ORA, 4: ORA, 5: ORA, 6: ORA, 7: ORA},
                            1: {0: AND, 1: AND, 2: AND, 3: AND, 4: AND, 5: AND, 6: AND, 7: AND},
                            2: {0: EOR, 1: EOR, 2: EOR, 3: EOR, 4: EOR, 5: EOR, 6: EOR, 7: EOR},
                            3: {0: ADC, 1: ADC, 2: ADC, 3: ADC, 4: ADC, 5: ADC, 6: ADC, 7: ADC},
                            4: {0: STA, 1: STA,         3: STA, 4: STA, 5: STA, 6: STA, 7: STA},
                            5: {0: LDA, 1: LDA, 2: LDA, 3: LDA, 4: LDA, 5: LDA, 6: LDA, 7: LDA},
                            6: {0: CMP, 1: CMP, 2: CMP, 3: CMP, 4: CMP, 5: CMP, 6: CMP, 7: CMP},
                            7: {0: SBC, 1: SBC, 2: SBC, 3: SBC, 4: SBC, 5: SBC, 6: SBC, 7: SBC}
                        }, 
                    2: 
                        {
                            0: {        1: ASL, 2: ASL, 3: ASL,         5: ASL,         7: ASL},
                            1: {        1: ROL, 2: ROL, 3: ROL,         5: ROL,         7: ROL},
                            2: {        1: LSR, 2: LSR, 3: LSR,         5: LSR,         7: LSR},
                            3: {        1: ROR, 2: ROR, 3: ROR,         5: ROR,         7: ROR},
                            4: {        1: STX, 2: TXA, 3: STX,         5: STX, 6: TXS,       },
                            5: {0: LDX, 1: LDX, 2: TAX, 3: LDX,         5: LDX, 6: TSX, 7: LDX},
                            6: {        1: DEC, 2: DEX, 3: DEC,         5: DEC,         7: DEC},
                            7: {        1: INC, 2: NOP, 3: INC,         5: INC,         7: INC}

                        } 
                    }
## Address modes

ADDRESS_MODES = {
    0: 'x_indexed_indirect',
    1: 'zero_page',
    2: 'immediate',
    3: 'absolute',
    4: 'indirect_y_indexed',
    5: 'zero_page_x_indexed',
    6: 'absolute_x_indexed',
    7: 'absolute_y_indexed'}

def fetch_and_decode_instruction(op_code):
    a = (op_code & 0b11100000) >> 5
    b = (op_code & 0b00011100) >> 2
    c = (op_code & 0b00000011)
    return INSTRUCTION_SET[c][a][b]+ (ADDRESS_MODES[b],)


if __name__ == '__main__':
    print(fetch_and_decode_instruction(0b000_0001_00))
