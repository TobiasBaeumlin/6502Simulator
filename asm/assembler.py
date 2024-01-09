import asm.assembler_helpers as ah
import re
from collections import OrderedDict


class AssemblerError(Exception):
    def __init__(self, message, error_list):
        super().__init__(message)
        self.errors = error_list


def pass1_error_check(tokens, address_mode, op_code, errors, line_number):
    if op_code == 'XX':
        if address_mode == 'Invalid':
            errors[line_number] = f'Invalid Operand {tokens[1]}'
            print('Error:', tokens[1], ' - Invalid Operand')
        else:
            errors[line_number] = f'Invalid mnemonic for specified addressing mode {tokens[0]}'
            print('Error:', tokens[0], ' - Invalid Mnemonic for the specified Addressing Mode')
    return


def handle_immediate_operands(operand):
    if operand[1].isdigit():
        return f'#${int(operand[1:]):02X}'
    elif operand[1] == "'":
        return f'#${ord(operand[2:3]):02X}'
    elif operand[1] == "%":
        return f'#${int(operand[2:]):02X}'
    else:
        return operand


def assemble_file(file_name: str) -> OrderedDict :
    with open(file_name) as source_file:
        # remove redundant white space in each line
        source_code = [' '.join(l.split()) for l in source_file]

    label_dict = assemble_file_pass_1(source_code)
    code_dict = assemble_file_pass_2(source_code, label_dict, list_file=None)
    return code_dict


def assemble_file_pass_1(source_code) -> dict:
    line_number = 0
    num_bytes = 0
    pass1_errors = {}
    label_dict = {}
    pc = 0

    for line in source_code:
        line_number += 1

        # ignore blank lines
        if len(line) == 0 or line.isspace():
            continue
        else:
            tokens = ah.tokenize_source_line(line)
            # detect lines with just comments in them
            if len(tokens) == 0:
                continue

        if (tokens[0] not in ah.VALID_MNEMONICS) and (tokens[0] not in ah.VALID_DIRECTIVES):
            # not in the valid mnemonic and directive tables, then it must be a LABEL
            label = tokens.pop(0)
            label_dict[label] = f'{pc:04X}'  
            if len(tokens) == 0:
                continue

        if len(tokens) > 2:
            pass1_errors[line_number] = 'Too many tokens'
            continue

        if len(tokens) == 2 and tokens[1].startswith('#'):
            tokens[1] = handle_immediate_operands(tokens[1])

        if tokens[0] == '.ORG':
            pc = ah.parse_num(tokens[1])
        elif tokens[0] == '.DB':
            num_data_bytes, data_bytes = ah.build_data_bytes(tokens[1])
            pc = pc + num_data_bytes
        elif tokens[0] == '.DS':
            pc = pc + int(tokens[1])
        elif tokens[0] == '.EQU':
            num_data_bytes, data_bytes = ah.build_data_bytes(tokens[1])
            label_dict[label] = data_bytes
        elif tokens[0] == '.END':
            break
        # handle Relative Address Mode Instructions    
        elif tokens[0] in ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS and re.fullmatch('[0-9A-Z]{1,8}', tokens[1]) != None:
            pc = pc + 2
        else:
            if len(tokens) == 2:
                operand = tokens[1]
                if operand != 'A' and not operand.startswith('$'):
                    for p in ah.ADDRESS_MODE_PATTERNS_SYM.keys():
                        if re.fullmatch(p, operand):
                            mode = ah.ADDRESS_MODE_PATTERNS_SYM[p]
                            if isinstance(mode, tuple):
                                if 'Zero Page' in mode:
                                    label = operand
                                elif 'Zero Page,X' in mode:
                                    label = operand.rstrip(',X')
                                elif 'Zero Page,Y' in mode:
                                    label = operand.rstrip(',Y')
                            else:
                                if mode == 'Indirect':
                                    label = operand.lstrip('(').rstrip(')')
                                elif mode == 'Indirect,X':
                                    label = operand.lstrip('(').rstrip(',X)')
                                elif mode == 'Indirect,Y':
                                    label = operand.lstrip('(').rstrip('),Y')
                                elif mode == 'Immediate':   
                                    label = operand.lstrip('#')
                            # handle arithmetic in symbolic label
                            z = re.search('[0-9+-]{2,4}', label)
                            if z:
                                f, t = z.span()
                                label = label[0:f]
                            if label in label_dict:
                                operand = '$' + label_dict[label]
                            else:
                                operand = '$FFFF'
                                label_dict[label] = operand
                            if isinstance(mode, tuple):
                                if 'Zero Page,X' in mode:
                                    operand = operand + ',X'
                                elif 'Zero Page,Y' in mode:
                                    operand = operand + ',Y'
                            else:
                                if mode == 'Indirect':
                                    operand = '(' + operand + ')'
                                elif mode == 'Indirect,X':
                                    operand = '(' + operand + ',X)'
                                elif mode == 'Indirect,Y':
                                    operand = '(' + operand + '),Y'
                                elif mode == 'Immediate':   
                                    operand = '#' + operand                            
                            break
                            
                address_mode, num_bytes, op_code = ah.determine_mode(tokens[0], operand)
                pass1_error_check(tokens, address_mode, op_code, pass1_errors, line_number)
            elif len(tokens) == 1:
                address_mode, num_bytes, op_code = ah.determine_mode(tokens[0], '')
                pass1_error_check(tokens, address_mode, op_code, pass1_errors, line_number)

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
    num_bytes = 0
    code_dict = OrderedDict()
    debug_info = {}
    pass2_errors = {}
    pc = 0

    address_mode = ''

    if list_file: 
        list_out = open(list_file + '.lst', 'w')

    for line in source_code:
        line_number += 1

        # ignore blank lines
        if len(line) == 0 or line.isspace():
            if list_file:
                list_out.write(line + '\n') 
            continue
        else:
            token_line = ah.tokenize_source_line(line)
            # detect lines with just comments in them
            if len(token_line) == 0:
                if list_file:
                    list_out.write(line + '\n') 
                continue        

        if (token_line[0] not in ah.VALID_MNEMONICS) and (token_line[0] not in ah.VALID_DIRECTIVES):
            # not in the valid mnemonic and directive tables, then it must be a LABEL
            label = token_line.pop(0)
            if len(token_line) == 0:
                pass2_errors[line_number] = 'No instruction after label'
                continue

        if len(token_line) == 2 and token_line[1].startswith('#'):
            token_line[1] = handle_immediate_operands(token_line[1])

        if token_line[0] == '.ORG':
            pc = ah.parse_num(token_line[1])
            if list_file:
                line_out = ah.build_source_listing_line(line, 'pc =', pc)
                list_out.write(line_out)   
        elif token_line[0] == '.DB':
            num_data_bytes, data_bytes = ah.build_data_bytes(token_line[1])
            if list_file:
                line_out = ah.build_source_listing_line(line, f'{pc:04X}', ':', data_bytes)
                list_out.write(line_out)   
            code_dict[pc] = data_bytes
            debug_info[pc] = line_number
            pc = pc + num_data_bytes
        elif token_line[0] == '.DS':
            if list_file:
                line_out = ah.build_source_listing_line(line, f'{pc:04X}', ':', 'Reserved', token_line[1], 'Bytes')
                list_out.write(line_out)   
            pc = pc + int(token_line[1])
        elif token_line[0] == '.EQU':
            num_data_bytes, data_bytes = ah.build_data_bytes(token_line[1])
            if list_file:
                line_out = ah.build_source_listing_line(line, label, '=', data_bytes)
                list_out.write(line_out)   
        elif token_line[0] == '.END':
            if list_file:
                line_out = ah.build_source_listing_line(line, f'{pc:04X}')
                list_out.write(line_out)   
            break
        # handle Relative Address Mode Instructions    
        elif token_line[0] in ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS and re.fullmatch('[0-9A-Z]{1,8}', token_line[1]) != None:
            op_code = ah.RELATIVE_ADDRESS_MODE_INSTRUCTIONS[token_line[0]]
            x = int(label_dict[token_line[1]], 16) - pc
            if x > 127 or x < -128:
                pass2_errors[line_number] = f'Relative displacement out of range: {token_line}'
                print('Error on:', token_line, ' - Relative Displacement Out of Range')
            else:
                if x < 0:
                    disp = ah.convert_int_to_twos_complement(x-2)
                else:    
                    disp = hex(x-2)[2:].zfill(2)
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code, disp)
                    list_out.write(line_out)   
                code_dict[pc] = op_code + disp
                debug_info[pc] = line_number
                pc = pc + 2
        else:
            if len(token_line) == 2:
                operand = token_line[1]
                if operand != 'A' and not operand.startswith('$'):
                    for p in ah.ADDRESS_MODE_PATTERNS_SYM.keys():
                        z = re.fullmatch(p, operand)
                        if z:
                            mode = ah.ADDRESS_MODE_PATTERNS_SYM[p]
                            if isinstance(mode, tuple):
                                if 'Zero Page' in mode:
                                    label = operand
                                elif 'Zero Page,X' in mode:
                                    label = operand.rstrip(',X')
                                elif 'Zero Page,Y' in mode:
                                    label = operand.rstrip(',Y')
                            else:
                                if mode == 'Indirect':
                                    label = operand.lstrip('(').rstrip(')')
                                elif mode == 'Indirect,X':
                                    label = operand.lstrip('(').rstrip(',X)')
                                elif mode == 'Indirect,Y':
                                    label = operand.lstrip('(').rstrip('),Y')
                                elif mode == 'Immediate':   
                                    label = operand.lstrip('#')
                            # handle arithmetic in symbolic label
                            z = re.search('[0-9+-]{2,4}', label)
                            if z:
                                f, t = z.span()
                                exp = label[f:t]
                                label = label[0:f]
                                lab_len = len(label_dict[label])
                                x = eval(str(int(label_dict[label], 16)) + exp)
                                if lab_len == 2 and x < 256:
                                    operand = '$' +  f'{x:02X}'
                                elif lab_len == 4 and x < 65536:
                                    operand = '$' +  f'{x:04X}'
                                else:
                                    pass2_errors[line_number] = f'Symbol Arithmetic overflow: {token_line}'
                                    print('Error on:', token_line, ' - Symbol Arithmetic Overflow')
                                    operand = '$FF'
                                    if lab_len == 4:
                                        operand += 'FF'
                            else:
                                operand = '$' + label_dict[label]

                            if isinstance(mode, tuple):
                                if 'Zero Page,X' in mode:
                                    operand = operand + ',X'
                                elif 'Zero Page,Y' in mode:
                                    operand = operand + ',Y'
                            else:
                                if mode == 'Indirect':
                                    operand = '(' + operand + ')'
                                elif mode == 'Indirect,X':
                                    operand = '(' + operand + ',X)'
                                elif mode == 'Indirect,Y':
                                    operand = '(' + operand + '),Y'
                                elif mode == 'Immediate':   
                                    operand = '#' + operand                            
                            break
                            
                address_mode, num_bytes, op_code = ah.determine_mode(token_line[0], operand)
            elif len(token_line) == 1:
                address_mode, num_bytes, op_code = ah.determine_mode(token_line[0], '')

            if address_mode == 'Invalid':
                pass2_errors[line_number] = f'Undefined label {label}'
                break
            if address_mode == 'Implied' or address_mode == 'Accumulator':
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code)
                    list_out.write(line_out)   
                code_dict[pc] = op_code
                debug_info[pc] = line_number
            elif address_mode == 'Immediate' or address_mode == 'Indirect,X' or address_mode == 'Indirect,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code, operand[2:4])
                    list_out.write(line_out)   
                code_dict[pc] = op_code + operand[2:4]
                debug_info[pc] = line_number
            elif address_mode == 'Zero Page' or address_mode == 'Zero Page,X' or address_mode == 'Zero Page,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code, operand[1:3])
                    list_out.write(line_out)   
                code_dict[pc] = op_code + operand[1:3]
                debug_info[pc] = line_number
            elif address_mode == 'Absolute' or address_mode == 'Absolute,X' or address_mode == 'Absolute,Y':
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code, operand[3:5], operand[1:3])
                    list_out.write(line_out)   
                code_dict[pc] = op_code + operand[3:5] + operand[1:3]
                debug_info[pc] = line_number
            elif address_mode == 'Indirect':
                if list_file:
                    line_out = ah.build_source_listing_line(line,  f'{pc:04X}', ':', op_code, operand[4:6], operand[2:4])    
                    list_out.write(line_out)   
                code_dict[pc] = op_code + operand[4:6] + operand[2:4]
                debug_info[pc] = line_number
            pc = pc + num_bytes

    if list_file:        
        list_out.close()

    if len(pass2_errors) > 0:
        print('Error(s) Encountered')
        print('Unable to Continue')
        raise AssemblerError('Error(s) in pass 2', pass2_errors)

    print('Pass 2 Complete - No Errors Encountered')
    return code_dict, debug_info
