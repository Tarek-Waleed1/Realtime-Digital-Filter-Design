from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QColorDialog,QMessageBox
from pyqtgraph import PlotWidget, plot,mkPen, PlotDataItem, ScatterPlotItem
from PyQt5.QtCore import Qt, QEvent,QTimer
import pyqtgraph as pg
import sys
from functools import partial
import numpy as np
import pandas as pd
import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import Utility
from Classes import plotDots,MyPlotWidget,graphInfo
import wfdb
import csv
Dots=plotDots()
input=graphInfo()
def drawUnitCircle(self,zGraph, Pole, Zero,zGraph2):
    drawCircle(zGraph)
    drawCircle(zGraph2)
    Dots.graph = zGraph
    Dots.Zero=Zero
    Dots.graph2=zGraph2

def drawCircle(graph):
    theta = np.linspace(0, 2 * np.pi, 100)
    x = np.cos(theta)
    y = np.sin(theta)
    circle_item = PlotDataItem(x=x, y=y, pen=mkPen('r'))
    graph.addItem(circle_item)
    graph.setMenuEnabled(False)
    graph.setLimits(xMin=-2, xMax=2, yMin=-2, yMax=2)
    graph.getViewBox().scaleBy((2, 2))
    graph.showGrid(True, True)
def handle_plot_click(event):
    vb = Dots.graph.plotItem.vb
    scene_coords = event.scenePos()
    if Dots.graph.sceneBoundingRect().contains(scene_coords):
        changed=0
        mouse_point = vb.mapSceneToView(scene_coords)
        if event.button() == 1:   # left click
            i = Utility.findNearestDot(Dots.dotData, mouse_point.x(), mouse_point.y(), 1,0.09)
            if Dots.graph.elapsed_timer.elapsed()<150 and i == 'add':
                # Dots.addDots(mouse_point)
                Dots.createDot(mouse_point.x(),mouse_point.y(),Dots.Zero.isChecked())
                changed=1
                Dots.lastClicked = len(Dots.dotData)-1
        elif event.button() == 2:   # right click
            deleteDot(mouse_point)
            changed=1
        if changed:
            drawMagPhase()
def onMouseMoved(event):
    if Dots.graph.left_button_pressed:
        point = Dots.graph.plotItem.vb.mapSceneToView(event.pos())
        if point is not None:
            i = Utility.findNearestDot(Dots.dotData, point.x(), point.y(), 0, 0.09)
            if i is not None:
                Dots.dotData[i].x = point.x()
                Dots.dotData[i].y = point.y()
                Dots.dotData[i].xConj=point.x()
                Dots.dotData[i].yConj=(point.y()*-1)
                if Dots.dotData[i].conjAdded:
                    Dots.dotData[i].plotreferenceConj.clear()
                    Dots.dotData[i].plotreferenceConj.addPoints(x=[Dots.dotData[i].xConj], y=[Dots.dotData[i].yConj])
                Dots.dotData[i].plotreference.clear()
                Dots.dotData[i].plotreference.addPoints(x=[Dots.dotData[i].x], y=[Dots.dotData[i].y])
                drawMagPhase()
                Dots.lastClicked=i


def deleteDot(position):
    i=Utility.findNearestDot(Dots.dotData,position.x(),position.y(),0,0.03)
    if i is not None:
        Dots.dotData[i].plotreference.clear()
        if Dots.dotData[i].conjAdded:
            Dots.dotData[i].plotreferenceConj.clear()
        Dots.dotData.pop(i)
        Dots.updatePlot()

def deleteDots(self,all=2):
    type=None
    match all:
        case 0:
            type='Pole'
        case 1:
            type='Zero'
        case 2:
            type='all'
    if type=='all':
        for i in range(len(Dots.dotData)):
            Dots.dotData[i].plotreference.clear()
            if Dots.dotData[i].conjAdded == 1:
                Dots.dotData[i].plotreferenceConj.clear()
        Dots.dotData=[]
    else:
        for i in range(len(Dots.dotData)):
            if Dots.dotData[i].type==type:
                Dots.dotData[i].plotreference.clear()
                if Dots.dotData[i].conjAdded == 1:
                    Dots.dotData[i].plotreferenceConj.clear()
        Utility.emptyType(Dots.dotData, type)
    Dots.updatePlot()
    drawMagPhase()

def setupGraph(self,zGraph,mag,phase,conjugate):
    Utility.prepareData(Dots, mag, phase, conjugate)
    my_plot_widget = MyPlotWidget()
    my_plot_widget.setGeometry(zGraph.geometry())
    my_plot_widget.show()
    layout = self.findChild(QGridLayout, 'gridLayout_5')  # Replace 'horizontalLayout' with your layout name
    layout.replaceWidget(zGraph, my_plot_widget)
    zGraph.setParent(None)
    return my_plot_widget

def cleargraph():
    Dots.magGraph.clear()
    Dots.phaseGraph.clear()
def drawMagPhase():
    f, mag, phase = Dots.frequency_response()
    cleargraph()
    Dots.magGraph.plot(f, 20 * np.log10(mag))
    Dots.phaseGraph.plot(f, np.rad2deg(phase))


def setranges(inputGraph,filteredGraph,time,maxAmp,minAmp=0):
    if input.openedSignal:
        time=max(time)
        maxAmp=max(maxAmp)
        minAmp=min(input.amp)
    inputGraph.setLimits(xMin=0, xMax=time, yMin=minAmp, yMax=maxAmp)
    filteredGraph.setLimits(xMin=0, xMax=time, yMin=minAmp, yMax=maxAmp)
def browseFiles(self,inputGraph,filteredGraph,temporalSlider,temporalValue):
    input.openedSignal=True
    self.filename, _ = QFileDialog.getOpenFileName(None, 'Open the signal file', './',
                                                   filter="Raw Data(*.csv *.txt *.xls *.hea *.dat *.rec *.wav)")
    path = self.filename
    filetype = path[len(path) - 3:]
    clearPlot(inputGraph,filteredGraph)
    if filetype == "dat":
        self.record = wfdb.rdrecord(path[:-4], channels=[1])
        temp_arr_y = self.record.p_signal
        temp_arr_y = np.concatenate(temp_arr_y)
        temp_arr_y = temp_arr_y[:3000]
        temp_arr_x=np.linspace(0,3,3000,endpoint=False)
        self.fsampling = self.record.fs
        samplerate=self.record.fs
        maxFreq=self.fsampling/2
        input.amp = temp_arr_y
        input.time = temp_arr_x
    if filetype == "csv":
        try:
            dataframe = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return
        except pd.errors.ParserError:
            dataframe = pd.read_csv(path, header=None)

        input.amp = dataframe.iloc[:, 1]
        input.time = dataframe.iloc[:, 0]
        samplerate=dataframe.iloc[0,2]

    drawGraphSetup(inputGraph, filteredGraph, input.time, input.amp)

    setranges(inputGraph, filteredGraph,input.time,input.amp)
    setQtimer(self,inputGraph, filteredGraph)
def drawGraphSetup(inputGraph,filteredGraph,time ,amp):
    input.graphIn = inputGraph.plot(time, amp)
    input.graphFiltered = filteredGraph.plot(time, amp)
def updateSlider(temporalSlider,temporalValue):
    tValue = temporalSlider.value()
    temporalValue.setText(str(tValue))
    Dots.temporalResolution = tValue

def updateInputFilteredGraph(inputGraph, filteredGraph):
    input.addValue()
    input.graphIn.setData(input.x_values, input.y_values)
    filter=Dots.applyfilter(input.y_values)
    # print(len(filter),print(len(filtered.x_values)))
    inputGraph.setXRange(input.x_values[len(input.x_values) - 1] - 500, input.x_values[len(input.x_values) - 1])
    filteredGraph.setXRange(input.x_values[len(input.x_values) - 1] - 500, input.x_values[len(input.x_values) - 1])
    if Dots.temporalCount >= Dots.temporalResolution:
        Dots.temporalCount = 1
        input.graphFiltered.setData(input.x_values, filter)
    else:
        Dots.temporalCount +=1

def setQtimer(self,inputGraph, filteredGraph, interval=100):
    input.timer = QtCore.QTimer(self)
    input.timer.setInterval(interval)
    input.timer.timeout.connect(partial(updateInputFilteredGraph,inputGraph, filteredGraph))
    input.timer.start()

def addConjugate():
    if Dots.lastClicked is not None:
        i=Dots.lastClicked
        match Dots.dotData[i].conjAdded:
            case 0:
                Dots.dotData[i].plotreferenceConj.addPoints(x=[Dots.dotData[i].xConj], y=[Dots.dotData[i].yConj])
                Dots.dotData[i].conjAdded = 1
            case 1:
                Dots.dotData[i].conjAdded = 0
                Dots.dotData[i].plotreferenceConj.clear()
        Dots.updatePlot()
        drawMagPhase()

def paintEvent(event,label):
    super(QLabel, label).paintEvent(event)
    painter = QPainter(label)
    painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
    # Calculate the center position
    center_y = label.height() // 2
    # Draw a horizontal line in the center
    painter.drawLine(0, center_y, label.width(), center_y)

def clearPlot(inputGraph,filteredGraph):
    inputGraph.clear()
    filteredGraph.clear()
    input.amp = []
    input.time = []
    input.x_values = []
    input.y_values = []
    input.timer=0

def mouseSignal(event,label,inputGraph,filteredGraph,self):
    if event.buttons() == Qt.LeftButton:
        if input.openedSignal:
            input.openedSignal = 0
            clearPlot(inputGraph,filteredGraph)
            input.time = np.arange(0, 10000, 1)
            inputGraph.setLimits(xMin=0, xMax=10000, yMin=-160, yMax=160)
            filteredGraph.setLimits(xMin=0, xMax=10000, yMin=-700, yMax=700)
            input.graphIn = inputGraph.plot(input.time, input.time)
            input.graphFiltered = filteredGraph.plot(input.time, input.time)
            setQtimer(self,inputGraph, filteredGraph,1)
        delta_y = label.height() // 2 - event.pos().y()
        input.amp.append(delta_y)

def handleAllPass(self,isAdd,allPassFiltersArray,filterIndex,filterPhase,AllPhase,Library,LibraryAdded):
    if not Library == 0:
        filterToBeUsed=allPassFiltersArray[int(filterIndex)]
        Dots.allPassArray.append(str(allPassFiltersArray[filterIndex]))
        allPassFilter=complex(filterToBeUsed)
    else:
        allPassFilter=complex(LibraryAdded.currentText())
    Dots.allPassFilter(allPassFilter,filterIndex,filterPhase,AllPhase,isAdd,Library,LibraryAdded)
    if LibraryAdded.count() == 0:
        drawMagPhase()
        filterPhase.clear()
        AllPhase.clear()





def addToLibrary(allPassFiltersArray,Library,filterPhase,AllPhase,valueOfAllPass):
    value=complex(valueOfAllPass)
    allPassFiltersArray.append(value)
    Library.addItem(valueOfAllPass)















