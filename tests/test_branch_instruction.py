import unittest
from emulator.processor import setup_processor
from emulator.opcodes import *


def test_branch_instruction(instruction:list[int], distance:int, flags:dict, branch:bool, num_cycles:int, register_data:dict={}) -> None:
    processor = setup_processor(instruction, data={}, registers=register_data, flags=flags)
    
    pc = processor.PC
    processor.run_instruction()
    
    if branch:
        assert processor.PC == pc + distance + len(instruction)
    else:
        assert processor.PC == pc + len(instruction)
    assert processor.cycles == num_cycles


def test_set_flag_instruction(instruction:list[int], flag:str, state:bool, flags:dict, num_cycles:int) -> None:
    processor = setup_processor(instruction, data={}, flags=flags)
    
    processor.run_instruction()
    
    assert processor.__getattribute__(flag) == state
    assert processor.cycles == num_cycles
  

class ProcessorTest(unittest.TestCase):
    def test_bcc_branched(self):
        test_branch_instruction([BCC, 132], distance=-124, flags={'C': False}, branch=True,
                                register_data={'PC': 0xf0}, num_cycles=3)

    def test_bcc_branched_cross_page_boundary(self):
        test_branch_instruction([BCC, 20], distance=20, flags={'C': False}, branch=True,
                                register_data={'PC': 0xf0}, num_cycles=4)

    def test_bcc_no_branch(self):
        test_branch_instruction([BCC, 253], distance=-3, flags={'C': True}, branch=False,
                                register_data={'PC':0xf0}, num_cycles=2)
    
    def test_bcs_branched(self):
        test_branch_instruction([BCS, 246], distance=-10, flags={'C': True}, branch=True,
                                register_data={'PC':0xf0}, num_cycles=3)

    def test_bcs_branched_cross_page_boundary(self):
        test_branch_instruction([BCS, 0x10], distance=0x10, flags={'C': True}, branch=True,
                                register_data={'PC':0xffa}, num_cycles=4)

    def test_bcs_no_branch(self):
        test_branch_instruction([BCS, 128], distance=-128, flags={'C': False}, branch=False,
                                register_data={'PC':0xf0}, num_cycles=2)
    
    def test_beq_branched(self):
        test_branch_instruction([BEQ, 128], distance=-128, flags={'Z': True}, branch=True,
                                register_data={'PC': 0xf0}, num_cycles=3)

    def test_beq_branched_cross_page_boundary(self):
        test_branch_instruction([BEQ, 128], distance=-128, flags={'Z': True}, branch=True,
                                register_data={'PC': 0xf10}, num_cycles=4)

    def test_beq_no_branch(self):
        test_branch_instruction([BEQ, 0x0], distance=0, flags={'Z': False}, branch=False,
                                register_data={'PC': 0xf0}, num_cycles=2)

    def test_bni_branched(self):
        test_branch_instruction([BMI, 0], distance=0, flags={'N': True}, branch=True,
                                register_data={'PC': 0xf0}, num_cycles=3)

    def test_bni_branched_cross_page_boundary(self):
        test_branch_instruction([BMI, 127], distance=127, flags={'N': True}, branch=True,
                                register_data={'PC': 0xf7f}, num_cycles=4)

    def test_bni_no_branch(self):
        test_branch_instruction([BMI, 128], distance=-128, flags={'N': False}, branch=False,
                                register_data={'PC': 0xf0}, num_cycles=2)

    def test_bne_branched(self):
        test_branch_instruction([BNE, 128], distance=-128, flags={'Z': False}, branch=True,
                                register_data={'PC': 0xf0}, num_cycles=3)

    def test_bne_branched_cross_page_boundary(self):
        test_branch_instruction([BNE, 128], distance=-128, flags={'Z': False},
                                branch=True, register_data={'PC': 0xff}, num_cycles=4)

    def test_bne_no_branch(self):
        test_branch_instruction([BNE, 255], distance=-1, flags={'Z': True},
                                branch=False, register_data={'PC': 0xf0}, num_cycles=2)

    def test_bpl_branched(self):
        test_branch_instruction([BPL, 255], distance=-1, flags={'N': False}, branch=True,
                                register_data={'PC': 0xff}, num_cycles=3)

    def test_bpl_branched_cross_page_boundary(self):
        test_branch_instruction([BPL, 255], distance=-1, flags={'N': False}, branch=True,
                                register_data={'PC':0xfe}, num_cycles=4)

    def test_bpl_no_branch(self):
        test_branch_instruction([BPL, 1], distance=1, flags={'N': True}, branch=False,
                                register_data={'PC': 0xf0}, num_cycles=2)

    def test_bvc_branched(self):
        test_branch_instruction([BVC, 1], distance=1, flags={'V': False}, branch=True,
                                register_data={'PC': 0xfc}, num_cycles=3)

    def test_bvc_branched_cross_page_boundary(self):
        test_branch_instruction([BVC, 1], distance=1, flags={'V': False}, branch=True,
                                register_data={'PC': 0xffd}, num_cycles=4)

    def test_bvc_no_branch(self):
        test_branch_instruction([BVC, 127], distance=127, flags={'V': True}, branch=False,
                                register_data={'PC': 0xf0}, num_cycles=2)

    def test_bvs_branched(self):
        test_branch_instruction([BVS, 127], distance=127, flags={'V': True}, branch=True,
                                register_data={'PC': 0x7e}, num_cycles=3)

    def test_bvs_branched_cross_page_boundary(self):
        test_branch_instruction([BVS, 127], distance=127, flags={'V': True}, branch=True,
                                register_data={'PC':0x27f}, num_cycles=4)

    def test_bvs_no_branch(self):
        test_branch_instruction([BVS, 0], distance=0, flags={'V': False}, branch=False,
                                register_data={'PC': 0xf0}, num_cycles=2)

    def test_clc(self):
        test_set_flag_instruction([CLC], flag='C', state=False, flags={'C': True}, num_cycles=2)

    def test_cld(self):
        test_set_flag_instruction([CLD], flag='D', state=False, flags={'D': True}, num_cycles=2)

    def test_cli(self):
        test_set_flag_instruction([CLI], flag='I', state=False, flags={'I': True}, num_cycles=2)  

    def test_clv(self):
        test_set_flag_instruction([CLV], flag='V', state=False, flags={'V': False}, num_cycles=2)  

    def test_sec(self):
        test_set_flag_instruction([SEC], flag='C', state=True, flags={'C': False}, num_cycles=2)

    def test_sed(self):
        test_set_flag_instruction([SED], flag='D', state=True, flags={'D': False}, num_cycles=2)  

    def test_sei(self):
        test_set_flag_instruction([SEI], flag='I', state=True, flags={'I': True}, num_cycles=2)  


if __name__ == '__main__':
    unittest.main()
