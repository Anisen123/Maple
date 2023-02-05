'''Class for all non-model objects in diagram.
Functions->
mousePressEvent: makes shape selected in diagram
mouseDoubleClickEvent: does nothing but necessary for parent call
contextMenuEvent: displays right-click menu
addTfr: adds transformer details of selected transformer to shape
displayDetails: displays all shape attributes
del: deletes all connected arrows
addInLink: adds incoming arrow
addOutLink: adds outgoing arrow
itemChange: sends signal for updating position of arrows
pos1: returns centre coordinate of shape in diagram
getList: returns list of attributes for saving
'''


import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsTextItem, QMenu, QMessageBox
from PyQt5.QtCore import QPointF, QSize, Qt
import time

class Shape(QGraphicsEllipseItem): #All objects in diagram which are not models
    def __init__(self,text,a,b,cost,latency,type1):
        
        super().__init__(0,0,a,b)
        self.in_arrows = []
        self.out_arrows = []
        self.setBrush(Qt.white)
        self.setPos(0,0)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.text = text
        self.a = a
        self.b = b
        self.selectedTime = None
        self.tfrs = []
        self.Cost = cost
        self.Latency = latency
        self.Type1 = type1
        
        if(text == "S"):
            self.textItem = QGraphicsPixmapItem(QPixmap("storage.png").scaled(QSize(20,20)),self) #named as textItem to simplify saving
            rect = self.textItem.boundingRect()
            rect.moveCenter(self.boundingRect().center())
            self.textItem.setPos(rect.topLeft())
            self.setPen(Qt.white)
        else:
            self.textItem = QGraphicsTextItem(self)
            self.textItem.setHtml('<center>' + text + '</center>')
            self.textItem.setTextWidth(self.boundingRect().width())
            rect = self.textItem.boundingRect()
            rect.moveCenter(self.boundingRect().center())
            self.textItem.setPos(rect.topLeft())
            

    # mouse hover event
    #def hoverEnterEvent(self, event):
    #    app.instance().setOverrideCursor(Qt.OpenHandCursor)

    #def hoverLeaveEvent(self, event):
    #    app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
            self.setSelected(True)

    def mouseDoubleClickEvent(self, event):
        pass
    
    #Print release coordinates
    #def mouseReleaseEvent(self, event):
    #    print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))

    #app = QApplication(sys.argv)

    def contextMenuEvent(self, event): #show on right click. Add condition to show menu only on right click. Event filter?
        menu = QMenu()
        detailsaction = menu.addAction("Show Model Details")
        detailsaction.triggered.connect(self.displayDetails)
        tfrsub = QMenu("Select Transformer")
        for tfr in self.tfrs:
            serveraction = tfrsub.addAction("Transformer" + str(tfr.ID))
            serveraction.triggered.connect(lambda chk, tfr=tfr: self.addTfr(tfr))
        menu.addMenu(tfrsub)
        menu.exec(event.screenPos())

    def addTfr(self,tfr): #add transformer details of selected transformer to shape 
        attrs = vars(tfr)
        self.Cost = attrs["Cost"]
        self.Latency=  attrs["Latency"]
        self.Type1 = attrs["Type"]

    def displayDetails(self):
        msg = QMessageBox()
        msg.setWindowTitle("Transformer Details")
        msg.setText("Cost: " + str(self.Cost) + "$\nLatency: " + str(self.Latency) + " ms\nType: " + self.Type1)
        x = msg.exec_()

    def __del__(self):
        for arrow in self.in_arrows:
            self.in_arrows.remove(arrow)
        for arrow in self.out_arrows:
            self.out_arrows.remove(arrow)

    def addInLink(self, arrow):
        self.in_arrows.append(arrow)

    def addOutLink(self,arrow):
        self.out_arrows.append(arrow)

    def itemChange(self,change,value): #update position of arrows
        if change == self.ItemPositionChange:
            for arrow in self.in_arrows:
                arrow.trackNodes()
            for arrow in self.out_arrows:
                arrow.trackNodes()
        if (change == self.ItemSelectedChange):
            self.selectedTime = time.time()
        return super(Shape, self).itemChange(change, value)
    
    def pos1(self): #centre of object
        xOffset = self.rect().x() + self.rect().width()/2
        yOffset = self.rect().y() + self.rect().height()/2
        return QPointF(self.pos().x() + xOffset, self.pos().y()+yOffset)

    def getList(self): #return relevant attributes for saving
        self.list = [self.text,self.a,self.b,self.Cost,self.Latency,self.Type1]
        str = ["Shape",self.scenePos().x(),self.scenePos().y()]
        str += self.list
        return str


    
