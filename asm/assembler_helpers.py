#     6502Simulator, a didactic visual simulator of the 6502 processor
#     Copyright (C) 2024  Tobias Bäumlin
#     Based on  6502Asm Copyright (C) 2022 James Salvino
#     See https://github.com/SYSPROG-JLS/6502Asm
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

import re

from asm.assembler import Pass1Error

VALID_MNEMONICS = {
    'LDA', 'BVS', 'PLA', 'INY', 'PHA', 'RTS', 'BCS', 'DEC', 'AND',
    'NOP', 'STY', 'ASL', 'BRK', 'TAX', 'SED', 'TXS', 'INC', 'EOR',
    'BMI', 'CPX', 'TYA', 'INX', 'LDY', 'PLP', 'LDX', 'STX', 'JSR',
    'BNE', 'BVC', 'CPY', 'LSR', 'CLI', 'CLV', 'ROL', 'TXA', 'DEX',
    'TSX', 'CLD', 'SEC', 'TAY', 'BPL', 'JMP', 'ADC', 'CLC', 'SEI',
    'PHP', 'SBC', 'BCC', 'BIT', 'RTI', 'ROR', 'STA', 'DEY', 'BEQ',
    'CMP', 'ORA',
}

VALID_DIRECTIVES = {
    '.ORG', '.DB', '.DS', '.EQU', '.END'
}

ADDRESS_MODES = {
    'Accumulator': (1, [('ASL', '0A'), ('LSR', '4A'), ('ROL', '2A'), ('ROR', '6A')]),

    'Immediate': (2, [('ADC', '69'), ('AND', '29'), ('LDY', 'A0'), ('LDX', 'A2'),
                      ('LDA', 'A9'), ('EOR', '49'), ('CPY', 'C0'), ('CPX', 'E0'),
                      ('CMP', 'C9'), ('ORA', '09'), ('SBC', 'E9')]),

    'Zero Page': (2, [('ADC', '65'), ('AND', '25'), ('ASL', '06'), ('BIT', '24'),
                      ('LSR', '46'), ('LDY', 'A4'), ('LDX', 'A6'), ('LDA', 'A5'),
                      ('INC', 'E6'), ('EOR', '45'), ('DEC', 'C6'), ('CPY', 'C4'),
                      ('CPX', 'E4'), ('CMP', 'C5'), ('ORA', '05'), ('ROL', '26'),
                      ('ROR', '66'), ('SBC', 'E5'), ('STA', '85'), ('STX', '86'),
                      ('STY', '84')]),

    'Zero Page,X': (2, [('ADC', '75'), ('AND', '35'), ('ASL', '16'), ('CMP', 'D5'),
                        ('DEC', 'D6'), ('EOR', '55'), ('INC', 'F6'), ('LDA', 'B5'),
                        ('LDY', 'B4'), ('LSR', '56'), ('ORA', '15'), ('ROL', '36'),
                        ('ROR', '76'), ('SBC', 'F5'), ('STA', '95'), ('STY', '94')]),

    'Zero Page,Y': (2, [('LDX', 'B6'), ('STX', '96')]),

    'Absolute': (3, [('ADC', '6D'), ('AND', '2D'), ('ASL', '0E'), ('BIT', '2C'),
                     ('CMP', 'CD'), ('CPX', 'EC'), ('CPY', 'CC'), ('DEC', 'CE'),
                     ('EOR', '4D'), ('INC', 'EE'), ('JMP', '4C'), ('JSR', '20'),
                     ('LDA', 'AD'), ('LDX', 'AE'), ('LDY', 'AC'), ('LSR', '4E'),
                     ('ORA', '0D'), ('ROL', '2E'), ('ROR', '6E'), ('SBC', 'ED'),
                     ('STA', '8D'), ('STX', '8E'), ('STY', '8C')]),

    'Absolute,X': (3, [('ADC', '7D'), ('AND', '3D'), ('ASL', '1E'), ('CMP', 'DD'),
                       ('DEC', 'DE'), ('EOR', '5D'), ('INC', 'FE'), ('LDA', 'BD'),
                       ('LDY', 'BC'), ('LSR', '5E'), ('ORA', '1D'), ('ROL', '3E'),
                       ('SBC', 'FD'), ('STA', '9D')]),

    'Absolute,Y': (3, [('ADC', '79'), ('AND', '39'), ('CMP', 'D9'), ('EOR', '59'),
                       ('LDA', 'B9'), ('LDX', 'BE'), ('ORA', '19'), ('SBC', 'F9'),
                       ('STA', '99')]),

    'Indirect': (3, [('JMP', '6C')]),

    'Indirect,X': (2, [('ADC', '61'), ('AND', '21'), ('CMP', 'C1'), ('EOR', '41'),
                       ('LDA', 'A1'), ('ORA', '01'), ('SBC', 'E1'), ('STA', '81')]),

    'Indirect,Y': (2, [('ADC', '71'), ('AND', '31'), ('CMP', 'D1'), ('EOR', '51'),
                       ('LDA', 'B1'), ('ORA', '11'), ('SBC', 'F1'), ('STA', '91')]),

    'Implied': (1, [('BRK', '00'), ('CLC', '18'), ('SEC', '38'), ('CLI', '58'),
                    ('SEI', '78'), ('CLV', 'B8'), ('CLD', 'D8'), ('SED', 'F8'),
                    ('TAX', 'AA'), ('TXA', '8A'), ('DEX', 'CA'), ('INX', 'E8'),
                    ('TAY', 'A8'), ('TYA', '98'), ('DEY', '88'), ('INY', 'C8'),
                    ('TXS', '9A'), ('TSX', 'BA'), ('PHA', '48'), ('PLA', '68'),
                    ('PHP', '08'), ('PLP', '28'), ('NOP', 'EA'), ('RTI', '40'),
                    ('RTS', '60')])
}

ADDRESS_MODE_PATTERNS = {
    'A': 'Accumulator',
    '\#\$([0-9A-F]{2}|UNDEF)': 'Immediate',
    '\$[0-9A-F]{2}': 'Zero Page',
    '\$[0-9A-F]{2},X': 'Zero Page,X',
    '\$[0-9A-F]{2},Y': 'Zero Page,Y',
    '\$([0-9A-F]{4}|UNDEF)': 'Absolute',
    '\$([0-9A-F]{4}|UNDEF),X': 'Absolute,X',
    '\$([0-9A-F]{4}|UNDEF),Y': 'Absolute,Y',
    '\(\$([0-9A-F]{4}|UNDEF)\)': 'Indirect',
    '\(\$([0-9A-F]{2}|UNDEF),X\)': 'Indirect,X',
    '\(\$([0-9A-F]{2}|UNDEF)\),Y': 'Indirect,Y',
}

ADDRESS_MODE_PATTERNS_SYM = {
    'A': 'Accumulator',
    '\#[0-9A-Z]{1,8}': 'Immediate',
    '[0-9A-Z]{1,8}([+-][0-9]+)?': 'Zero Page_Absolute',
    '[0-9A-Z]{1,8}([+-][0-9]+)?,X': 'Zero Page_Absolute,X',
    '[0-9A-Z]{1,8}([+-][0-9]+)?,Y': 'Zero Page_Absolute,Y',
    '\([0-9A-Z]{1,8}([+-][0-9]+)?\)': 'Indirect',
    '\([0-9A-Z]{1,8}([+-][0-9]+)?,X\)': 'Indirect,X',
    '\([0-9A-Z]{1,8}([+-][0-9]+)?\),Y': 'Indirect,Y',

}

RELATIVE_ADDRESS_MODE_INSTRUCTIONS = {
    'BPL': '10', 'BMI': '30', 'BVC': '50', 'BVS': '70',
    'BCC': '90', 'BCS': 'B0', 'BNE': 'D0', 'BEQ': 'F0'
}


def is_valid_label(token):
    return re.fullmatch('[A-Z_][A-Z0-9_]{0,7}$', token) is not None and token != 'A'


def clean_line(line: str) -> str:
    return line.split(';')[0].strip()


def get_token(line):
    try:
        token, rest = line.split(maxsplit=1)
    except ValueError:
        return line.upper(), ''
    return token.upper(), rest


# Construct, print, and return a source listing line
def build_source_listing_line(sline, *arguments):
    z = ''
    for arg in arguments:
        if isinstance(arg, str):
            z = z + arg + ' '
        else:
            z = z + str(arg) + ' '
    l = len(z)
    if l > 25:
        z = z[0:26]
    else:
        z = z + (25 - l) * ' '
    print(z, sline)
    return z + ' ' + sline + '\n'


# Convert a (signed) integer to a 1 byte hex string in two's complement format
def convert_int_to_twos_complement(x: int) -> str:
    assert -128 <= x < 128
    return f'{int.from_bytes(x.to_bytes(1, signed=True)):02X}'


# Given the mnemonic and operand in a source line
# determine the addressing mode and...
# return the addressing mode, number of bytes for that instruction and 
# the instruction's opcode
#
# 'XX' is returned in cases where the assembler mnemonic is invalid
# 'Invalid' is returned for mode and 9 is returned for numbytes 
# in cases where the addressing mode cannot be determined
#
def determine_mode(mnemonic, operand):
    mode = 'Invalid'
    if operand == '':
        mode = 'Implied'
    elif operand == 'A':
        mode = 'Accumulator'
    else:
        for p in ADDRESS_MODE_PATTERNS.keys():
            if re.fullmatch(p, operand):
                mode = ADDRESS_MODE_PATTERNS[p]
                break

    if mode == 'Invalid':
        return mode, 0, 'XX'

    numbytes = ADDRESS_MODES[mode][0]
    good_mnemonic = False
    for m, op_code in ADDRESS_MODES[mode][1]:
        if m == mnemonic:
            good_mnemonic = True
            break
    if good_mnemonic:
        return mode, numbytes, op_code
    else:
        return mode, numbytes, 'XX'


# Construct data bytes field from a .db directive
# return the number of bytes and data bytes string
def build_data_bytes(operand):
    db_str = ''
    for token in [token.strip() for token in operand.split(',')]:
        if len(token) == 0:
            raise ValueError('Empty number')
        if token.startswith('$'):
            try:
                value = int(token[1:], 16)
            except ValueError:
                raise ValueError(f'Invalid hex number {token}')
            s = f'{value:X}'
        elif token[0].isdigit():
            try:
                value = int(token)
            except ValueError:
                raise ValueError(f'Invalid decimal number {token}')
            s = f'{value:X}'
        elif token.startswith("'"):
            s = ''
            for c in token.strip("'"):
                try:
                    s += f'{ord(c):02X}'
                except ValueError:
                    raise ValueError(f'Invalid character {c}')
        elif token.startswith("%"):
            try:
                value = int(token[1:], 2)
            except ValueError:
                raise ValueError(f'Invalid binary number {token}')
            s = f'{value:X}'
        else:
            raise ValueError(f'Invalid byte format: {token}')
        db_str += '0' * (len(s) % 2) + s
    nb = len(db_str) // 2
    return nb, db_str


def parse_num(text: str) -> int:
    if text.startswith('0x'):
        try:
            value = int(text[2:], 16)
        except ValueError:
            value = None
    elif text.startswith('$'):
        try:
            value = int(text[1:], 16)
        except ValueError:
            value = None
    elif text.startswith('0b'):
        try:
            value = int(text[2:], 2)
        except ValueError:
            value = None
    elif text.startswith('%'):
        try:
            value = int(text[1:], 2)
        except ValueError:
            value = None
    else:
        try:
            value = int(text, 10)
        except ValueError:
            value = None
    if value is None:
        raise ValueError('Invalid numeral')
    return value


def pass1_error_check(token, operand, address_mode, op_code, errors, line_number):
    if op_code == 'XX':
        if address_mode == 'Invalid':
            errors[line_number] = f'Invalid Operand {operand}'
        else:
            errors[line_number] = f'Invalid mnemonic for specified addressing mode {token}'


def handle_immediate_operands(operand: str) -> str:
    if len(operand) < 2:
        raise ValueError(f'Invalid operand: {operand}')
    if operand[1].isdigit():
        try:
            operand = f'#${int(operand[1:]):02X}'
        except ValueError:
            raise ValueError(f'Invalid decimal operand: {operand}')
    elif operand[1] == "'":
        try:
            operand = f'#${ord(operand[2:3]):02X}'
        except ValueError:
            raise ValueError(f'Invalid character operand {operand}')
    elif operand[1] == "%":
        try:
            operand = f'#${int(operand[2:], 2):02X}'
        except ValueError:
            raise ValueError(f'Invalid binary operand {operand}')
    elif operand[1] == "$":
        try:
            operand = f'#${int(operand[2:], 16):02X}'
        except ValueError:
            raise ValueError(f'Invalid hexadecimal operand {operand}')
    elif is_valid_label(operand[1:].upper()):
        pass
    else:
        raise ValueError(f'Invalid operand {operand}')
    return operand


def extract_label_from_operand(operand: str, mode: str) -> str:
    if mode == 'Zero Page_Absolute':
        return operand
    if mode == 'Zero Page_Absolute,X':
        return operand[:-2]
        # return operand.rstrip(',X')
    if mode == 'Zero Page_Absolute,Y':
        return operand[:-2]
        # return operand.rstrip(',Y')
    if mode == 'Indirect':
        return operand[1:-1]
        # return operand.lstrip('(').rstrip(')')
    if mode == 'Indirect,X':
        return operand[1:-3]
        #return operand.lstrip('(').rstrip(',X)')
    if mode == 'Indirect,Y':
        return operand[1:-3]
        # return operand.lstrip('(').rstrip('),Y')
    # mode must be 'Immediate'
    return operand[1:]
    # return operand.lstrip('#')


def rebuild_operand(operand: str, mode: str) -> str:
    if mode == 'Zero Page_Absolute':
        return operand
    if mode == 'Zero Page_Absolute,X':
        return operand + ',X'
    if mode == 'Zero Page_Absolute,Y':
        return operand + ',Y'
    if mode == 'Indirect':
        return f'({operand})'
    if mode == 'Indirect,X':
        return f'({operand},X)'
    if mode == 'Indirect,Y':
        return f'({operand}),Y'
    # mode must be 'Immediate':
    return f'#{operand}'


def parse_symbolic_label(operand: str, label_dict: dict, evaluate: bool=False) -> str:
    for p in ADDRESS_MODE_PATTERNS_SYM.keys():
        if re.fullmatch(p, operand):
            mode = ADDRESS_MODE_PATTERNS_SYM[p]
            label = extract_label_from_operand(operand, mode)
            # handle arithmetic in symbolic label: <label>[+-]<num>
            z = re.search('[+-][0-9]+$', label)
            if z:
                f, t = z.span()
                label = label[0:f]

            if not is_valid_label(label):
                raise Pass1Error(f'invalid label: {label}')

            if label in label_dict:
                operand = '$' + label_dict[label]
            else:
                # label is not defined yet
                operand = '$UNDEF'
                label_dict[label] = 'UNDEF'
            operand = rebuild_operand(operand, mode)
            break
    return operand


def substitute_symbolic_label(operand: str, label_dict: dict) -> str:
    for p in ADDRESS_MODE_PATTERNS_SYM.keys():
        z = re.fullmatch(p, operand)
        if z:
            mode = ADDRESS_MODE_PATTERNS_SYM[p]
            label = extract_label_from_operand(operand, mode)
            # handle arithmetic in symbolic label
            z = re.search('[+-][0-9]+$', label)
            if z:
                f, t = z.span()
                exp = label[f:t]
                label = label[0:f]
                if label_dict[label] == 'UNDEF':
                    raise ValueError(f'Undefined label {label}')
                lab_len = len(label_dict[label])
                x = eval(str(int(label_dict[label], 16)) + exp)
                if lab_len == 2 and x < 256:
                    operand = '$' + f'{x:02X}'
                elif lab_len == 4 and x < 65536:
                    operand = '$' + f'{x:04X}'
                else:
                    raise ValueError('Symbol Arithmetic overflow')
            else:
                operand = f'${label_dict[label]}'
                if operand == '$UNDEF':
                    raise ValueError(f'Undefined label {label}')
            operand = rebuild_operand(operand, mode)
            break
    return operand


def parse_relative_mode_operand(operand: str, label_dict: dict, pc: int) -> str:
    if len(operand) == 0:
        raise ValueError('Empty operand for relative address mode')
    if operand.startswith('$'):
        try:
            value = int(operand[1:], 16) - pc
        except ValueError:
            raise ValueError('Invalid hexadecimal operand')
    elif operand[0] in ('+', '-'):
        try:
            value = int(operand)
        except ValueError:
            raise ValueError('Invalid relative operand')
    elif operand in label_dict:
        value = int(label_dict[operand], 16) - pc
    else:
        raise ValueError(f'Undefined label {operand}')
    if value > 127 or value < -128:
        raise ValueError('Relative displacement out of range')
    if value < 0:
        return convert_int_to_twos_complement(value - 2)
    return f'{(value-2):02X}'

