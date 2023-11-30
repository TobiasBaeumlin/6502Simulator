import sys
import signal
from PySide6 import QtWidgets
from gui.processor_visualization import *
from gui.simulator_gui import MainWindow


def SIGSEGV_signal_arises(signalNum, stack): pass


signal.signal(signal.SIGSEGV, SIGSEGV_signal_arises)

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()

window.show()
app.exec()





