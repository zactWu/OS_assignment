import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QIntValidator, QIcon
from PyQt5.QtCore import Qt
import operator


class MainWindow(QWidget):
    # 默认属性和参数
    (mem_width, mem_height) = (112.5, 960)
    free_color = QColor(240, 255, 255, 100)
    busy_color = QColor(255, 215, 0, 100)
    (start_x, start_y) = (0, 0)
    ratio = 1.5

    (MaxIndex, BlockIndex) = (640, 1)
    # 输入控件
    RequiredMemory = None
    RequiredIndex = None
    SubmitMemory = None
    SubmitIndex = None

    # 已分配内存块列表
    DeployList = None
    # 未分配的空闲块表
    FreeList = None

    def __init__(self):
        super().__init__()
        self.DeployList = []
        self.FreeList = []
        # 初始化空闲表
        InitialFreeBlock = MemoryBlock()
        InitialFreeBlock.setProperty(addr=0, size=640, index=0, isDeploy=False)
        self.FreeList.append(InitialFreeBlock)
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1200, 1080)
        self.setWindowTitle('MemoryManagement')
        self.start_x = (self.width() - self.mem_width) / 2 + 200  # 锚点
        self.start_y = self.height() * 0.05
        # 文字绘制
        label1 = QLabel(self)
        label1.setText("内存使用情况")
        label1.move(self.start_x + 20, self.start_y - 40)
        label2 = QLabel(self)
        label2.setText("0")
        label2.move(self.start_x - 36, self.start_y - 5)
        label3 = QLabel(self)
        label3.setText("640")
        label3.move(self.start_x - 60, self.start_y + self.mem_height - 5)

        self.InputPrint()
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.show()

    def InputPrint(self):
        label4 = QLabel(self)
        label5 = QLabel(self)
        label6 = QLabel(self)

        label4.setText("分配内存块：")
        label4.move(100, 100)
        label5.setText("回收内存块：")
        label5.move(100, 200)
        label6.setText("选择分配策略:")
        label6.move(100, 300)

        self.RequiredMemory = QLineEdit(self)
        self.RequiredMemory.move(250, 95)
        self.RequiredMemory.setPlaceholderText("输入内存(0-640整数)")
        self.RequiredMemory.setValidator(QIntValidator())
        self.SubmitMemory = QPushButton(self)
        self.SubmitMemory.setText("分配")
        self.SubmitMemory.move(500, 90)
        self.SubmitMemory.clicked.connect(self.allocateStrategy)

        self.RequiredIndex = QLineEdit(self)
        self.RequiredIndex.move(250, 195)
        self.RequiredIndex.setPlaceholderText("输入内存块编号")
        self.RequiredIndex.setValidator(QIntValidator())
        self.SubmitIndex = QPushButton(self)
        self.SubmitIndex.setText("回收")
        self.SubmitIndex.move(500, 190)
        self.SubmitIndex.clicked.connect(self.recycleStrategy)

        self.ratiobutton1 = QRadioButton('最先适配', self)
        self.ratiobutton1.move(270, 295)
        self.ratiobutton2 = QRadioButton('最优适配', self)
        self.ratiobutton2.move(420, 295)

    def allocateStrategy(self):
        scale = int(self.RequiredMemory.text())
        self.RequiredMemory.clear()
        if self.ratiobutton1.isChecked():  # 最先适配算法
            block = MemoryBlock()
            for space in self.FreeList:
                if space.size >= scale:
                    block.setProperty(addr=space.address, size=scale, index=1, isDeploy=True)
                    self.DeployList.append(block)
                    space.address = space.address + block.size
                    space.size = space.size - block.size
                    break
        elif self.ratiobutton2.isChecked():  # 最优适配算法
            block = MemoryBlock()
            anchor, gap = -1, 640
            for i in range(len(self.FreeList)):
                if self.FreeList[i].size - scale >= 0 and self.FreeList[i].size - scale < gap:
                    anchor = i
                    gap = self.FreeList[i].size - scale
            if anchor != -1:
                block.setProperty(addr=self.FreeList[anchor].address, size=scale, index=1, isDeploy=True)
                self.DeployList.append(block)
                self.FreeList[anchor].size = self.FreeList[anchor].size - scale
                self.FreeList[anchor].address = self.FreeList[anchor].address + scale
        else:
            QMessageBox.information(self, "提示", "请先选择分配策略", QMessageBox.Yes | QMessageBox.No)
        self.update()

    def recycleStrategy(self):
        recycler = int(self.RequiredIndex.text())
        self.RequiredIndex.clear()
        for i in range(len(self.DeployList)):
            if recycler == self.DeployList[i].index:
                self.FreeList.append(self.DeployList[i])
                while recycler in MemoryBlock.IndexPool:
                    MemoryBlock.IndexPool.remove(recycler)
                self.DeployList.pop(i)
                self.update()
                break
        cmpfun = operator.attrgetter('address')
        self.FreeList.sort(key=cmpfun)

        for j in range(len(self.FreeList) - 1, 0, -1):
            if self.FreeList[j].address == self.FreeList[j - 1].address + self.FreeList[j - 1].size:
                self.FreeList[j - 1].size = self.FreeList[j - 1].size + self.FreeList[j].size
                self.FreeList.pop(j)

    def tablePrint(self, qp, color):
        col = QColor(0, 0, 0)
        col.setNamedColor("black")
        qp.setPen(col)
        qp.setBrush(color)
        qp.drawRect(self.start_x, self.start_y, self.mem_width, self.mem_height)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.tablePrint(qp, self.free_color)
        for task in self.DeployList:
            self.allocateMemory(qp, task)  # 显示已分配内存
        qp.end()

    def allocateMemory(self, qp, task):
        if type(task) != MemoryBlock:
            return False

        col = QColor(0, 0, 0)
        col.setNamedColor("black")
        qp.setPen(col)
        qp.setBrush(self.busy_color)
        qp.drawRect(self.start_x, self.start_y + task.address * self.ratio, self.mem_width, task.size * self.ratio)
        qp.drawText(self.start_x + 0.5 * self.mem_width, self.start_y + task.address * self.ratio + task.size,
                    str(task.index))
        if task.address == 0:
            qp.drawText(self.start_x - 40, self.start_y + (task.address + task.size) * self.ratio + 7,
                        str(task.address + task.size))
        elif task.address + task.size != 640:
            qp.drawText(self.start_x - 40, self.start_y + task.address * self.ratio + 7, str(task.address))
            qp.drawText(self.start_x - 40, self.start_y + (task.address + task.size) * self.ratio + 7,
                        str(task.address + task.size))


class MemoryBlock:
    MaxIndex = 640
    IndexPool = []

    def _init_(self):
        self.address, self.size = 0, 0
        index = 0
        isDeploy = False

    # 设置要分配的内存块的参数
    def setProperty(self, addr, size, index, isDeploy):
        self.address = addr
        self.size = size
        self.isDeploy = isDeploy
        # 不是空块
        if index != 0:
            for i in range(1, MemoryBlock.MaxIndex + 1):
                if i not in MemoryBlock.IndexPool:
                    self.index = i
                    MemoryBlock.IndexPool.append(i)
                    break


if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 分辨率自适应
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
