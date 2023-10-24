from processor import Processor
from intelhex import IntelHex

def load_executable(filename:str, processor:Processor) -> None:
    hex_data = IntelHex(filename)
    data = hex_data.todict()
    for key, value in data.items():
        processor.memory.data[key] = value


if __name__ == '__main__':
    processor = Processor()
    load_executable('6502Asm/test1.hex', processor=processor)
    processor.PC = 0x0200
    while(processor.cycles < 1000):
        processor.run_instruction()