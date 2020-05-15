# building environment: windows pycharm professional 2019.3.3
# dependency: PyQt5
# coding: utf-8
# author: 1851007 武信庭

import threading
import time
import numpy as np
from PyQt5.QtCore import QTimer

from interface import *

'状态标志定义'
OPEN = 0  # 开门状态
CLOSED = 1  # 关门状态
GOUP = 1  # 乘客要上行
GODOWN = 2  # 乘客要下行
RUNNING_UP = 1  # 电梯上行
RUNNING_DOWN = 2  # 电梯下行
STANDSTILL = 0  # 电梯静止
NOPE = 0  # 动画空
RSTART = 1  # 动画运行就绪
RSTOP = 2  # 动画停止就绪
AVAL = 1
UNAVAL = 0

INFINITE = 1000  # 无穷常量

'动画与命令处理类'
class DealCommand(object):
    def __init__(self, Elev):
        self.elev = Elev  # 与界面文件建立连接
        self.timer = QTimer()  # 定时器
        self.timer.timeout.connect(self.UdEleState)
        self.timer.start(1000)
        self.way_queue = []  # 电梯调度列表
        self.rev_way_queue = []  # 电梯不顺路调度列表

        for i in range(0, 5):
            self.way_queue.append([])
            self.rev_way_queue.append([])

    # 开关门槽函数
    def doorCtrl(self, whichelev, whichcommand):
        if whichcommand == 0:  # 开门
            if self.elev.doorState[whichelev] == CLOSED and self.elev.elevState[whichelev] == STANDSTILL:  # 若电梯静止且关闭
                self.elev.doorState[whichelev] = OPEN  # 将门状态更新为开启
                self.elev.elevEnabled[whichelev] = UNAVAL
                self.openDoor_Anim(whichelev)

        else:  # 关门
            if self.elev.doorState[whichelev] == OPEN and self.elev.elevState[whichelev] == STANDSTILL:  # 若电梯静止且开启
                self.elev.doorState[whichelev] = CLOSED  # 将门状态更新为关闭
                self.elev.elevEnabled[whichelev] = AVAL
                self.closeDoor_Anim(whichelev)

    # 开门动画
    def openDoor_Anim(self, whichelev):
        self.elev.ele_anim[2 * whichelev].setDirection(QAbstractAnimation.Forward)  # 正向动画
        self.elev.ele_anim[2 * whichelev + 1].setDirection(QAbstractAnimation.Forward)
        self.elev.ele_anim[2 * whichelev].start()  # 播放
        self.elev.ele_anim[2 * whichelev + 1].start()

    # 关门动画
    def closeDoor_Anim(self, whichelev):
        self.elev.ele_anim[2 * whichelev].setDirection(QAbstractAnimation.Backward)  # 反向动画
        self.elev.ele_anim[2 * whichelev + 1].setDirection(QAbstractAnimation.Backward)
        self.elev.ele_anim[2 * whichelev].start()  # 播放
        self.elev.ele_anim[2 * whichelev + 1].start()

    # 乘客进电梯动画
    def peopleIn_Anim(self, whichelev):
        self.elev.people[whichelev].setVisible(True)
        self.elev.people_anim[whichelev].setDirection(QAbstractAnimation.Forward)
        self.elev.people_anim[whichelev].start()

        s = threading.Timer(1.5, self.setDoorTop, (whichelev,))  # 1.5秒后把门至于顶层
        s.start()

    # 乘客出电梯动画
    def peopleOut_Anim(self, whichelev):
        self.elev.people[whichelev].setVisible(True)
        self.elev.people_anim[whichelev].setDirection(QAbstractAnimation.Backward)
        self.elev.people_anim[whichelev].start()

        s = threading.Timer(1, self.setpeopleTop, (whichelev,))  # 1s后把乘客至于顶层
        s.start()

    # 将门至于顶层
    def setDoorTop(self, whichelev):
        self.elev.ele_door[2 * whichelev].raise_()
        self.elev.ele_door[2 * whichelev + 1].raise_()

    # 将乘客至于顶层
    def setpeopleTop(self, whichelev):
        self.elev.people[whichelev].raise_()
        self.elev.people[whichelev].setVisible(False)

    # 电梯内部按键命令
    def insideDispatch(self, whichelev, dest):
        curfloor = self.elev.elevNow[whichelev]  # 当前位置
        if curfloor == dest:  # 如果目标楼层为当前楼层
            if self.elev.elevState[whichelev] == STANDSTILL:  # 若电梯静止则打开门
                self.elev.doorState[whichelev] = OPEN
                self.openDoor_Anim(whichelev)
            button = self.elev.findChild(QtWidgets.QPushButton,
                                         "button {0} {1}".format(whichelev, curfloor))  # 允许点击按钮
            button.setStyleSheet("")  # 还原按钮颜色
            button.setEnabled(True)
        elif curfloor < dest:  # 若目标层数比当前层数高
            if self.elev.elevState[whichelev] == STANDSTILL:  # 电梯处于静止状态
                self.way_queue[whichelev].append(dest)  # 将目标楼层加入调度队列
            elif self.elev.elevState[whichelev] == RUNNING_UP:  # 电梯正向上运行(顺路)
                self.way_queue[whichelev].append(dest)  # 将目标楼层加入调度队列并排序
                self.way_queue[whichelev].sort()
            elif self.elev.elevState[whichelev] == RUNNING_DOWN:  # 电梯正向下运行(不顺路)
                self.rev_way_queue[whichelev].append(dest)  # 将目标楼层加入不顺路队列并排序
                self.rev_way_queue[whichelev].sort()
        else:  # 若目标层数比当前层数低
            if self.elev.elevState[whichelev] == STANDSTILL:  # 电梯处于静止状态
                self.way_queue[whichelev].append(dest)  # 将目标楼层加入调度队列
            elif self.elev.elevState[whichelev] == RUNNING_DOWN:  # 电梯正向下运行(顺路)
                self.way_queue[whichelev].append(dest)  # 将目标楼层加入调度队列并反向排序
                self.way_queue[whichelev].sort()
                self.way_queue[whichelev].reverse()
            elif self.elev.elevState[whichelev] == RUNNING_UP:  # 电梯正向上运行(不顺路)
                self.rev_way_queue[whichelev].append(dest)  # 将目标楼层加入不顺路消息队列并反向排序
                self.rev_way_queue[whichelev].sort()
                self.rev_way_queue[whichelev].reverse()

    # 外部楼层命令处理
    def outsideDispatch(self, whichfloor, choice):
        enabled_list = []
        for i in range(0, 5):
            if self.elev.elevEnabled[i]:  # 筛选没损坏的电梯加入队列
                enabled_list.append(i)

        # 计算顺路电梯与目标楼层的距离，并找出最优选择
        dist = [INFINITE] * 5  #
        for enabled_elev in enabled_list:
            if self.elev.elevState[enabled_elev] == choice == GOUP and whichfloor > \
                    self.elev.elevNow[enabled_elev]:  # 向上顺路
                dist[enabled_elev] = abs(self.elev.elevNow[enabled_elev] - whichfloor)  # 计算楼层差

            elif self.elev.elevState[enabled_elev] == choice == GODOWN and whichfloor < \
                    self.elev.elevNow[enabled_elev]:  # 向下顺路
                dist[enabled_elev] = abs(self.elev.elevNow[enabled_elev] - whichfloor)  # 计算楼层差

            elif self.elev.elevState[enabled_elev] == STANDSTILL:  # 该电梯此时静止，则优先选择
                dist[enabled_elev] = 0.5 * abs(self.elev.elevNow[enabled_elev] - whichfloor)
            elif self.elev.elevState[enabled_elev] + choice == 3:  # 电梯请求反向不顺路
                dist[enabled_elev] = abs(self.way_queue[enabled_elev][-1] - whichfloor)
            else:  # 电梯同向不顺路,滞后选择
                dist[enabled_elev] = 4 * abs(self.way_queue[enabled_elev][-1] - whichfloor)
            print(dist[enabled_elev])

        best_elev = dist.index(min(dist))  # 选择距离最短的最佳电梯
        print(best_elev)

        if dist[best_elev] == 0:  # 如果最佳电梯就在用户选择的楼层
            self.elev.doorState[best_elev] = OPEN  # 开门并等待用户关闭
            self.openDoor_Anim(best_elev)
            self.elev.elevEnabled[best_elev] = UNAVAL
        else:
            self.way_queue[best_elev].append(whichfloor)  # 加入该最佳电梯的调度队列
            if choice == GOUP:  # 若此时为向上顺路则加入当前调度队列并排序
                self.way_queue[best_elev].sort()
            else:  # 若此时为向下顺路则加入当前调度队列并反向排序
                self.way_queue[best_elev].sort()
                self.way_queue[best_elev].reverse()
            button = self.elev.findChild(QtWidgets.QPushButton,
                                         "button {0} {1}".format(best_elev, whichfloor))  # 标识目标楼层
            button.setStyleSheet("background-color: rgb(11, 15, 255);")
            button.setEnabled(False)

    # 警报器槽函数
    def warnCtrl(self, whichelev):
        # 单独禁用
        self.elev.elevEnabled[whichelev] = UNAVAL

        self.elev.openbtn[whichelev].setEnabled(False)  # 开门键禁用
        self.elev.closebtn[whichelev].setEnabled(False)  # 关门键禁用
        self.elev.warnbtn[whichelev].setEnabled(False)  # 报警键禁用
        self.elev.layerbtn[whichelev].setEnabled(False)  # 楼层按键禁用
        self.elev.ele_background[whichelev].setEnabled(False)  # 电梯背景禁用
        self.elev.ele_door[2 * whichelev].setEnabled(False)  # 电梯门禁用
        self.elev.ele_door[2 * whichelev + 1].setEnabled(False)  # 电梯门禁用
        self.elev.label[whichelev].setEnabled(False)  # 电梯名禁用
        self.elev.layernum[whichelev].setEnabled(False)  # 数码管禁用
        self.elev.elestate[whichelev].setEnabled(False)  # 上下行标志禁用
        self.elev.ele_anim[2 * whichelev].stop()  # 停止动画
        self.elev.ele_anim[2 * whichelev + 1].stop()  # 停止动画

        # 集体禁用
        arr = np.array(self.elev.elevEnabled)
        if (arr == False).all():
            self.elev.comboBox.setEnabled(False)  # 下拉框禁用
            self.elev.chooselabel.setEnabled(False)  # 文字禁用
            self.elev.upbtn.setEnabled(False)  # 上行按钮禁用
            self.elev.downbtn.setEnabled(False)  # 下行按钮禁用
            time.sleep(0.5)
            self.MessBox = QtWidgets.QMessageBox.information(self.elev, "警告", "所有电梯已损坏!")

    # 更新电梯状态
    def UdEleState(self):
        for i in range(0, len(self.way_queue)):
            if len(self.way_queue[i]):  # 若有电梯的调度队列不为空
                if self.elev.doorState[i] == OPEN:  # 若电梯门打开
                    continue
                elif self.elev.elevState[i] == STANDSTILL:  # 若电梯处于静止状态
                    self.openDoor_Anim(i)
                    self.peopleIn_Anim(i)
                    if self.elev.elevNow[i] < self.way_queue[i][0]:  # 根据运行方向更新电梯状态
                        self.elev.elevState[i] = RUNNING_UP
                    elif self.elev.elevNow[i] > self.way_queue[i][0]:
                        self.elev.elevState[i] = RUNNING_DOWN
                    self.elev.animState[i] = RSTART  # 动画变为就绪运行状态

                elif self.elev.animState[i] == RSTART:  # 动画处于就绪运行状态
                    self.closeDoor_Anim(i)
                    self.elev.animState[i] = NOPE  # 动画变为运行状态

                elif self.elev.animState[i] == RSTOP:  # 动画处于就绪停止状态
                    self.way_queue[i].pop(0)  # 结束该命令的处理
                    self.closeDoor_Anim(i)
                    self.elev.animState[i] = NOPE
                    self.elev.elevState[i] = STANDSTILL  # 电梯变为静止状态
                    self.elev.elestate[i].setStyleSheet("QGraphicsView{border-image: url(Resources/state.png)}")

                else:  # 电梯移动
                    destFloor = self.way_queue[i][0]
                    if self.elev.elevNow[i] < destFloor:  # 向上
                        self.elev.elevState[i] = RUNNING_UP
                        self.elev.elestate[i].setStyleSheet(
                            "QGraphicsView{border-image: url(Resources/state_up.png)}")
                        self.elev.elevNow[i] = self.elev.elevNow[i] + 1  # 将当前楼层加一
                        self.elev.layernum[i].setProperty("value", self.elev.elevNow[i])

                    elif self.elev.elevNow[i] > destFloor:  # 向下
                        self.elev.elevState[i] = RUNNING_DOWN
                        self.elev.elestate[i].setStyleSheet(
                            "QGraphicsView{border-image: url(Resources/state_down.png)}")
                        self.elev.elevNow[i] = self.elev.elevNow[i] - 1  # 将当前楼层减一
                        self.elev.layernum[i].setProperty("value", self.elev.elevNow[i])

                    else:  # 电梯到达目标层
                        self.openDoor_Anim(i)
                        self.peopleOut_Anim(i)
                        self.elev.animState[i] = RSTOP  # 动画变为就绪停止状态

                        button = self.elev.findChild(QtWidgets.QPushButton,
                                                     "button {0} {1}".format(i, self.elev.elevNow[i]))  # 恢复该按钮的状态
                        button.setStyleSheet("")
                        button.setEnabled(True)

            elif len(self.rev_way_queue[i]):  # 电梯反向移动
                self.way_queue[i] = self.rev_way_queue[i].copy()  # 交换两个队列
                self.rev_way_queue[i].clear()  # 清空不顺路队列

        # 禁用电梯运行过程中的报警功能
        for i in range(0, 5):
            if self.elev.layerbtn[i].isEnabled():  # 如果这个电梯没被禁用
                if self.elev.elevState[i] == STANDSTILL:  # 如果电梯是静止的
                    self.elev.warnbtn[i].setEnabled(True)
                else:
                    self.elev.warnbtn[i].setEnabled(False)
