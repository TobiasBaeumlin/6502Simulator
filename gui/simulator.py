import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QLCDNumber, QInputDialog)
from emulator.processor import Processor
from emulator.operators import set_bit
from mainwindow import Ui_MainWindow
from functools import partial
from intelhex import IntelHex  
import io      

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.assembler_file_name = ''
        self.program_counter_frame.mousePressEvent = self.set_program_counter
        
        for reg in range(0x100):
            widget = self.__getattribute__(f'reg{reg:02X}')
            widget.mousePressEvent = partial(self.set_register, reg)
        self.step_button.clicked.connect(self.step_button_clicked)
        self.reset_button.clicked.connect(self.reset_button_clicked)
        self.assemble_button.clicked.connect(self.assemble_button_clicked)
        self.open_file.clicked.connect(self.open_assembler_file_clicked)
        self.save_file.clicked.connect(self.save_assembler_file_clicked)
        self.save_file_as.clicked.connect(self.save_assembler_file_as_clicked)


    def set_decimal_mode(self):
        for r in range(0x100):
            self.__getattribute__(f'reg{r:02X}').setMode(QLCDNumber.Dec)
        self.program_counter_high_byte.setMode(QLCDNumber.Dec)        
        self.program_counter_low_byte.setMode(QLCDNumber.Dec)        
        self.accumulator.setMode(QLCDNumber.Dec)        
        self.index_x.setMode(QLCDNumber.Dec)        
        self.index_y.setMode(QLCDNumber.Dec)      
        self.stack_pointer.setMode(QLCDNumber.Dec)               

    def set_hex_mode(self):
        for r in range(0x100):
            self.__getattribute__(f'reg{r:02X}').setMode(QLCDNumber.Hex)       
        self.program_counter_high_byte.setMode(QLCDNumber.Hex)        
        self.program_counter_low_byte.setMode(QLCDNumber.Hex)        
        self.accumulator.setMode(QLCDNumber.Hex)        
        self.index_x.setMode(QLCDNumber.Hex)        
        self.index_y.setMode(QLCDNumber.Hex)      
        self.stack_pointer.setMode(QLCDNumber.Hex)  

    def set_program_counter(self, s):
        text, ok = QInputDialog.getText(
            self, "Set Program Counter", "Address:")    
        if ok and text:
            try:
                address = int(text, 16)
            except ValueError:
                pass
            if 0<=address<=0xffff:
                self.processor.PC = address
            else:
                pass
    
    def set_register(self, reg, s):
        text, ok = QInputDialog.getText(self, f'Set Memory Address {reg:04X}', 'Value:')    
        if ok and text:
            if text.startswith('0x') or text.startswith('#'):
                try:
                    value = int(text, 16)
                except ValueError:
                    value = -1
            else:
                try:
                    value = int(text, 10)
                except ValueError:
                    value = -1
            
            if 0<=value<=0xff:
                address = (self.processor.current_page << 8) + reg
                self.processor.memory.data[address] = value
                self.__getattribute__(f'reg{reg:02x}').setProperty('intValue', value)
            else:
                pass

    def step_button_clicked(self):
        self.processor.run_instruction()

    def reset_button_clicked(self):
        self.processor.reset()

    def assemble_button_clicked(self):
        if not self.assembler_file_name:
            self.save_assembler_file_as_clicked()
        
        hex_data = IntelHex(self.assembler_file_name + '.hex')
        data = hex_data.todict()
        for key, value in data.items():
            processor.memory.data[key] = value
   


    def open_assembler_file_clicked(self):
        pass

    def save_assembler_file_clicked(self):
        pass

    def save_assembler_file_as_clicked(self):
        pass


class ProcessorVisualization(Processor):
    def __init__(self, window:MainWindow):
        super().__init__()
        self.window = window
        self.window.processor:Processor = self
        self.single_cycle = False              # Do not stop after each cycle
        self.cycle_delay = 100                 # Wait for 100ms after each cycle  
        self.shown_page = 0
        self.shown_page_row = 0
        self.shown_page_col = 0
        self._current_page = 0
        window.set_hex_mode()

    @property
    def current_page(self):
        return self._current_page
    
    @ current_page.setter
    def current_page(self, value):
        assert 0 <= value <0x100
        self._current_page = value
        self.show_page(value)
        self.window.page.setText(f'{value:02X}')

    @ Processor.CI.setter
    def CI(self, value):
        self.current_instruction = value
        self.window.current_instruction.setText(value)

    @ Processor.PC.setter
    def PC(self, value):
        self.window.program_counter_high_byte.setProperty('intValue', value >> 8)
        self.window.program_counter_low_byte.setProperty('intValue', value & 0xff)
        self.window.current_address.setText(f'{value:04X}')
        self.show_memory_address(value)
        self.program_counter.set_value(value)   

    @ Processor.SP.setter
    def SP(self, value):
        self.window.stack_pointer.setProperty('intValue', value)
        self.stack_pointer.set_value(value)

    @ Processor.A.setter
    def A(self, value):
        self.window.accumulator.setProperty('intValue', value)
        self.window.accumulator_binary.setProperty('intValue', value)
        self.accumulator.set_value(value)

    @ Processor.X.setter
    def X(self, value):
        self.window.index_x.setProperty('intValue', value)
        self.index_x.set_value(value)

    @ Processor.Y.setter
    def Y(self, value):
        self.window.index_y.setProperty('intValue', value)
        self.index_y.set_value(value)

    @ Processor.C.setter
    def C(self, value):
        self.window.flag_c.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 0, value)

    @ Processor.Z.setter
    def Z(self, value):
        self.window.flag_z.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 1, value)
    
    @ Processor.I.setter
    def I(self, value):
        self.window.flag_i.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 2, value)
    
    @ Processor.D.setter
    def D(self, value):
        self.window.flag_d.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 3, value)
    
    @ Processor.B.setter
    def B(self, value):
        self.window.flag_b.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 4, value)

    @ Processor.V.setter
    def V(self, value):
        self.window.flag_v.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 6, value)

    @ Processor.N.setter
    def N(self, value):
        self.window.flag_d.setProperty('intValue', value)
        self.status.value = set_bit(self.status.value, 7, value)

    def show_page(self, page):
        if page == self.shown_page:
            return
        for c in range(0x10):
            self.set_page_row_color(c, 'black')
            self.set_page_col_color(c, 'black')
            
        for r in range(0x100):
            byte = self.memory.data[(page << 8) + r]
            self.window.__getattribute__(f'reg{r:02X}').setProperty('intValue', byte)
        self.window.page.setText( f'{page:2X}')
        self.shown_page = page

    def set_page_row_color(self, row, color):
        self.window.__getattribute__(f'page_row_{row:1X}').setStyleSheet(f'color: {color}')

    def set_page_col_color(self, col, color):
        self.window.__getattribute__(f'page_col_{col:1X}').setStyleSheet(f'color: {color}')

    def show_memory_address(self, address:int):
        page = address >> 8
        reg = address & 0xff
        if page != self.shown_page:
            self.show_page(page)
        row = (address & 0xf0) >> 4
        col = address & 0x0f
        if self.shown_page== page and self.shown_page_row == row and self.shown_page_col == col:
            return
        self.set_page_row_color(self.shown_page_row, 'red')
        self.set_page_col_color(self.shown_page_col, 'red') 
        self.set_page_row_color(row, 'red')
        self.set_page_col_color(col, 'red')
        self.shown_page_col = col
        self.shown_page_row = row
        byte = self.memory.data[(page << 8) + reg]
        self.window.__getattribute__(f'reg{reg:02X}').setProperty('intValue', byte)
        self.window.page.setText( f'{(address>>8):02X}')
        
        
    
    def cycle(self):
        super().cycle()
        self.window.cycle_counter.setText(str(self.cycles))

    def fetch_byte(self, address: int) -> int:
        byte = super().fetch_byte(address)
        self.show_memory_address(address)
        self.window.data.setText(f'{byte:02x}')
        return byte
    
    def put_byte(self, address: int, byte: int) -> None:
        super().put_byte(address, byte)
        self.show_memory_address(address)
        self.window.data.setText(f'{byte:02x}')     






app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
processor = ProcessorVisualization(window)
processor.reset()
window.show()
app.exec()





