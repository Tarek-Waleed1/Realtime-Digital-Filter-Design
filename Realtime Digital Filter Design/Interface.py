from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget
import pyqtgraph
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
import functions
import Utility
import numpy as np
from allpassFilters import allPassFiltersArray
def initConnectors(self):
    graphSetup = self.findChild(PlotWidget, "UnitCircle")
    zGraph2 = self.findChild(PlotWidget, "UnitCircle_2")
    Mag = self.findChild(PlotWidget, "Magnitude")
    filterPhase = self.findChild(PlotWidget, "Phase_2")
    AllPhase = self.findChild(PlotWidget, "fixedPhase")
    temporalSlider = self.findChild(QtWidgets.QSlider, "temporalresslider")
    temporalvalue = self.findChild(QtWidgets.QLabel, "temporalresvalue")
    padArea = self.findChild(QtWidgets.QLabel, "padarea")
    temporalSlider.setMinimum(1)  # Set minimum value to 1
    temporalSlider.setMaximum(100)
    inSig = self.findChild(PlotWidget, "inputsignal")
    outSig = self.findChild(PlotWidget, "Filterd")
    inSig.getViewBox().enableAutoRange()
    inSig.getViewBox().setLimits(xMin=0)
    outSig.getViewBox().enableAutoRange()
    outSig.getViewBox().setLimits(xMin=0)
    Phase=self.findChild(PlotWidget, "Phase")
    pole = self.findChild(QtWidgets.QRadioButton, "poleradio")
    zero = self.findChild(QtWidgets.QRadioButton, "zeroradio")
    conjugate = self.findChild(QtWidgets.QCheckBox, "conjugate")
    zGraph=functions.setupGraph(self,graphSetup, Mag,Phase,conjugate)
    functions.drawUnitCircle(self,zGraph, pole.isChecked(), zero, zGraph2)
    zGraph.setAspectLocked(True)
    zGraph.setXRange(-2, 2)
    zGraph.setYRange(-2, 2)
    zGraph2.setAspectLocked(True)
    zGraph2.setXRange(-2, 2)
    zGraph2.setYRange(-2, 2)
    deleteZero = self.findChild(QtWidgets.QPushButton, "clearzero")
    deletePole = self.findChild(QtWidgets.QPushButton, "clearpole")
    deleteAll = self.findChild(QtWidgets.QPushButton, "clearall")
    openFiles = self.findChild(QtWidgets.QAction, "actionOpen")
    Library = self.findChild(QtWidgets.QComboBox, "Library")
    LibraryAdded = self.findChild(QtWidgets.QComboBox, "Library_2")
    addallpass = self.findChild(QtWidgets.QPushButton, "addallpass")
    removeallpass = self.findChild(QtWidgets.QPushButton, "removeallpass")
    valueOfAllPass = self.findChild(QtWidgets.QLineEdit, "valueofalpha")
    addtolibrary = self.findChild(QtWidgets.QPushButton,"addtolibrary")
    zGraph.scene().sigMouseClicked.connect(functions.handle_plot_click)
    self.setMouseTracking(True)
    temporalSlider.valueChanged.connect(lambda: functions.updateSlider(temporalSlider,temporalvalue))
    zGraph.sigSceneMouseMoved.connect(functions.onMouseMoved)
    deleteAll.clicked.connect(lambda: functions.deleteDots(self))
    deletePole.clicked.connect(lambda: functions.deleteDots(self,0))
    deleteZero.clicked.connect(lambda: functions.deleteDots(self,1))
    openFiles.triggered.connect(lambda: functions.browseFiles(self,inSig,outSig,temporalSlider, temporalvalue))
    conjugate.stateChanged.connect(lambda:functions.addConjugate())
    padArea.start_pos = padArea.mapToGlobal(padArea.pos())
    padArea.mousePressEvent = lambda event: functions.mouseSignal(event, padArea,inSig,outSig,self)
    padArea.mouseMoveEvent = lambda event: functions.mouseSignal(event, padArea,inSig,outSig,self)
    padArea.paintEvent=lambda event:functions.paintEvent(event,padArea)
    for i in range(len(allPassFiltersArray)):
        Library.addItem(str(allPassFiltersArray[i]))
    addallpass.clicked.connect(lambda: functions.handleAllPass(self,1,allPassFiltersArray,Library.currentIndex(),filterPhase,AllPhase,Library,LibraryAdded))
    removeallpass.clicked.connect(lambda: functions.handleAllPass(self, 0,allPassFiltersArray,Library.currentIndex(),filterPhase,AllPhase,Library,LibraryAdded))
    addtolibrary.clicked.connect(lambda:functions.addToLibrary(allPassFiltersArray,Library,filterPhase,AllPhase,valueOfAllPass.text()))
    LibraryAdded.currentIndexChanged.connect(lambda:functions.handleAllPass(self, 1,allPassFiltersArray,LibraryAdded.currentIndex(),filterPhase,AllPhase,0,LibraryAdded))



