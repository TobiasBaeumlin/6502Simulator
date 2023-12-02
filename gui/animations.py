from PySide6.QtCore import QSequentialAnimationGroup, QPropertyAnimation, QRect, QPoint
from PySide6.QtWidgets import QLabel


def segment_length(point_a:QPoint, point_b:QPoint) -> int:
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
        duration =  segment_length(path[i], path[i + 1]) // gui.animation_speed
        a = QPropertyAnimation(animator, b"pos")
        a.setDuration(duration)
        a.setStartValue(path[i])
        a.setEndValue(path[i + 1])
        animation_group.addAnimation(a)
    gui.animators.append(animator)
    return animation_group
