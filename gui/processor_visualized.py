from emulator.processor import Processor
from simulator import MainWindow

class ProcessorVisualization(Processor):
    def __init__(self, window:MainWindow):
        super().__init__()
        self.window= window

    def cycle(self):
        super().cycle()
        self.window.cycle_counter.setProperty('text', str(self.cycles))

    def fetch_byte(self, address: int) -> int:
        byte = super().fetch_byte(address)
        self.window.address_high_byte.setProperty('intValue', byte >> 8)
        self.window.address_low_byte.setProperty('intValue', byte & 0xff)
        return byte