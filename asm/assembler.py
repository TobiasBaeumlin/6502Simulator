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

import asm.assembler_helpers as ah
import re
from collections import OrderedDict


class AssemblerError(Exception):
    def __init__(self, message, error_list):
        super().__init__(message)
        self.errors = error_list


class Pass1Error(Exception):
    def __init__(self, message):
        super().__init__(message)


class Pass2Error(Exception):
    def __init__(self, message):
        super().__init__(message)


def assemble_file(file_name: str) -> OrderedDict:
    with open(file_name) as source_file:
        # remove redundant white space in each line
        source_code = [' '.join(l.split()) for l in source_file]

    label_dict = assemble_file_pass_1(source_code)
    code_dict = assemble_file_pass_2(source_code, label_dict, list_file=None)
    return code_dict


def assemble_file_pass_1(source_code) -> dict:
    line_number = 0
    pass1_errors = {}
    label_dict = {}
    pc = 0

    for line in source_code:
        line_number += 1

        # Strip comments
        line = ah.clean_line(line)

        # ignore blank lines
        if line == '':
            continue

        # Get first token in upper case
        token, line = ah.get_token(line)

        if token not in ah.VALID_MNEMONICS and token not in ah.VALID_DIRECTIVES:
            # not in the valid mnemonic and directive tables, then it must be a LABEL
            if not ah.is_valid_label(token):
                pass1_errors[line_number] = \
                    (f'Invalid label {token}: Must start with letter, followed by maximum 7 letters, digits '
                     f'or underscores')

            # Get next token
            next_token, line = ah.get_token(line)
            if next_token == '.EQU':
                num_data_bytes, data_bytes = ah.build_data_bytes(line)
                label_dict[token] = data_bytes
                continue
            else:
                if pc < 0x100:
                    label_dict[token] = f'{pc:02X}'
                else:
                    label_dict[token] = f'{pc:04X}'
                if next_token == '':
                    continue
            token = next_token

        if len(line) > 1 and line.startswith('#'):
            try:
                line = ah.handle_immediate_operands(line)
            except ValueError as e:
                pass1_errors[line_number] = f'Invalid immediate operand {e}'

        if token == '.ORG':
            try:
                pc = ah.parse_num(line)
            except ValueError as e:
                pass1_errors[line_number] = f'Error in .org directive: {e}'
        elif token == '.DB':
            try:
                num_data_bytes, data_bytes = ah.build_data_bytes(line)
            except ValueError as e:
                pass1_errors[line_number] = f'Error in .db directive: {e}'
            else:
                pc = pc + num_data_bytes
        elif token == '.DS':
            try:
                num_data_bytes = ah.parse_num(line)
            except ValueError:
                pass1_errors[line_number] = f'Invalid numeral in .ds directive: {line}'
            else:
                pc = pc + num_data_bytes
        elif token == '.END':
            break
        # handle Relative Address Mode Instructions
        elif token in ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS and re.fullmatch('[0-9A-Z]{1,8}', token) is not None:
            pc = pc + 2
        else:
            if line == '':
                address_mode, num_bytes, op_code = ah.determine_mode(token, '')
                ah.pass1_error_check(token, '', address_mode, op_code, pass1_errors, line_number)
            else:
                operand, line = ah.get_token(line)
                if line != '':
                    pass1_errors[line_number] = 'Too many tokens'
                    continue
                if operand != 'A' and not operand.startswith('$'):
                    try:
                        operand = ah.parse_symbolic_label(operand, label_dict)
                    except Pass1Error as error:
                        pass1_errors[line_number] = str(error)
                address_mode, num_bytes, op_code = ah.determine_mode(token, operand)
                ah.pass1_error_check(token, operand, address_mode, op_code, pass1_errors, line_number)
            pc = pc + num_bytes

    if len(pass1_errors) == 0:
        print('Pass 1 Complete - No Errors Encountered')
    else:
        print('Pass 1 Complete - ', len(pass1_errors), 'Error(s) Encountered')
        raise AssemblerError('Error(s) in assembler pass 1', pass1_errors)
    print(' ')
    return label_dict


def assemble_file_pass_2(source_code: list[str], label_dict: dict, list_file=None) -> (OrderedDict, dict):
    line_number = 0
    code_dict = OrderedDict()
    debug_info = {}
    pass2_errors = {}
    pc = 0

    if list_file:
        list_out = open(list_file + '.lst', 'w')

    for source_line in source_code:
        line_number += 1

        # Strip comments
        line = ah.clean_line(source_line)

        # ignore blank lines
        if line == '':
            if list_file:
                list_out.write(line + '\n')
            continue

        # Get first token in upper case
        token, line = ah.get_token(line)

        if token not in ah.VALID_MNEMONICS and token not in ah.VALID_DIRECTIVES:
            # Get next token
            next_token, line = ah.get_token(line)

            if next_token == '':
                continue

            if next_token == '.EQU':
                num_data_bytes, data_bytes = ah.build_data_bytes(line)
                if list_file:
                    line_out = ah.build_source_listing_line(source_line, token, '=', data_bytes)
                    list_out.write(line_out)
                continue

            token = next_token

        if len(line) > 1 and line.startswith('#'):
            line = ah.handle_immediate_operands(line)

        if token == '.ORG':
            pc = ah.parse_num(line)
            if list_file:
                line_out = ah.build_source_listing_line(source_line, 'pc =', pc)
                list_out.write(line_out)
        elif token == '.DB':
            num_data_bytes, data_bytes = ah.build_data_bytes(line)
            if list_file:
                line_out = ah.build_source_listing_line(source_line, f'{pc:04X}', ':', data_bytes)
                list_out.write(line_out)
            code_dict[pc] = data_bytes
            debug_info[pc] = line_number
            pc = pc + num_data_bytes
        elif token == '.DS':
            num_data_bytes = ah.parse_num(line)
            if list_file:
                line_out = ah.build_source_listing_line(
                    source_line, f'{pc:04X}', ':', 'Reserved', num_data_bytes, 'Bytes'
                )
                list_out.write(line_out)
            pc = pc + num_data_bytes
        elif token == '.END':
            if list_file:
                line_out = ah.build_source_listing_line(source_line, f'{pc:04X}')
                list_out.write(line_out)
            break
        # Handle Relative Address Mode Instructions
        elif token in ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS and re.fullmatch('[0-9A-Z]{1,8}', token) is not None:
            operand, line = ah.get_token(line)
            if line != '':
                pass2_errors[line_number] = f'Too many tokens in line: {line}'
            op_code = ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS[token]
            try:
                offset = ah.parse_relative_mode_operand(operand, label_dict, pc)
            except ValueError as e:
                offset = '00'
                pass2_errors[line_number] = str(e)
            if list_file:
                line_out = ah.build_source_listing_line(source_line, f'{pc:04X}', ':', op_code, offset)
                list_out.write(line_out)
            code_dict[pc] = op_code + offset
            debug_info[pc] = line_number
            pc = pc + 2
        else:
            if line == '':
                operand = ''
            else:
                operand, line = ah.get_token(line)
                if operand != 'A' and not operand.startswith('$'):
                    try:
                        operand = ah.substitute_symbolic_label(operand, label_dict)
                    except ValueError as e:
                        operand = '00'
                        pass2_errors[line_number] = str(e)
            address_mode, num_bytes, op_code = ah.determine_mode(token, operand)
            if address_mode == 'Invalid':
                pass2_errors[line_number] = f'Undefined label {operand}'
                break
            if address_mode == 'Implied' or address_mode == 'Accumulator':
                if list_file:
                    line_out = ah.build_source_listing_line(source_line,  f'{pc:04X}', ':', op_code)
                    list_out.write(line_out)
                code_dict[pc] = op_code
                debug_info[pc] = line_number
            elif address_mode == 'Immediate' or address_mode == 'Indirect,X' or address_mode == 'Indirect,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(source_line,  f'{pc:04X}', ':', op_code, operand[2:4])
                    list_out.write(line_out)
                code_dict[pc] = op_code + operand[2:4]
                debug_info[pc] = line_number
            elif address_mode == 'Zero Page' or address_mode == 'Zero Page,X' or address_mode == 'Zero Page,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(source_line,  f'{pc:04X}', ':', op_code, operand[1:3])
                    list_out.write(line_out)
                code_dict[pc] = op_code + operand[1:3]
                debug_info[pc] = line_number
            elif address_mode == 'Absolute' or address_mode == 'Absolute,X' or address_mode == 'Absolute,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(
                        source_line,  f'{pc:04X}', ':', op_code, operand[3:5], operand[1:3]
                    )
                    list_out.write(line_out)
                code_dict[pc] = op_code + operand[3:5] + operand[1:3]
                debug_info[pc] = line_number
            elif address_mode == 'Indirect':
                if list_file:
                    line_out = ah.build_source_listing_line(
                        source_line,  f'{pc:04X}', ':', op_code, operand[4:6], operand[2:4]
                    )
                    list_out.write(line_out)
                code_dict[pc] = op_code + operand[4:6] + operand[2:4]
                debug_info[pc] = line_number

            pc = pc + num_bytes

    if list_file:
        list_out.close()

    if len(pass2_errors) > 0:
        raise AssemblerError('Error(s) in pass 2', pass2_errors)

    print('Pass 2 Complete - No Errors Encountered')
    return code_dict, debug_info


if __name__ == '__main__':
    # with open('../../6502Asm/test1.asm') as source_file:
    #     # remove redundant white space in each line
    #     source_code = [' '.join(l.split()) for l in source_file]
    source_code = ["label BNE $4", 'BEQ -10', 'BMI +10', 'BPL label']
    try:
        label_dict = assemble_file_pass_1(source_code)
    except AssemblerError as e:
        print(e, e.errors)
    else:
        try:
            code_dict = assemble_file_pass_2(source_code, label_dict, list_file='test.out')
        except AssemblerError as e:
            print(e, e.errors)
