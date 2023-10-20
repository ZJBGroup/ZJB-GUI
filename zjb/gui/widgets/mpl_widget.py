from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot

class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        self.vertical_layout = QVBoxLayout()
        # self.vertical_layout.addWidget(self.canvas)

        # self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(self.vertical_layout)
