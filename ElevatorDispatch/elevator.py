# building environment: windows pycharm professional 2019.3.3
# dependency: PyQt5
# coding: utf-8
# author: 1851007 武信庭

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

from interface import *


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.PrintUi(self)
        self.setWindowTitle('Elevator')  # 窗口UI设置
        self.setWindowIcon(QIcon('Resources/icon.png'))


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 分辨率自适应
    app = QApplication(sys.argv)  # 界面对象基类
    window = MainWindow()  # 建立窗口
    window.setStyleSheet("#MainWindow{background-color: rgb(255,241,200);}")
    window.show()

    sys.exit(app.exec())
