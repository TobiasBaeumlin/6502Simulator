import asm6502Mod as fn
import re
import sys
from collections import OrderedDict

class AssemblerError(Exception):
    def __init__(self, message, error_list):
        super().__init__(message)
        self.errors = error_list




pass2_error_count = 0
code_dict = OrderedDict()


address_mode_patterns_sym = {
    '\#[0-9A-Z]{1,8}': 'Immediate', '[0-9A-Z+-]{1,8}': ('Zero Page', 'Absolute'), 
    '[0-9A-Z]{1,8},X': ('Zero Page,X', 'Absolute,X'), '[0-9A-Z]{1,8},Y': ('Zero Page,Y', 'Absolute,Y'),  
    '\([0-9A-Z]{1,8}\)': 'Indirect', '\([0-9A-Z]{1,8},X\)': 'Indirect,X', '\([0-9A-Z]{1,8}\),Y': 'Indirect,Y'
}


relative_address_mode_instructions = {
    'BPL': '10', 'BMI': '30', 'BVC': '50', 'BVS':'70', 
    'BCC': '90', 'BCS': 'B0', 'BNE': 'D0', 'BEQ': 'F0'
}


def pass1_error_check(t, a, o, errors, line_number):
    global pass1_error_count
    if o == 'XX':
        pass1_error_count += 1
        if a == 'Invalid':
            errors[line_number] = f'Invalid Operand {t[1]}'
            print('Error:', t[1], ' - Invalid Operand')
        else:
            errors[line_number] = f'Invalid mnemonic for specified addressing mode {t[0]}'
            print('Error:', t[0], ' - Invalid Mnemonic for the specified Addressing Mode')
    return


def assemble_file(file_name: str) -> list:
    with open(file_name) as source_file:
         source_code = [l.rstrip('\n') for l in source_file]

    label_dict = assemble_file_pass_1(source_code)
    code_dict = assemble_file_pass_2(source_code, label_dict, write_lst_file=False)
    return code_dict

def assemble_file_pass_1(source_code) -> dict:
    pass1_errors = {}
    label_dict = {}
    pc = 1
    line_number = 0
    
    for line in source_code:
        line_number += 1

        # ignore blank lines
        if len(line) == 0 or line.isspace():
            continue
        else:
            token_line = fn.tokenize_sl(line)
            # detect lines with just comments in them
            if len(token_line) == 0:
                continue

        if (token_line[0] not in fn.valid_mnemonic_table) and (token_line[0] not in fn.valid_directive_table):
        # not in the valid mnemonic and directive tables, then it must be a LABEL
            label = token_line.pop(0)
            label_dict[label] = fn.i2h(pc, 4)

        if len(token_line) == 2 and token_line[1].startswith('#'):
        # handle different types of immediate operands: #$0A, #128, #'C', #%00001111
            if token_line[1][1].isdigit():
                token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][1:]), 2)
            elif token_line[1][1] == "'":
                token_line[1] = '#' + '$' + fn.i2h(ord(token_line[1][2:3]), 2)
            elif token_line[1][1] == "%":
                token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][2:],2), 2)
                
        if token_line[0] == '.ORG':
            pc = int(token_line[1][1:],16)
        elif token_line[0] == '.DB':
            num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
            pc = pc + num_data_bytes
        elif token_line[0] == '.DS':
            pc = pc + int(token_line[1])
        elif token_line[0] == '.EQU':
            num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
            label_dict[label] = data_bytes
        elif token_line[0] == '.END':
            break
        # handle Relative Address Mode Instructions    
        elif token_line[0] in relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token_line[1]) != None:
            pc = pc + 2
        else:
            if len(token_line) == 2:
                operand = token_line[1]
                if not '$' in operand:
                    for p in address_mode_patterns_sym.keys():
                        z = re.fullmatch(p, operand)
                        if z != None:
                            mode = address_mode_patterns_sym[p]
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
                            if z != None:
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
                            
                am, nb, oc = fn.determine_mode(token_line[0], operand)
                pass1_error_check(token_line, am, oc, line_number)
            elif len(token_line) == 1:
                am, nb, oc = fn.determine_mode(token_line[0], '')
                pass1_error_check(token_line, am, oc, line_number)
            else:
                pass1_error_count += 1
                pass1_errors[line_number] = 'Too many tokens'
                print(f'Error on line {line_number}:', token_line, ' - Too Many Tokens')
                    
            pc = pc + nb    

        if len(pass1_errors) == 0:
            print('Pass 1 Complete - No Errors Encountered')
        else:
            print('Pass 1 Complete - ', pass1_error_count, 'Error(s) Encountered')
            raise AssemblerError('Error(s) in assembler pass 1', pass1_errors)
        print(' ')

    return label_dict

        
def assemble_file_pass_2(source_code, label_dict, write_list_file=False):
    line_number = 0
    pass2_errors = {}

    if write_list_file:
        lst_file_name = file_name.split('.')[0] + '.lst' 
        list_out = open(lst_file_name, 'w')

    for line in source_code:
        # ignore blank lines
        if len(line) == 0 or line.isspace():
            print(line)
            if write_list_file:
                list_out.write(line + '\n') 
            continue
        else:
            token_line = fn.tokenize_sl(line)
            # detect lines with just comments in them
            if len(token_line) == 0:
                print(line)
                if write_list_file:
                    list_out.write(line + '\n') 
                continue        

        if (token_line[0] not in fn.valid_mnemonic_table) and (token_line[0] not in fn.valid_directive_table):
        # not in the valid mnemonic and directive tables, then it must be a LABEL
            label = token_line.pop(0)

        if len(token_line) == 2 and token_line[1].startswith('#'):
        # handle different types of immediate operands: #$0A, #128, #'C', #%00001111
            if token_line[1][1].isdigit():
                token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][1:]), 2)
            elif token_line[1][1] == "'":
                token_line[1] = '#' + '$' + fn.i2h(ord(token_line[1][2:3]), 2)
            elif token_line[1][1] == "%":
                token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][2:],2), 2)

        if token_line[0] == '.ORG':
            pc = int(token_line[1][1:],16)
            if write_list_file:
                line_out = fn.myprint(line, 'pc =', pc)
                list_out.write(line_out)   
        elif token_line[0] == '.DB':
            num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
            if write_list_file:
                line_out = fn.myprint(line, fn.i2h(pc, 4), ':', data_bytes)
                list_out.write(line_out)   
            code_dict[fn.i2h(pc, 4)] = data_bytes
            pc = pc + num_data_bytes
        elif token_line[0] == '.DS':
            if write_list_file:
                line_out = fn.myprint(line, fn.i2h(pc, 4), ':', 'Reserved', token_line[1], 'Bytes')
                list_out.write(line_out)   
            pc = pc + int(token_line[1])
        elif token_line[0] == '.EQU':
            num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
            if write_list_file:
                line_out = fn.myprint(line, label, '=', data_bytes)
                list_out.write(line_out)   
        elif token_line[0] == '.END':
            if write_list_file:
                line_out = fn.myprint(line, fn.i2h(pc, 4))
                list_out.write(line_out)   
            print(' ')
            if len(pass2_errors) == 0:
                print('Pass 2 Complete - No Errors Encountered')
            else:
                print('Pass 2 Complete - ', pass2_error_count, 'Error(s) Encountered')
            print(' ')
            print('Assembly Complete')
            break
        # handle Relative Address Mode Instructions    
        elif token_line[0] in relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token_line[1]) != None:
            oc = relative_address_mode_instructions[token_line[0]]
            x = int(label_dict[token_line[1]], 16) - pc
            if x > 127 or x < -128:
                pass2_errors[line_number] = f'Relative displacement out of range: {token_line}'
                print('Error on:', token_line, ' - Relative Displacement Out of Range')
            else:
                if x < 0:
                    disp = fn.cvtint2scomp(x-2)
                else:    
                    disp = hex(x-2)[2:].zfill(2)
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc, disp)
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc + disp             
                pc = pc + 2
        else:
            if len(token_line) == 2:
                operand = token_line[1]
                if not '$' in operand:
                    for p in address_mode_patterns_sym.keys():
                        z = re.fullmatch(p, operand)
                        if z != None:
                            mode = address_mode_patterns_sym[p]
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
                            if z != None:
                                f, t = z.span()
                                exp = label[f:t]
                                label = label[0:f]
                                lab_len = len(label_dict[label])
                                x = eval(str(int(label_dict[label], 16)) + exp)
                                if lab_len == 2 and x < 256:
                                    operand = '$' + fn.i2h(x, 2)
                                elif lab_len == 4 and x < 65536:
                                    operand = '$' + fn.i2h(x, 4)
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
                            
                am, nb, oc = fn.determine_mode(token_line[0], operand)
            elif len(token_line) == 1:
                am, nb, oc = fn.determine_mode(token_line[0], '')
                    
            if am == 'Implied' or am == 'Accumulator':
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc)
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc
            elif am == 'Immediate' or am == 'Indirect,X' or am == 'Indirect,Y':
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc, operand[2:4])
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc + operand[2:4]
            elif am == 'Zero Page' or am == 'Zero Page,X' or am == 'Zero Page,Y': 
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc, operand[1:3])
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc + operand[1:3]
            elif am == 'Absolute' or am == 'Absolute,X' or am == 'Absolute,Y':
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc, operand[3:5], operand[1:3])
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc + operand[3:5] + operand[1:3]
            elif am == 'Indirect':
                if write_list_file:
                    line_out = fn.myprint(line, fn.i2h(pc, 4), ':', oc, operand[4:6], operand[2:4])    
                    list_out.write(line_out)   
                code_dict[fn.i2h(pc, 4)] = oc + operand[4:6] + operand[2:4]
            pc = pc + nb

    if write_list_file:        
        list_out.close()

    if len(pass2_errors) > 0:
        print('Error(s) Encountered')
        print('Unable to Continue')
        raise AssemblerError('Error(s) in pass 2', pass2_errors) 
    
    return code_dict


    # create and write out the Intel hex file
    print(' ')
    print('Creating Intel hex file')
    file_out = file_name.split('.')[0] + '.hex'
    tot_bytes = 0
    tot_code = ''
    with open(file_out, 'w') as sfo:
        for address in code_dict:
            if tot_code  == '':
                iaddress = address
            code = code_dict[address]
            num_bytes = len(code) // 2
            next_address = hex(int(address, 16) + num_bytes).upper()[2:].zfill(4)
            tot_bytes += num_bytes
            tot_code += code
            if tot_bytes < 16 and next_address in code_dict:
                continue
            iline = ':' + hex(tot_bytes).upper()[2:].zfill(2) + iaddress + '00' + tot_code 
            x = iline[1:]
            y = [int(x[i:i+2],16) for i in range(0,len(x),2)]
            chksum = hex(256-sum(y) % 256)[2:].zfill(2).upper()
            if len(chksum) > 2:
                chksum = chksum[1:]
            iline += chksum + '\n'
            sfo.write(iline)
            tot_bytes = 0
            tot_code = ''

     