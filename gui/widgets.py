from PySide6.QtWidgets import QFrame, QLabel, QLCDNumber
from PySide6.QtGui import QPainter, QPaintEvent, QPen, QColor, QFont
from PySide6.QtCore import  Qt


# class ComputerFrame(QFrame):
#     def paintEvent(self, event: QPaintEvent) -> None:
#         painter = QPainter(self)
#         self.paint_bus(painter)
#         painter.end()
#         return super().paintEvent(event)
#
#     @staticmethod
#     def paint_bus(painter: QPainter):
#         pen = QPen()
#         pen.setColor(QColor(180, 20, 50))
#         pen.setWidth(4)
#         painter.setPen(pen)
#         painter.setWindow(0, 0, 950, 870)
#         painter.setViewport(20, -70, 970, 940)
#         painter.drawLine(Points.sr, Points.c1)
#         painter.drawLine(Points.pc, Points.c2)
#         painter.drawLine(Points.ar_i, Points.c10)
#         painter.drawLine(Points.ac, Points.c4)
#         painter.drawLine(Points.ix, Points.al_i1)
#         painter.drawLine(Points.iy, Points.c6)
#         painter.drawLine(Points.sp, Points.al_i2)
#         painter.drawLine(Points.al_o, Points.c9)
#         # Vertical lines
#         painter.drawLine(Points.c1, Points.c3)
#         painter.drawLine(Points.c4, Points.c8)
#         painter.drawLine(Points.ir, Points.dat)
#         painter.drawLine(Points.ar_o, Points.mem)


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

    def setGeometry(self, qrect):
        super().setGeometry(qrect)
        font = QFont()
        font.setPointSize(3 * qrect.height() // 5)
        self.setFont(font)

    # def setProperty(self, prop, value):
    #     self.value = value
    #     self.display()

    def setText(self, arg):
        if type(arg) == int:
            if self.mode == QLCDNumber.Hex:
                arg = f'${arg:02X}'
            elif self.mode == QLCDNumber.Bin:
                arg = f'^{arg:08b}'
            else:
                arg = str(arg)
        super().setText(arg)
