# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 18:52:52 2019

@author: John Doe
"""

import sys
import numpy as np
from guiutils import load_data
from ecg_offline import peaks_signal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QFileDialog, QAction, QMainWindow,
                             QVBoxLayout, QSizePolicy)
from PyQt5.QtGui import QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as
                                                NavigationToolbar)


class Window(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle('biopeaks')
        self.setGeometry(50, 50, 1500, 500)
        self.setWindowIcon(QIcon('python_icon.png'))
        
        # initialize data
        self.data = None
        self.peaks = None
        
        # set up toolbar
        toolbar = self.addToolBar('Toolbar')

        loadData = QAction(QIcon('open_icon.png'), 'Load data', self)
        loadData.triggered.connect(self.load_data)
        toolbar.addAction(loadData)      

        findPeaks = QAction(QIcon('plot_icon.png'), 'Find peaks', self)
        findPeaks.triggered.connect(self.find_peaks)
        toolbar.addAction(findPeaks)      

        savePeaks = QAction(QIcon('save_icon.png'), 'Save peaks', self)
        savePeaks.triggered.connect(self.save_peaks)
        toolbar.addAction(savePeaks)      

        # set up the central widget containing the plot and navigationtoolbar
        self.centwidget = QWidget()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.navitools = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout(self.centwidget)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.navitools)
        self.setCentralWidget(self.centwidget)
        
        self.show()

    # toolbar methods
    def load_data(self):
        fname = QFileDialog.getOpenFileNames(self, 'Open file', '\home')
        
        # initiate plot to show user that their data loaded successfully
        if fname[0]:
            self.data = load_data(fname[0][0][:-4])
            self.ax.clear()
            self.ax.plot(self.data)
            self.canvas.draw()
        
    def find_peaks(self):
        # identify and show peaks
        if self.data is not None:
            self.peaks = peaks_signal(self.data, 360)
            self.ax.scatter(self.peaks, self.data[self.peaks], c='m')
            self.canvas.draw()
            
    def save_peaks(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save peaks', 'untitled.csv',
                                                  'All Files (*);;CSV (*.csv)')
        if filename and (self.peaks is not None):
            np.savetxt(filename, self.peaks)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())
    