import numpy as np
from PyQt5.QtCore import Qt,QTimer
from pyqtgraph import ScatterPlotItem
import pyqtgraph as pg
def findNearestDot(Points,xClicked,yClciked,click,tolerance = 0.03):
    count=0
    for i in Points:
        x_diff = abs(i.x - xClicked)
        y_diff = abs(i.y - yClciked)
        if i.conjAdded:
            y_diffc=abs(i.yConj - yClciked)
            if y_diff > y_diffc:
                y_diff = y_diffc
        if x_diff <= tolerance and y_diff <= tolerance:
            return count
        count += 1
    if click:
        return 'add'
def prepareData(Dots,Mag,Phase,conj):
    Dots.magGraph = Mag
    Dots.phaseGraph = Phase
    Dots.isConjugate = conj

def emptyType(array,type):
    toBeRemoved=[obj for obj in array if obj.type==type]
    for i in toBeRemoved:
        array.remove(i)
