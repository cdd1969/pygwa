from pyqtgraph.Qt import QtCore, QtGui
import math
#from lib.functions.devlin2003 import angle2bearing


class myArrow(QtGui.QGraphicsLineItem):
    '''
        Class describes an Arrow graphics item in PyQt
        Taken from : http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/graphicsview/diagramscene/diagramscene.py
    '''
    def __init__(self, startPoint, endPoint, angle=None, length=50., **kwargs):

        self.myArrowHeadSize = kwargs.pop('arrowHeadSize', 10)
        self.myLineWidth = kwargs.pop('lineWidth', 2)
        self.myColor = kwargs.pop('color', QtCore.Qt.black)


        super(myArrow, self).__init__(**kwargs)
        self.arrowHead = QtGui.QPolygonF()

        if angle is None:
            '''
                create arrow based on two point
            '''
            self.p1 = startPoint
            self.p2   = endPoint
        else:
            if isinstance(angle, (int, float, long)) and angle >= -360. and angle <= 360.:
                '''
                    Create an arrow based on the starting point, angle (degrees) and length
                '''
                self.p1 = startPoint

                #angle = angle - 90  #conversion to set the theta=0 to the y-axes direction, the theta > 0 direction is already clock-wise
                angle = math.radians(angle)
                self.p2 = QtCore.QPointF(startPoint.x() + math.cos(angle) * length,
                                        startPoint.y() + math.sin(angle) * length)
            else:
                raise ValueError('{0} Invalid value for the keyword argument `angle`. Must be float in range [-360:+360]'.format(angle))

        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        
        self.setPen(QtGui.QPen(self.myColor, self.myLineWidth, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        return QtCore.QRectF(self.p1, QtCore.QSizeF(self.p2.x() - self.p1.x(), self.p2.y() - self.p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def updatePosition(self):
        line = QtCore.QLineF(self.p1, self.p2)
        self.setLine(line)

    def shape(self):
        path = super(myArrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def paint(self, painter, option, widget=None):
        if (self.p1 == self.p2):
            return

        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = self.myArrowHeadSize
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        line = QtCore.QLineF(self.p1, self.p2)


        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p2(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)



if __name__ == '__main__':
    import sys, random

    def angle2bearing(angle, origin='N'):
        ''' Convert angle to bearing
            see http://www.mathwords.com/b/bearing.htm
            http://webhelp.esri.com/arcgisdesktop/9.1/index.cfm?id=1650&pid=1638&topicname=Setting%20direction%20measuring%20systems%20and%20units
        Args:
        -----
            angle (float) [degrees]:
                angle with respect to x-axis (east), counter-clockwise positive (angle may be in range -360. to 360.)
            origin ('N'|'S'):
                origin of bearing (south/north)
                'N' >>> North Azimuth system (clockwise from N)
                'S' >>> South Azimuth system (counter-clockwise from S)
        '''
        if angle < -360. or angle > 360.:
            raise ValueError('Invalid angle {0}. Must be in range [-360.:360.]').format(angle)
        
        if origin == 'N':
            b = (360. - (angle - 90.)) % 360.
        elif origin == 'S':
            b = (360. + (angle + 90.)) % 360.
        else:
            raise NotImplementedError()
        return (b, origin)
    
    class Example(QtGui.QGraphicsView):
    
        def __init__(self):
            super(Example, self).__init__()
            
            self.initUI()
            
        def initUI(self):

            self.setGeometry(300, 300, 300, 300)
            self.setWindowTitle('Points')


            scene = QtGui.QGraphicsScene()
            scene.setSceneRect(-100, -100, 200, 200)  #set scene to be 200x200 with 0, 0 beeing the center point
            self.setScene(scene)
            self.scale(1, -1)  #reverse positive directions to match those in a common mathematical x/y plane
            
            self.drawAxes()
            self.show()
        
        def drawAxes(self):
            pen = QtGui.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.SolidLine)

            #xAxes = QtCore.QLineF(-90, 0, 90, 0)
            #yAxes = QtCore.QLineF(0, -90, 0, 90)
            xAxes = myArrow(QtCore.QPointF(0, -90), QtCore.QPointF(0, 90), arrowHeadSize=5, lineWidth=0.5)
            yAxes = myArrow(QtCore.QPointF(-90, 0), QtCore.QPointF(90, 0), arrowHeadSize=5, lineWidth=0.5)
            scene = self.scene()
            scene.addItem(xAxes)
            scene.addItem(yAxes)

            self.axesItems = [xAxes, yAxes]




        def drawPoints(self):
            
            scene = self.scene()

            #for i in range(3):
            #    angle = random.randint(0, 0)
            for angle in [0]:

                print 'adding arrow: angle', angle
                #angle = angle + 90  #conversion to set the theta=0 to the y-axes direction, the theta > 0 direction is already clock-wise
                angle = angle2bearing(angle)[0]
                arrow = myArrow(QtCore.QPointF(0, 0), None, angle=angle, color=QtCore.Qt.blue)
                scene.addItem(arrow)

        def clearArrows(self):
            '''
                Method clears the scene from all items except axes
            '''
            for item in self.items():
                if item in self.axesItems:
                    print 'not removing item:', item
                    continue
                if isinstance(item, myArrow):
                    print 'removing item:', item
                    self.scene().removeItem(item)
            print 'finished clearing'

        def keyPressEvent(self, event):
            print 'key pressed', event.key()
            if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Backspace]:
                self.clearArrows()
                event.accept()
            else:
                event.ignore()
            print 'finished event'

            
    def main():
        app = QtGui.QApplication(sys.argv)
        ex = Example()
        ex.drawPoints()
        #ex.clearArrows()
        #ex.drawPoints()
        #ex.clearArrows()

        sys.exit(app.exec_())



    main()
