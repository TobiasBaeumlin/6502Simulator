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


from PySide6.QtCore import QSequentialAnimationGroup, QPropertyAnimation, QRect, QPoint
from PySide6.QtWidgets import QLabel


def segment_length(point_a: QPoint, point_b: QPoint) -> int:
    return abs(point_a.x() - point_b.x()) + abs(point_a.y()-point_b.y())


def build_animation(data_transfer, gui):
    animation = build_path_animation(data_transfer, gui)
    for animator in gui.animators:
        animator.show()
    return animation


def build_path_animation(transfer, gui):
    path = transfer['path']
    data = transfer['data']

    path_length = 0
    for i in range(len(path) - 1):
        path_length += segment_length(path[i], path[i + 1])

    animation_group = QSequentialAnimationGroup()
    animator = QLabel(gui.computer_frame)
    animator.setObjectName(u"animator")
    animator.setGeometry(QRect(0, 0, 40, 30))
    animator.setStyleSheet(u"background-color:red;border-radius:10px;")
    animator.setText(str(data))
    for i in range(len(path) - 1):
        duration = segment_length(path[i], path[i + 1]) // gui.animation_speed
        a = QPropertyAnimation(animator, b"pos")
        a.setDuration(duration)
        a.setStartValue(path[i])
        a.setEndValue(path[i + 1])
        animation_group.addAnimation(a)
    gui.animators.append(animator)
    return animation_group
