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


from PySide6.QtWidgets import QFrame, QLabel, QLCDNumber
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class RegisterMode:
    HEX = 16
    BIN = 2
    DEC = 10


class RegisterWidget(QLabel):
    mode = RegisterMode.HEX
    value = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setIndent(0)
        self.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.mode = QLCDNumber.Hex
        self.value = 0

    def setMode(self, mode):
        self.mode = mode
        self.setText(self.value)

    def setGeometry(self, qrect):
        super().setGeometry(qrect)
        font = QFont()
        font.setPointSize(3 * qrect.height() // 5)
        self.setFont(font)

    def setText(self, arg):
        if type(arg) == int:
            self.value = arg
            if self.mode == QLCDNumber.Mode.Hex:
                arg = f'${arg:02X}'
            elif self.mode == QLCDNumber.Mode.Bin:
                arg = f'%{arg:08b}'
            else:
                arg = str(arg)
        super().setText(arg)
