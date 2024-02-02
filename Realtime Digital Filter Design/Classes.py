import scipy.signal
from PyQt5.QtCore import Qt,QElapsedTimer
from pyqtgraph import PlotWidget,ScatterPlotItem
from PyQt5.QtWidgets import QApplication, QWidget
import pyqtgraph as pg
from scipy.signal import zpk2tf, TransferFunction, freqz,lfilter,tf2zpk
import numpy as np
class points():
    def __init__(self):
        self.x=None
        self.y=None
        self.plotreference=0
        self.plotreferenceFilter=0
        self.xConj = 0
        self.yConj = 0
        self.plotreferenceConj = 0
        self.type='boom'
        self.conjAdded=0
        self.libIndex=None
class graphInfo():
    def __init__(self):
        self.graphIn=None
        self.graphFiltered=None
        self.freqSampling=0
        self.amp=[]
        self.time=[]
        self.x_values=[]
        self.y_values=[]
        self.cineSpeed=1
        self.timer=0
        self.openedSignal=1
        self.mouseIndex=0
    def addValue(self):
        if len(self.y_values) == 0:
            self.y_values.append(self.amp[0])
        else:
            if len(self.amp) > len(self.y_values):
                self.y_values.append(self.amp[len(self.y_values)])
            else:
                return

        if len(self.x_values) == 0:
            self.x_values.append(self.time[0])
        else:
            if len(self.time) > len(self.x_values):
                self.x_values.append(self.time[len(self.x_values)])
class plotDots():
    def __init__(self):
        self.dotData = []
        self.graph = 0
        self.graph2 = 0
        self.magGraph = 0
        self.phaseGraph = 0
        self.left_button_pressed = False
        self.Zero = 0
        self.isConjugate = 0
        self.poles = []
        self.zeros = []
        self.num = []
        self.den = []
        self.lastClicked = None
        self.currentFilter = 0
        self.temporalResolution=1
        self.temporalCount=1
        self.zPlotReference = ScatterPlotItem()
        self.pPlotReference = ScatterPlotItem(size=10, pen=pg.mkPen(None), symbol='x',
                                              brush=pg.mkBrush(255, 0, 0, 120))
        self.allPassArray=[]
    def addDots(self,mousePosition):
        # Add a point to the scatter plot at the clicked position
        self.createDot(self,mousePosition.x(),mousePosition.y(),self.Zero.isChecked())

    def frequency_response(self, sample_rate=1000):
        self.poles, self.zeros=self.setupZerosPoles()
        self.num, self.den = zpk2tf(self.zeros, self.poles, 1.0)
        custom_filter = TransferFunction(self.num, self.den, dt=1.0 / sample_rate)
        f, h = freqz(custom_filter.num, custom_filter.den, worN=8000, fs=sample_rate)
        magnitude_response = np.abs(h)
        phase_response = np.angle(h)
        freq_hz = f*2 / (np.pi)

        return freq_hz, magnitude_response, phase_response
    def setupZerosPoles(self):
        poles=[]
        zeros=[]
        count=0
        for i in range(len(self.dotData)):
            if self.dotData[i].libIndex is not None:
                count += 1
        if count == range(len(self.dotData)):
            return [0,0]
        for i in range(len(self.dotData)):
            if self.dotData[i].type=='Pole':
                poles.append(complex(self.dotData[i].x, self.dotData[i].y))
                if self.dotData[i].conjAdded:
                    poles.append(complex(self.dotData[i].xConj, self.dotData[i].yConj))
            else:
                zeros.append(complex(self.dotData[i].x, self.dotData[i].y))
                if self.dotData[i].conjAdded:
                    zeros.append(complex(self.dotData[i].xConj, self.dotData[i].yConj))
        return [poles,zeros]
    def applyfilter(self,signal,graph=0):
        if any(self.num) or any(self.den):
            z=lfilter(self.num,self.den,signal)
            real_parts = np.real(z)
            self.currentFilter=z

        else:
            real_parts = signal
        if graph:
            graph.clear()
            graph.setLimits(xMin=0, xMax=10000, yMin=min(real_parts), yMax=max(real_parts))
        return real_parts
    def updatePlot(self):
        self.graph.setXRange(-2, 2)
        self.graph.setYRange(-2, 2)
        self.graph2.setXRange(-2, 2)
        self.graph2.setYRange(-2, 2)

    def clearPlot(self,filterPhase,AllPhase):
        self.magGraph.clear()
        self.phaseGraph.clear()
        filterPhase.clear()
        AllPhase.clear()
        self.zPlotReference.clear()
        self.pPlotReference.clear()


    def allPassFilter(self,allPassFilter,filterIndex,filterPhase,AllPhase,isAdd,Library,LibraryAdded):
        self.clearPlot(filterPhase,AllPhase)
        if isAdd:
            b=[-allPassFilter,1]
            a=[1,-allPassFilter]
            z,p,k=tf2zpk(b,a)
            zXCoordinate = np.real(z)
            zYCoordinate = np.imag(z)
            pXCoordinate = np.real(p)
            pYCoordinate = np.imag(p)
            zXCoordinate=zXCoordinate.flatten()[0]
            zYCoordinate=zYCoordinate.flatten()[0]
            pXCoordinate=pXCoordinate.flatten()[0]
            pYCoordinate=pYCoordinate.flatten()[0]
            self.zPlotReference.addPoints(x=[zXCoordinate], y=[zYCoordinate])
            self.pPlotReference.addPoints(x=[pXCoordinate], y=[pYCoordinate])
            self.graph2.addItem(self.zPlotReference)
            self.graph2.addItem(self.pPlotReference)
            if not Library == 0:
                LibraryAdded.addItem(self.allPassArray[-1])
                self.createDot(zXCoordinate,zYCoordinate,1,filterIndex)
                self.createDot(pXCoordinate, pYCoordinate, 0, filterIndex)


        else:
            allPassChosen=LibraryAdded.currentText()
            filterIndex=Library.findText(allPassChosen)
            LibraryAdded.removeItem(LibraryAdded.currentIndex())
            LibraryAdded.update()
            toBeRemoved = [obj for obj in self.dotData if obj.libIndex == filterIndex]
            for i in toBeRemoved:
                i.plotreference.clear()
                self.dotData.remove(i)
            self.updatePlot()
            if not LibraryAdded.count()==0:
                allPassFilter = complex(LibraryAdded.currentText())
            b = [-allPassFilter, 1]
            a = [1, -allPassFilter]
        if not LibraryAdded.count() == 1 or not Library == 0:
            f, mag, phase = self.frequency_response()
            self.magGraph.plot(f, 20 * np.log10(mag))
            f,h=freqz(b,a)
            bFilter=np.convolve(self.num,b)
            aFilter=np.convolve(self.den,a)
            fFilter, hFilter = freqz(bFilter, aFilter)
            filterPhase.plot(f, np.rad2deg(np.angle(h)))
            self.phaseGraph.plot(f, np.rad2deg(np.angle(hFilter)))
            AllPhase.plot(f, np.rad2deg(np.angle(hFilter)))
    def createDot(self,x,y,type,libIndex=None):
        data=points()
        if type:
            data.type='Zero'
            data.plotreference=ScatterPlotItem()
            data.plotreferenceConj=ScatterPlotItem()
        else:
            data.type='Pole'
            data.plotreference=ScatterPlotItem(size=10, pen=pg.mkPen(None), symbol='x', brush=pg.mkBrush(255, 0, 0, 120))
            data.plotreferenceConj=ScatterPlotItem(size=10, pen=pg.mkPen(None), symbol='x', brush=pg.mkBrush(255, 0, 0, 120))
        self.graph.addItem(data.plotreference)
        self.graph.addItem(data.plotreferenceConj)
        data.x = x
        data.y = y
        data.plotreference.addPoints(x=[data.x], y=[data.y])
        data.xConj = x
        data.yConj = y * -1
        data.libIndex=libIndex
        if self.isConjugate.isChecked() and libIndex is None:
            data.plotreferenceConj.addPoints(x=[data.xConj], y=[data.yConj])
            data.conjAdded=1
        self.dotData.append(data)


class MyPlotWidget(PlotWidget):
    sigMouseReleased = pg.QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_button_pressed = False
        self.elapsed_timer = QElapsedTimer()
        self.moving=False
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.sigMouseReleased.emit(event)
            self.left_button_pressed = True
            self.elapsed_timer.start()

    def mouseMoveEvent(self, event):
        if self.left_button_pressed:
            self.moving = True
            # Handle mouse movement while the left button is held down
            self.sigSceneMouseMoved.emit(event)  # Emit your custom signal if needed

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.sigMouseReleased.emit(event)
            self.left_button_pressed = False
            self.moving = False
