# building environment: windows pycharm professional 2019.3.3
# dependency: PyQt5
# coding: utf-8
# author: 1851007 武信庭

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from dispatch import DealCommand

'状态标志定义'
OPEN = 0  # 开门状态
CLOSED = 1  # 关门状态
GOUP = 1  # 乘客上行
GODOWN = 2  # 乘客下行
RUNNING_UP = 1  # 电梯上行
RUNNING_DOWN = 2  # 电梯下行
STANDSTILL = 0  # 电梯静止
NOPE = 0  # 空动画
RSTART = 1  # 就绪进行
RSTOP = 2  # 就绪停止
ENABLE = 1
AVAL = 1
UNAVAL = 0


'UI设计与接口类'
class Ui_MainWindow(object):
    def __init__(self):
        self.Ctrl = DealCommand(self)  # 与调度文件建立连接

        self.elevEnabled = [AVAL] * 5  # 电梯状态标志位(可使用/禁用)
        self.doorState = [CLOSED] * 5  # 电梯门状态标志位(开门/关门)
        self.elevState = [STANDSTILL] * 5  # 电梯状态标志位(运行向上/运行向下/静止)
        self.animState = [NOPE] * 5  # 动画播放状态标志位(空/即将运动/即将停止)
        self.elevNow = [1] * 5  # 电梯楼层
        self.wall = []  # 背景墙
        self.ele_background = []  # 电梯背景
        self.ele_door = []  # 电梯门
        self.ele_anim = []  # 电梯开关门动画
        self.label = []  # 电梯名
        self.layernum = []  # 数码管
        self.elestate = []  # 上下行标志
        self.warnbtn = []  # 报警器
        self.layerbtn = []  # 楼层按键
        self.layer = []
        self.people = []  # 乘客
        self.people_anim = []  # 乘客动画
        self.openbtn = []
        self.closebtn = []  # 开关键

    # UI绘制
    def PrintUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 700)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 墙
        wall_pos = [10, 280, 560, 840, 1120, 1390]

        for i in range(0, len(wall_pos)):
            self.wall.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.wall[i].setGeometry(QtCore.QRect(wall_pos[i], 120, 10, 560))
            self.wall[i].setAutoFillBackground(False)
            self.wall[i].setStyleSheet("background-color: rgb(0, 0, 0);")
            self.wall[i].setObjectName("wall" + str(i))

        # 电梯
        ele_pos = [30, 300, 580, 860, 1140]

        for i in range(0, len(ele_pos)):
            # 电梯背景
            self.ele_background.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.ele_background[i].setGeometry(QtCore.QRect(ele_pos[i], 470, 131, 161))
            self.ele_background[i].setStyleSheet("background-color: rgb(113, 150, 159);")
            self.ele_background[i].setObjectName("ele_background" + str(i))

            # 电梯门
            self.ele_door.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.ele_door[i * 2].setGeometry(QtCore.QRect(ele_pos[i], 470, 64, 161))
            self.ele_door[i * 2].setStyleSheet("background-color: rgb(0,49,79);")
            self.ele_door[i * 2].setObjectName("ele_door" + str(2 * i))
            self.ele_anim.append(QPropertyAnimation(self.ele_door[2 * i], b"geometry"))
            self.ele_anim[i * 2].setDuration(1000)  # 设定动画时间
            self.ele_anim[i * 2].setStartValue(QtCore.QRect(ele_pos[i], 470, 64, 161))  # 设置起始大小
            self.ele_anim[i * 2].setEndValue(QtCore.QRect(ele_pos[i], 470, 8, 161))  # 设置终止大小

            self.ele_door.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.ele_door[i * 2 + 1].setGeometry(QtCore.QRect(ele_pos[i] + 67, 470, 64, 161))
            self.ele_door[i * 2 + 1].setStyleSheet("background-color: rgb(0,49,79);")
            self.ele_door[i * 2 + 1].setObjectName("ele_door" + str(2 * i + 1))
            self.ele_anim.append(QPropertyAnimation(self.ele_door[2 * i + 1], b"geometry"))
            self.ele_anim[i * 2 + 1].setDuration(1000)
            self.ele_anim[i * 2 + 1].setStartValue(QtCore.QRect(ele_pos[i] + 67, 470, 64, 161))
            self.ele_anim[i * 2 + 1].setEndValue(QtCore.QRect(ele_pos[i] + 123, 470, 8, 161))

        # 电梯楼层显示
        layernum_pos = [50, 320, 600, 880, 1160]
        for i in range(0, len(layernum_pos)):
            self.layernum.append(QtWidgets.QLCDNumber(self.centralwidget))
            self.layernum[i].setGeometry(QtCore.QRect(layernum_pos[i], 420, 51, 41))
            self.layernum[i].setDigitCount(2)
            self.layernum[i].setProperty("value", 1.0)  # 设置初始楼层为1层
            self.layernum[i].setObjectName("layernum" + str(i))

        # 电梯名
        elename_pos = [70, 340, 620, 900, 1180]
        for i in range(0, len(elename_pos)):
            self.label.append(QtWidgets.QLabel(self.centralwidget))
            self.label[i].setGeometry(QtCore.QRect(elename_pos[i], 640, 51, 21))
            self.label[i].setStyleSheet("font: 10pt \"Arial\";\n"
                                        "background-color: rgb(113, 150, 159);")
            self.label[i].setObjectName("label" + str(i))

        # 电梯上下行标志
        elestate_pos = [95, 365, 645, 925, 1205]
        for i in range(0, len(elestate_pos)):
            self.elestate.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.elestate[i].setGeometry(QtCore.QRect(elestate_pos[i], 410, 71, 61))
            self.elestate[i].setStyleSheet("QGraphicsView{border-image: url(Resources/state.png)}")
            self.elestate[i].setObjectName("elestate" + str(i))

        # 电梯内楼层按键
        layerbtn_pos = [180, 450, 730, 1010, 1290]
        for i in range(0, len(layerbtn_pos)):
            self.layerbtn.append(QtWidgets.QWidget(self.centralwidget))
            self.layerbtn[i].setGeometry(QtCore.QRect(layerbtn_pos[i] + 10, 120, 81, 451))
            self.layerbtn[i].setObjectName("layerbtn" + str(i))
            self.layer.append(QtWidgets.QGridLayout(self.layerbtn[i]))
            self.layer[i].setContentsMargins(0, 0, 0, 0)
            self.layer[i].setObjectName("layer" + str(i))

        names = ['19', '20', '17', '18', '15', '16', '13', '14', '11', '12', '9', '10', '7', '8', '5', '6', '3', '4',
                 '1', '2']
        positions = [(i, j) for i in range(10) for j in range(2)]  # 画按键表格
        for i in range(0, len(layerbtn_pos)):
            for position, name in zip(positions, names):
                button = QtWidgets.QPushButton(name)
                button.setObjectName("button " + str(i) + ' ' + name)
                button.setStyleSheet("")
                button.clicked.connect(MainWindow.btnClick)  # 绑定电梯内部楼层按键槽函数
                self.layer[i].addWidget(button, *position)

        # 开关键
        openbtn_pos = [180, 450, 730, 1010, 1290]
        closebtn_pos = [225, 495, 775, 1055, 1335]
        for i in range(0, len(openbtn_pos)):
            self.openbtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.openbtn[i].setGeometry(QtCore.QRect(openbtn_pos[i] + 10, 565, 35, 35))
            self.openbtn[i].setObjectName("openbtn" + str(i))
            self.closebtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.closebtn[i].setGeometry(QtCore.QRect(closebtn_pos[i] + 10, 565, 35, 35))
            self.closebtn[i].setObjectName("closebtn" + str(i))

            self.openbtn[i].clicked.connect(MainWindow.doorClick)  # 绑定门开关键槽函数
            self.closebtn[i].clicked.connect(MainWindow.doorClick)

        # 下拉框
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(630, 55, 111, 31))
        self.comboBox.setObjectName("comboBox")
        for i in range(0, 20):
            self.comboBox.addItem(str(i + 1))  # 加入楼层信息

        # 按钮提示信息
        self.chooselabel1 = QtWidgets.QLabel(self.centralwidget)
        self.chooselabel1.setGeometry(QtCore.QRect(670, 20, 161, 30))
        self.chooselabel1.setStyleSheet("font: 13pt \"微软雅黑\";\n")
        self.chooselabel1.setObjectName("chooselabel1")
        self.chooselabel2 = QtWidgets.QLabel(self.centralwidget)
        self.chooselabel2.setGeometry(QtCore.QRect(795, 20, 161, 30))
        self.chooselabel2.setStyleSheet("font: 13pt \"微软雅黑\";\n")
        self.chooselabel2.setObjectName("chooselabel2")

        # 上行按钮
        self.upbtn = QtWidgets.QPushButton(self.centralwidget)
        self.upbtn.setGeometry(QtCore.QRect(760, 40, 50, 50))
        self.upbtn.setStyleSheet("QPushButton{border-image: url(Resources/up.png)}"
                                 "QPushButton:hover{border-image: url(Resources/up_hover.png)}"
                                 "QPushButton:pressed{border-image: url(Resources/up_press.png)}")
        self.upbtn.setObjectName("upbtn")

        # 下行按钮
        self.downbtn = QtWidgets.QPushButton(self.centralwidget)
        self.downbtn.setGeometry(QtCore.QRect(810, 40, 50, 50))
        self.downbtn.setStyleSheet("QPushButton{border-image: url(Resources/down.png)}"
                                   "QPushButton:hover{border-image: url(Resources/down_hover.png)}"
                                   "QPushButton:pressed{border-image: url(Resources/down_press.png)}")
        self.downbtn.setObjectName("downbtn")

        self.upbtn.clicked.connect(MainWindow.chooseClick)  # 绑定楼层命令槽函数
        self.downbtn.clicked.connect(MainWindow.chooseClick)

        # 乘客
        people_pos = [30, 300, 580, 860, 1140]
        for i in range(0, len(people_pos)):
            self.people.append(QtWidgets.QGraphicsView(self.centralwidget))
            self.people[i].setGeometry(QtCore.QRect(people_pos[i] - 20, 590, 71, 71))
            self.people[i].setStyleSheet("QGraphicsView{border-image: url(Resources/people.png)}")
            self.people[i].setVisible(False)
            self.people[i].setObjectName("people" + str(i))
            self.people_anim.append(QPropertyAnimation(self.people[i], b"geometry"))
            self.people_anim[i].setDuration(1500)
            self.people_anim[i].setStartValue(QtCore.QRect(people_pos[i] - 20, 590, 71, 71))
            self.people_anim[i].setEndValue(QtCore.QRect(people_pos[i] + 10, 510, 111, 121))

        # 报警器
        warnbtn_pos = [190, 460, 740, 1020, 1300]
        for i in range(0, len(warnbtn_pos)):
            self.warnbtn.append(QtWidgets.QPushButton(self.centralwidget))
            self.warnbtn[i].setGeometry(QtCore.QRect(warnbtn_pos[i] + 10, 620, 50, 50))
            self.warnbtn[i].setStyleSheet("QPushButton{border-image: url(Resources/warn.png)}"
                                          "QPushButton:hover{border-image: url(Resources/warn_hover.png)}"
                                          "QPushButton:pressed{border-image: url(Resources/warn_press.png)}")
            self.warnbtn[i].setObjectName("warnbtn" + str(i))
        for i in range(0, len(self.warnbtn)):
            self.warnbtn[i].clicked.connect(MainWindow.warningClick)  # 绑定报警器槽函数


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # 报警器槽函数
    def warningClick(self):
        which_warnbtn = int(self.sender().objectName()[-1])
        self.warnbtn[which_warnbtn].setStyleSheet("background-color: rgb(255, 255, 255);")
        self.MessBox = QtWidgets.QMessageBox.information(self.warnbtn[int(which_warnbtn)], "警告", "第" +
                                                         str(which_warnbtn) + "号电梯损坏, 将被停用")  # 弹出警告框
        self.warnbtn[which_warnbtn].setStyleSheet("QGraphicsView{border-image: url(Resources/warn_press.png)}")
        self.Ctrl.warnCtrl(which_warnbtn)  # 调用warnCtrl进行处理

    # 电梯内部按键槽函数
    def btnClick(self):
        whichbtn = self.sender()
        btn_name = whichbtn.objectName()
        buf = [int(s) for s in btn_name.split() if s.isdigit()]  # 提取字符串中的数字
        whichelev = buf[0]
        whichfloor = buf[1]

        whichbtn.setStyleSheet("background-color: rgb(255, 150, 3);")  # 点击反馈
        whichbtn.setEnabled(False)  # 将按钮禁用
        self.Ctrl.insideDispatch(whichelev, whichfloor)  # 调用insideDispatch处理

    # 外部楼层命令槽函数
    def chooseClick(self):
        whichfloor = int(self.comboBox.currentText())
        whichbtn = self.sender().objectName()

        if whichbtn[0] == 'd':
            choice = GODOWN
        else:
            choice = GOUP

        self.Ctrl.outsideDispatch(whichfloor, choice)  # 调用控制器进行outsideDispatch处理

    # 开关门槽函数
    def doorClick(self):
        objectName = self.sender().objectName()
        whichelev = int(objectName[-1])
        whichcommand = 0 if objectName[0] == 'o' else 1  # 0：开门   1：关门

        self.Ctrl.doorCtrl(whichelev, whichcommand)  # 调用doorCtrl处理

    # 文字统一设置函数
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.chooselabel1.setText(_translate("MainWindow", "楼层"))
        self.chooselabel2.setText(_translate("MainWindow", "按钮"))
        for i in range(0, len(self.label)):
            self.label[i].setText(_translate("MainWindow", " 电梯" + str(i)))
            self.openbtn[i].setText(_translate("MainWindow", "开"))
            self.closebtn[i].setText(_translate("MainWindow", "关"))
