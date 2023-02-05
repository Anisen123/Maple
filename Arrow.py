'''Class which defines arrows contained in diagram. 
Functions-> 
mousePressEvent: reverses direction of arrow
trackNodes: adjusts positions of arrow on changing coordinates of end objects
paint: paints arrowhead
'''
from PyQt5 import QtGui
from PyQt5.QtCore import QLine, QLineF, QPointF, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsLineItem
import math

class Arrow(QGraphicsLineItem):
    def __init__(self,start_item, end_item):
        self.arrowHead = QPolygonF()
        super().__init__(0,0,2,2)
        self.start_item = start_item
        self.end_item = end_item
        self.start_item.addOutLink(self)  #send information for arrows connected to node
        self.end_item.addInLink(self)
        self.trackNodes()
        self.setFlag(self.ItemIsSelectable, True)
        self.setZValue(-1) 

    def mousePressEvent(self, event):
        temp = self.end_item
        self.end_item = self.start_item
        self.start_item = temp

    def trackNodes(self):
        self.setLine(QLineF(self.start_item.pos1(), self.end_item.pos1()))
        self.update(self.arrowHead.boundingRect())

    def paint(self,painter,option,widget):  #for painting arrowhead
        self.arrowHead.clear()
        start = self.start_item.pos1()
        end = self.end_item.pos1()

        painter.setRenderHint(painter.Antialiasing)
        arrowSize = 20
        painter.setPen(Qt.black)
        painter.setBrush(Qt.black)

        line1 = QLineF(end, start)
        """m =  (end.y() - start.y())/(end.x() - start.x()) #slope of line
        b = self.end_item.boundingRect().width()
        a = self.end_item.boundingRect().height()  -> code to make arrowhead touch border of shape to which it is pointing 
        t = (b*b)/(a*a)
        end_point_x = math.sqrt((t*t)/(t*t + m*m))
        end_point_y = end_point_x*m
        end_point = QPointF(end_point_x,end_point_y)"""
        line = QLineF(line1.pointAt(0.3),start)
        #line = QLineF(end_point,start)

        angle = math.atan2(-line.dy(), line.dx())
        arrowP1 = QPointF(line.p1() + QPointF(math.sin(angle + math.pi / 3) * arrowSize,math.cos(angle + math.pi / 3) * arrowSize))
        arrowP2 = QPointF(line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 3) * arrowSize, math.cos(angle + math.pi - math.pi / 3) * arrowSize))

        
        self.arrowHead << line.p1() << arrowP1 << arrowP2 
        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)