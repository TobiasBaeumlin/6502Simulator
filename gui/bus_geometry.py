from PySide6.QtCore import QPoint


class AnimationCoord:
    x1 = 50
    x2 = 260
    x3 = 480
    x4 = 610
    x5 = 690
    x6 = 1000
    x7 = 1045
    x8 = 1240

    y0 = 80
    y1 = 120
    y2 = 200
    y3 = 290
    y4 = 370
    y5 = 420
    y6 = 470
    y7 = 500
    y8 = 530

    dx_1 = 40
    dx_2 = 67
    dx_3 = 102

    dy = 30


AnimationPoints = {
    # Crossing points processor bus
    'pb0': QPoint(AnimationCoord.x1, AnimationCoord.y4),
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
    'ab0': QPoint(AnimationCoord.x1, AnimationCoord.y2),
    'ab1': QPoint(AnimationCoord.x1, AnimationCoord.y3),
    'ab2': QPoint(AnimationCoord.x1, AnimationCoord.y5),
    'ab3': QPoint(AnimationCoord.x5, AnimationCoord.y5),
    'ab4': QPoint(AnimationCoord.x7, AnimationCoord.y5),
    # Data bus
    'db0': QPoint(AnimationCoord.x2, AnimationCoord.y6),
    'db1': QPoint(AnimationCoord.x3, AnimationCoord.y6),
    'db2': QPoint(AnimationCoord.x4, AnimationCoord.y6),
    'db3': QPoint(AnimationCoord.x6, AnimationCoord.y6),
    'db4': QPoint(AnimationCoord.x8, AnimationCoord.y6),
    # Connecting points processor
    'sr': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y1),
    'pcd': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y2),   # program counter data
    'pca': QPoint(AnimationCoord.x1 + AnimationCoord.dx_1, AnimationCoord.y2),   # program counter address
    'sp': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y3),
    'a': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y0),
    'a2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_1, AnimationCoord.y1),
    'x': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y2),
    'x2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_2, AnimationCoord.y2),
    'y': QPoint(AnimationCoord.x3 - AnimationCoord.dx_1, AnimationCoord.y3),
    'y2': QPoint(AnimationCoord.x2 + AnimationCoord.dx_2, AnimationCoord.y3),
    'op1': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y0),
    'op2': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y1),
    'res': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y2),
    'ir': QPoint(AnimationCoord.x3 + AnimationCoord.dx_1, AnimationCoord.y4),
    # Address register and bus
    'ard': QPoint(AnimationCoord.x2 - AnimationCoord.dx_1, AnimationCoord.y3),   # address register data
    'ara': QPoint(AnimationCoord.x1 + AnimationCoord.dx_1, AnimationCoord.y3),   # address register address
    'ma': QPoint(AnimationCoord.x1, AnimationCoord.y7),
    'md': QPoint(AnimationCoord.x4, AnimationCoord.y8),
    'za': QPoint(AnimationCoord.x5, AnimationCoord.y7),
    'zd': QPoint(AnimationCoord.x8, AnimationCoord.y8),
    'sa': QPoint(AnimationCoord.x7, AnimationCoord.y5 - AnimationCoord.dy),
    'sd': QPoint(AnimationCoord.x6, AnimationCoord.x3)
}

AnimationPaths = {
    'A': {},                      # Accumulator
    'X': {},                      # Index X
    'Y': {},
    'SR': {},                     # Status register
    'PC': {},                     # Program counter
    'S': {},                     # Stack pointer
    'RES': {},
    'AR': {},
    'MD': {},
    'MA': {},
    'ZD': {},
    'ZA': {},
    'IR': {},
    'C': {},
    'N': {},
}

AnimationPaths['MD']['A'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                             AnimationPoints['pb5'], AnimationPoints['a']]
AnimationPaths['MD']['IR'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                              AnimationPoints['pb9'], AnimationPoints['ir']]
AnimationPaths['MD']['X'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                             AnimationPoints['pb7'], AnimationPoints['x']]
AnimationPaths['MD']['Y'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                             AnimationPoints['pb8'], AnimationPoints['y']]
AnimationPaths['MD']['OP1'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                               AnimationPoints['pb5'], AnimationPoints['op1']]
AnimationPaths['MD']['OP2'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]
AnimationPaths['MD']['PC'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db0'],
                              AnimationPoints['pb2'], AnimationPoints['pcd']]
AnimationPaths['MD']['PCL'] = AnimationPaths['MD']['PC']
AnimationPaths['MD']['PCH'] = AnimationPaths['MD']['PC']

AnimationPaths['ZD']['A'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                             AnimationPoints['pb5'], AnimationPoints['a']]
AnimationPaths['ZD']['IR'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                              AnimationPoints['pb9'], AnimationPoints['ir']]
AnimationPaths['ZD']['X'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                             AnimationPoints['pb7'], AnimationPoints['x']]
AnimationPaths['ZD']['Y'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                             AnimationPoints['pb8'], AnimationPoints['y']]
AnimationPaths['ZD']['OP1'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                               AnimationPoints['pb5'], AnimationPoints['op1']]
AnimationPaths['ZD']['OP2'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db1'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]
AnimationPaths['ZD']['PC'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db0'],
                              AnimationPoints['pb2'], AnimationPoints['pcd']]

AnimationPaths['A']['MD'] = list(reversed(AnimationPaths['MD']['A']))
AnimationPaths['A']['ZD'] = list(reversed(AnimationPaths['ZD']['A']))
AnimationPaths['A']['X'] = [AnimationPoints['a'], AnimationPoints['pb5'], AnimationPoints['pb7'],
                            AnimationPoints['x']]
AnimationPaths['A']['Y'] = [AnimationPoints['a'], AnimationPoints['pb5'], AnimationPoints['pb8'],
                            AnimationPoints['y']]
AnimationPaths['A']['OP1'] = [AnimationPoints['a'], AnimationPoints['op1']]
AnimationPaths['A']['SR'] = [AnimationPoints['a2'], AnimationPoints['sr']]

AnimationPaths['X']['A'] = list(reversed(AnimationPaths['A']['X']))
AnimationPaths['X']['MD'] = list(reversed(AnimationPaths['MD']['X']))
AnimationPaths['X']['ZD'] = list(reversed(AnimationPaths['ZD']['X']))
AnimationPaths['X']['S'] = [AnimationPoints['x'], AnimationPoints['pb7'], AnimationPoints['pb8'],
                             AnimationPoints['sp']]
AnimationPaths['X']['SR'] = [AnimationPoints['x2'], AnimationPoints['pb2'], AnimationPoints['pb1'],
                             AnimationPoints['sr']]

AnimationPaths['Y']['A'] = list(reversed(AnimationPaths['A']['Y']))
AnimationPaths['Y']['MD'] = list(reversed(AnimationPaths['MD']['Y']))
AnimationPaths['Y']['ZD'] = list(reversed(AnimationPaths['ZD']['Y']))
AnimationPaths['Y']['SR'] = [AnimationPoints['y2'], AnimationPoints['pb3'], AnimationPoints['pb1'],
                             AnimationPoints['sr']]

AnimationPaths['RES']['MD'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['db1'],
                               AnimationPoints['db2'], AnimationPoints['md']]
AnimationPaths['RES']['ZD'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['db1'],
                               AnimationPoints['db4'], AnimationPoints['zd']]
AnimationPaths['RES']['A'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['pb5'],
                              AnimationPoints['a']]
AnimationPaths['RES']['SR'] = [AnimationPoints['res'], AnimationPoints['pb7'], AnimationPoints['pb9'],
                               AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['PC']['AR'] = [AnimationPoints['pca'], AnimationPoints['ab0'], AnimationPoints['ab1'],
                              AnimationPoints['ara']]
AnimationPaths['PC']['MD'] = [AnimationPoints['pcd'], AnimationPoints['pb2'], AnimationPoints['db0'],
                              AnimationPoints['db2'], AnimationPoints['md']]
AnimationPaths['PC']['ZD'] = [AnimationPoints['pcd'], AnimationPoints['pb2'], AnimationPoints['db0'],
                              AnimationPoints['db4'], AnimationPoints['zd']]
AnimationPaths['PC']['ZA'] = [AnimationPoints['pca'], AnimationPoints['ab0'], AnimationPoints['ab2'],
                              AnimationPoints['ab3'], AnimationPoints['za']]
AnimationPaths['PC']['MA'] = [AnimationPoints['pca'], AnimationPoints['ab0'], AnimationPoints['ma']]
AnimationPaths['PC']['SA'] = [AnimationPoints['pca'], AnimationPoints['ab0'], AnimationPoints['ab2'],
                              AnimationPoints['ab4'], AnimationPoints['sa']]

AnimationPaths['AR']['MA'] = [AnimationPoints['ara'], AnimationPoints['ab1'], AnimationPoints['ma']]
AnimationPaths['AR']['ZA'] = [AnimationPoints['ara'], AnimationPoints['ab1'], AnimationPoints['ab2'],
                              AnimationPoints['ab3'], AnimationPoints['za']]
AnimationPaths['AR']['SA'] = [AnimationPoints['ara'], AnimationPoints['ab1'], AnimationPoints['ab2'],
                              AnimationPoints['ab4'], AnimationPoints['sa']]

AnimationPaths['IR']['SR'] = [AnimationPoints['ir'], AnimationPoints['pb9'], AnimationPoints['pb4'],
                              AnimationPoints['pb1'], AnimationPoints['sr']]
AnimationPaths['IR']['OP2'] = [AnimationPoints['ir'], AnimationPoints['pb8'], AnimationPoints['pb6'],
                               AnimationPoints['op2']]

AnimationPaths['MD']['OP2'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db1'],
                               AnimationPoints['pb6'], AnimationPoints['op2']]

AnimationPaths['ZD']['AR'] = [AnimationPoints['zd'], AnimationPoints['db4'], AnimationPoints['db0'],
                              AnimationPoints['pb3'], AnimationPoints['ara']]
AnimationPaths['ZD']['ARL'] = AnimationPaths['ZD']['AR']
AnimationPaths['ZD']['ARH'] = AnimationPaths['ZD']['AR']
AnimationPaths['MD']['AR'] = [AnimationPoints['md'], AnimationPoints['db2'], AnimationPoints['db0'],
                              AnimationPoints['pb3'], AnimationPoints['ara']]
AnimationPaths['MD']['ARL'] = AnimationPaths['ZD']['AR']
AnimationPaths['MD']['ARH'] = AnimationPaths['ZD']['AR']

AnimationPaths['S']['X'] = list(reversed(AnimationPaths['X']['S']))
AnimationPaths['S']['SR'] = [AnimationPoints['sp'], AnimationPoints['pb8'], AnimationPoints['pb9'],
                             AnimationPoints['pb4'], AnimationPoints['pb1'], AnimationPoints['sr']]

AnimationPaths['SR']['OP2'] = [AnimationPoints['sr'], AnimationPoints['pb1'], AnimationPoints['pb4'],
                               AnimationPoints['pb9'], AnimationPoints['pb6'], AnimationPoints['op2']]
AnimationPaths['C']['OP2'] = AnimationPaths['SR']['OP2']
