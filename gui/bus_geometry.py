from PySide6.QtCore import QPoint


# class FrameCoord:
#     x0 = 50
#     x1 = 224
#     x2 = 400
#     x3 = 654
#     y1 = 170
#     y2 = 235
#     y3 = 290
#     y4 = 350
#     y5 = 440
#     y6 = 560
#     dx_1 = 24
#     dx_2 = 67
#     dx_3 = 102
#
#     dy = 30
#
#
# class Points:
#     # Crossing points
#     c1 = QPoint(FrameCoord.x1, FrameCoord.y1)
#     c2 = QPoint(FrameCoord.x1, FrameCoord.y3)
#     c3 = QPoint(FrameCoord.x1, FrameCoord.y5)
#     c4 = QPoint(FrameCoord.x2, FrameCoord.y1)
#     c5 = QPoint(FrameCoord.x2, FrameCoord.y2)
#     c6 = QPoint(FrameCoord.x2, FrameCoord.y3)
#     c7 = QPoint(FrameCoord.x2, FrameCoord.y4)
#     c8 = QPoint(FrameCoord.x2, FrameCoord.y5)
#     c9 = QPoint(FrameCoord.x3, FrameCoord.y2)
#     c10 = QPoint(FrameCoord.x3, FrameCoord.y5)
#     # Connecting points
#     sr = QPoint(FrameCoord.x1 - FrameCoord.dx_1, FrameCoord.y1)
#     pc = QPoint(FrameCoord.x1 - FrameCoord.dx_1, FrameCoord.y3)
#     ai = QPoint(FrameCoord.x1 - FrameCoord.dx_1, FrameCoord.y5)
#     ao = QPoint(FrameCoord.x0, FrameCoord.y5)
#     ac = QPoint(FrameCoord.x2 - FrameCoord.dx_1, FrameCoord.y1)
#     ix = QPoint(FrameCoord.x2 - FrameCoord.dx_1, FrameCoord.y2)
#     iy = QPoint(FrameCoord.x2 - FrameCoord.dx_1, FrameCoord.y3)
#     sp = QPoint(FrameCoord.x2 - FrameCoord.dx_1, FrameCoord.y4)
#     al_i1 = QPoint(FrameCoord.x2 + FrameCoord.dx_2, FrameCoord.y2)
#     al_i2 = QPoint(FrameCoord.x2 + FrameCoord.dx_2, FrameCoord.y4)
#     al_o = QPoint(FrameCoord.x3 - FrameCoord.dx_3, FrameCoord.y2)
#     ir = QPoint(FrameCoord.x3, FrameCoord.y1 + FrameCoord.dy)
#     dat = QPoint(FrameCoord.x3, FrameCoord.y6 - FrameCoord.dy)
#     mem = QPoint(FrameCoord.x0, FrameCoord.y6 - FrameCoord.dy)
#

class AnimationCoord:
    x0 = 50
    x1 = 95
    x2 = 260
    x3 = 480
    x4 = 680
    x5 = 725
    x6 = 805
    x7 = 1000
    x8 = 1045

    y0 = 80
    y1 = 120
    y2 = 200
    y3 = 290
    y4 = 340
    y5 = 400
    y6 = 430
    y7 = 470
    y8 = 530

    dx_1 = 40
    dx_2 = 67
    dx_3 = 102

    dy = 30


AnimationPoints = {
    # Crossing points processor bus
    'pb1': QPoint(AnimationCoord.x2, AnimationCoord.y1),
    'pb2': QPoint(AnimationCoord.x2, AnimationCoord.y2),
    'pb3': QPoint(AnimationCoord.x2, AnimationCoord.y3),
    'pb4': QPoint(AnimationCoord.x2, AnimationCoord.y4),
    'pb5': QPoint(AnimationCoord.x3, AnimationCoord.y0),
    'pb6': QPoint(AnimationCoord.x3, AnimationCoord.y1),
    'pb7': QPoint(AnimationCoord.x3, AnimationCoord.y2),
    'pb8': QPoint(AnimationCoord.x3, AnimationCoord.y3),
    'pb9': QPoint(AnimationCoord.x3, AnimationCoord.y4),
    # Address bus
    'ab1': QPoint(AnimationCoord.x1, AnimationCoord.y5),
    'ab2': QPoint(AnimationCoord.x5, AnimationCoord.y5),
    'ab3': QPoint(AnimationCoord.x6, AnimationCoord.y5),
    'ab4': QPoint(AnimationCoord.x8, AnimationCoord.y5),
    # Data bus
    'db1': QPoint(AnimationCoord.x0, AnimationCoord.y6),
    'db2': QPoint(AnimationCoord.x2, AnimationCoord.y6),
    'db3': QPoint(AnimationCoord.x3, AnimationCoord.y6),
    'db4': QPoint(AnimationCoord.x4, AnimationCoord.y6),
    'db5': QPoint(AnimationCoord.x7, AnimationCoord.y6),
    # Connecting points processor
    'sr': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y1),
    'pc': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y2),
    'sp': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y3),
    'a': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y0),
    'a2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_1, AnimationCoord.y0),
    'x': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y2),
    'x2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_2, AnimationCoord.y2),
    'y': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y3),
    'y2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_2, AnimationCoord.y3),
    'op1': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y0),
    'op2': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y1),
    'res': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y2),
    'ir': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y3),
    # Address register and bus
    'ai': QPoint(AnimationCoord.x6 - AnimationCoord.dx_2, AnimationCoord.y4),
    'ao': QPoint(AnimationCoord.x6, AnimationCoord.y5 - AnimationCoord.dy),
    'ma': QPoint(AnimationCoord.x1, AnimationCoord.y8),
    'md': QPoint(AnimationCoord.x0, AnimationCoord.y7),
    'za': QPoint(AnimationCoord.x5, AnimationCoord.y8),
    'zd': QPoint(AnimationCoord.x4, AnimationCoord.y7),
    'sa': QPoint(AnimationCoord.x8, AnimationCoord.y4 + AnimationCoord.dy),
    'sd': QPoint(AnimationCoord.x7, AnimationCoord.x4)
}

AnimationPaths = {
    'A': {},
    'X': {},
    'Y': {},
    'PC': {},
    'SP': {},
    'CI': {},
    'RES': {},
    'AR': {},
    'MD': {},
    'MA': {},
    'ZD': {},
    'ZA': {},
    'IR': {}
}

AnimationPaths['MD']['A'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                             AnimationPoints['pb5'], AnimationPoints['a']]
AnimationPaths['MD']['IR'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                              AnimationPoints['pb8'], AnimationPoints['ir']]
AnimationPaths['MD']['X'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                             AnimationPoints['pb7'], AnimationPoints['x']]
AnimationPaths['MD']['Y'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                             AnimationPoints['pb8'], AnimationPoints['y']]
AnimationPaths['MD']['OP1'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                               AnimationPoints['pb5'], AnimationPoints['op1']]
AnimationPaths['MD']['OP2'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]
AnimationPaths['MD']['PC'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db2'],
                              AnimationPoints['pb2'], AnimationPoints['pc']]
AnimationPaths['MD']['PCL'] = AnimationPaths['MD']['PC']
AnimationPaths['MD']['PCH'] = AnimationPaths['MD']['PC']

AnimationPaths['ZD']['A'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                             AnimationPoints['pb5'], AnimationPoints['a']]
AnimationPaths['ZD']['IR'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                              AnimationPoints['pb8'], AnimationPoints['ir']]
AnimationPaths['ZD']['X'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                             AnimationPoints['pb7'], AnimationPoints['x']]
AnimationPaths['ZD']['Y'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                             AnimationPoints['pb8'], AnimationPoints['y']]
AnimationPaths['ZD']['OP1'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                               AnimationPoints['pb5'], AnimationPoints['op1']]
AnimationPaths['ZD']['OP2'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db3'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]
AnimationPaths['ZD']['PC'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db2'],
                              AnimationPoints['pb2'], AnimationPoints['pc']]

AnimationPaths['A']['MD'] = list(reversed(AnimationPaths['MD']['A']))
AnimationPaths['A']['ZD'] = list(reversed(AnimationPaths['ZD']['A']))
AnimationPaths['A']['X'] = [AnimationPoints['a'], AnimationPoints['pb5'], AnimationPoints['pb7'],
                            AnimationPoints['x']]
AnimationPaths['A']['Y'] = [AnimationPoints['a'], AnimationPoints['pb5'], AnimationPoints['pb8'],
                            AnimationPoints['y']]
AnimationPaths['A']['OP1'] = [AnimationPoints['a'], AnimationPoints['op1']]
AnimationPaths['A']['SR'] = [AnimationPoints['a'], AnimationPoints['pb5'], AnimationPoints['pb9'],
                             AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['X']['A'] = list(reversed(AnimationPaths['A']['X']))
AnimationPaths['X']['MD'] = list(reversed(AnimationPaths['MD']['X']))
AnimationPaths['X']['ZD'] = list(reversed(AnimationPaths['ZD']['X']))
AnimationPaths['X']['SP'] = [AnimationPoints['x'], AnimationPoints['pb7'], AnimationPoints['pb9'],
                             AnimationPoints['pb4'], AnimationPoints['pb3'], AnimationPoints['sp']]
AnimationPaths['X']['SR'] = [AnimationPoints['x'], AnimationPoints['pb7'], AnimationPoints['pb9'],
                             AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['Y']['A'] = list(reversed(AnimationPaths['A']['Y']))
AnimationPaths['Y']['MD'] = list(reversed(AnimationPaths['MD']['Y']))
AnimationPaths['Y']['ZD'] = list(reversed(AnimationPaths['ZD']['Y']))
AnimationPaths['Y']['SR'] = [AnimationPoints['y'], AnimationPoints['pb8'], AnimationPoints['pb9'],
                             AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['RES']['MD'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['db3'],
                               AnimationPoints['db1'], AnimationPoints['md']]
AnimationPaths['RES']['ZD'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['db3'],
                               AnimationPoints['db4'], AnimationPoints['zd']]
AnimationPaths['RES']['A'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['pb5'],
                              AnimationPoints['a']]
AnimationPaths['RES']['SR'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['pb9'],
                               AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['PC']['AR'] = [AnimationPoints['pc'], AnimationPoints['pb2'], AnimationPoints['pb4'],
                              AnimationPoints['ai']]
AnimationPaths['PC']['MD'] = [AnimationPoints['pc'], AnimationPoints['pb2'], AnimationPoints['db2'],
                              AnimationPoints['db2'], AnimationPoints['md']]
AnimationPaths['PC']['ZD'] = [AnimationPoints['pc'], AnimationPoints['pb2'], AnimationPoints['db2'],
                              AnimationPoints['db4'], AnimationPoints['zd']]

AnimationPaths['SP']['X'] = list(reversed(AnimationPaths['X']['SP']))

AnimationPaths['AR']['MA'] = [AnimationPoints['ao'], AnimationPoints['ab3'], AnimationPoints['ab1'],
                              AnimationPoints['ma']]
AnimationPaths['AR']['ZA'] = [AnimationPoints['ao'], AnimationPoints['ab3'], AnimationPoints['ab2'],
                              AnimationPoints['za']]

AnimationPaths['IR']['SR'] = [AnimationPoints['ir'], AnimationPoints['pb8'], AnimationPoints['pb9'],
                              AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]
AnimationPaths['IR']['AR'] = [AnimationPoints['ir'], AnimationPoints['pb8'], AnimationPoints['pb9'],
                              AnimationPoints['ai']]
AnimationPaths['IR']['OP2'] = [AnimationPoints['ir'], AnimationPoints['pb8'], AnimationPoints['pb6'],
                               AnimationPoints['op2']]

AnimationPaths['MD']['OP2'] = [AnimationPoints['md'], AnimationPoints['db1'], AnimationPoints['db3'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]
