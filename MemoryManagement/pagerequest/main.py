import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QBrush
import random

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 坐标定义
        self.paras = dict()
        self.paras["分页"] = {"x": 200, "y": 50, "w": 60, "h": 40}
        self.paras["页表"] = {"x": 900, "y": 50}
        self.paras["内存"] = {"x": 1600, "y": 50}
        self.paras["LRU"] = {"x": 1400, "y": 700}
        self.paras["缺页"] = {"x": 1500, "y": 900}
        self.paras["指令条数"] = 320
        self.instructions = [i for i in range(320)]  # 指令分页

        self.notice = QLabel(self)
        self.notice.setText("缺页率:    ")
        self.notice.move(self.paras["缺页"]["x"], self.paras["缺页"]["y"])

        self.PageChart = []  # 页表
        self.PhysicMem = []  # 物理内存
        self.LostNums = 0  # 缺页次数
        self.TotalNums = 0  # 总次数

        for i in range(32):
            self.PageChart.append({"memory": -1, "unused": 0})
        for i in range(4):
            self.PhysicMem.append(-1)

        self.PageTable = QTableWidget(self)
        PageTitle = ["物理地址"]
        self.PageTable.setColumnCount(1)
        self.PageTable.setRowCount(32)
        self.PageTable.setHorizontalHeaderLabels(PageTitle)
        vlabel = []
        for i in range(self.PageTable.rowCount()):
            self.PageTable.setRowHeight(i, 36)  # 设置i行的高度
            vlabel.append(str(i))
        for k in range(self.PageTable.columnCount()):
            self.PageTable.setColumnWidth(k, 180)
        self.PageTable.setVerticalHeaderLabels(vlabel)
        self.PageTable.setGeometry(self.paras["页表"]["x"] - 40, 120, 230, 1220)

        self.PhysicsMemory = QTableWidget(self)
        PhysicsTitle = ["指令"]
        self.PhysicsMemory.setColumnCount(1)
        self.PhysicsMemory.setRowCount(4)
        self.PhysicsMemory.setHorizontalHeaderLabels(PhysicsTitle)
        self.PhysicsMemory.setVerticalHeaderLabels(["0", "10", "20", "30"])
        for i in range(self.PageTable.rowCount()):
            self.PhysicsMemory.setRowHeight(i, 100)  # 设置i行的高度
        for k in range(self.PageTable.columnCount()):
            self.PhysicsMemory.setColumnWidth(k, 200)
        self.PhysicsMemory.setGeometry(self.paras["内存"]["x"] - 40, 120, 240, 460)

        self.initUi()

    def initUi(self):
        self.setGeometry(200, 200, 2250, 1450)
        self.setWindowTitle("Memory PageRequests")
        self.textPrint()  # 绘制文字
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.show()

    def textPrint(self):
        label_1 = QLabel(self)
        label_2 = QLabel(self)
        label_3 = QLabel(self)

        label_1.setText("指令逻辑内存分页")
        label_2.setText("页表")
        label_3.setText("物理内存")

        label_1.move(self.paras["分页"]["x"], self.paras["分页"]["y"])
        label_2.move(self.paras["页表"]["x"], self.paras["页表"]["y"])
        label_3.move(self.paras["内存"]["x"], self.paras["内存"]["y"])

        self.SubmitMemory_1 = QPushButton(self)
        self.SubmitMemory_2 = QPushButton(self)
        self.SubmitMemory_3 = QPushButton(self)
        self.SubmitMemory_1.setText("单歩")
        self.SubmitMemory_2.setText("五步")
        self.SubmitMemory_3.setText("全部")
        self.SubmitMemory_1.move(self.paras["LRU"]["x"], self.paras["LRU"]["y"])
        self.SubmitMemory_2.move(self.paras["LRU"]["x"] + 200, self.paras["LRU"]["y"])
        self.SubmitMemory_3.move(self.paras["LRU"]["x"] + 400, self.paras["LRU"]["y"])
        self.SubmitMemory_1.clicked.connect(lambda: self.requestStrategy(1))
        self.SubmitMemory_2.clicked.connect(lambda: self.requestStrategy(5))
        self.SubmitMemory_3.clicked.connect(lambda: self.requestStrategy(int(len(self.instructions) / 2)))

    # 接收请求
    def requestStrategy(self, span):
        if self.TotalNums + span > 320:
            return
        for i in range(span):
            piece = random.randint(0, len(self.instructions) - 2)
            self.solveLogics(self.instructions[piece])
            self.solveLogics(self.instructions[piece + 1])
            self.instructions.pop(piece + 1)
            self.instructions.pop(piece)
    # 置换算法
    def solveLogics(self, instruction):
        # 获得页数
        self.TotalNums = self.TotalNums + 1
        page = int(instruction / 10)
        for i in range(len(self.PageChart)):
            if self.PageChart[i]["memory"] != -1 and self.PageChart[i]["memory"] != page:
                self.PageChart[i]["unused"] = self.PageChart[i]["unused"] + 1

        if self.PageChart[page]["memory"] == -1:
            self.LostNums = self.LostNums + 1
            flag = 0
            max_unused, anchor = -1, -1
            for i in range(len(self.PhysicMem)):
                if self.PhysicMem[i] == -1:
                    # 把该页存入内存块
                    self.PhysicMem[i] = page
                    self.PageChart[page] = {"memory": i*10, "unused": 0}
                    flag = 1
                    break
                else:  # 记录未使用次数最多的
                    if self.PageChart[self.PhysicMem[i]]["unused"] >= max_unused:
                        max_unused = self.PageChart[self.PhysicMem[i]]["unused"]
                        # 要被替换的内存块
                        anchor = i
            # 若内存块没有空余
            if flag == 0:
                self.PageChart[page] = {"memory": anchor, "unused": 0}
                self.PageChart[self.PhysicMem[anchor]] = {"memory": -1, "unused": 0}
                self.PhysicMem[anchor] = page
        elif self.PageChart[page] != -1:
            self.PageChart[page]["unused"] = 0
        text = "缺页率" + str(self.LostNums / self.TotalNums)
        self.notice.setText(text)
        print(self.LostNums / self.TotalNums)
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.pagesPaint(qp)

    # 更新分页显示
    def pagesPaint(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor("black")
        qp.setBrush(QColor(255, 215, 0, 0))
        for i in range(32):
            qp.drawRect(self.paras["分页"]["x"] + 40, self.paras["分页"]["y"] + 50 + i * self.paras["分页"]["h"],
                        self.paras["分页"]["w"], self.paras["分页"]["h"])
            qp.drawText(self.paras["分页"]["x"] + 3, self.paras["分页"]["y"] + 57 + (i + 1) * self.paras["分页"]["h"],
                        str((i + 1) * 10))

        col = QColor(0, 0, 0)
        col.setNamedColor("black")
        qp.setBrush(QColor(255, 215, 0, 100))

        for p in range(len(self.instructions)):
            qp.drawRect(self.paras["分页"]["x"] + 40,
                        self.paras["分页"]["y"] + 50 + self.instructions[p] * self.paras["分页"]["h"] * 32 / 320,
                        self.paras["分页"]["w"], self.paras["分页"]["h"] * 32 / 320)
        for k in range(len(self.PageChart)):
            phy_address = QTableWidgetItem(
                str(self.PageChart[k]["memory"]) + " 未用次数" + str(self.PageChart[k]["unused"]))
            self.PageTable.setItem(k, 0, phy_address)
        for t in range(len(self.PhysicMem)):
            phy_content = QTableWidgetItem(str(self.PhysicMem[t]))
            self.PhysicsMemory.setItem(t, 0, phy_content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
