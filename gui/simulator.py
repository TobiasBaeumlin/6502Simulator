import sys
import signal
from PySide6 import QtWidgets
from gui.simulator_gui import Simulator


def SIGSEGV_signal_arises(signalNum, stack): pass


signal.signal(signal.SIGSEGV, SIGSEGV_signal_arises)

app = QtWidgets.QApplication(sys.argv)

window = Simulator()

window.show()
app.exec()

