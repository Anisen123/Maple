'''Class for all models in diagram, contains corresponding UniqueModel.
Functions->
displayDetails: displays all model attributes
mousePressEvent: makes model selected in diagram
contextMenuEvent: displays right-click menu
addInLink: adds incoming arrow
addOutLink: adds outgoing arrow
itemChange: sends signal for updating position of arrows
pos1: returns centre coordinate of model shape in diagram
changeLatency: changes latency of self.model (UniqueModel)
makeBatch: makes model mode batch
makeRealTime: makes model mode realtime
cloudOptions: displays form for selected required cloud configuration
costText: displays cost in above form
update: updates selected cost to self.model
closeForm: closes above form
addConfig: adds selected configuration to self.model
overheadBox: form for adding ovehead cost or latency
closeOverhead: closes above form
getList: returns list of attributes for saving
'''

import sys
from PyQt5 import QtCore
from CloudCost import CloudCost, calcAllCosts
from PyQt5.QtWidgets import QApplication, QCheckBox, QDoubleSpinBox, QFormLayout, QGraphicsRectItem, QGraphicsTextItem, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QRadioButton, QSpinBox
from PyQt5.QtCore import QPointF, Qt
import time
import copy
CustomObjectRole = QtCore.Qt.UserRole + 1

class ModelShape(QGraphicsRectItem): #class for all models in diagram, contains corresponding UniqueModel
    def __init__(self,model):
        super().__init__(0,0,100,50)
        self.setPos(0,0)
        self.setBrush(Qt.white)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        
        #font = QFont()
        #font.setPointSize(20)
        #self.textItem.setFont(font)
        self.model = model
        self.textItem = QGraphicsTextItem(self)
        self.textItem.setHtml('<center>' + model.ID + '</center>')
        self.textItem.setTextWidth(self.boundingRect().width())
        rect = self.textItem.boundingRect()
        rect.moveCenter(self.boundingRect().center())
        self.textItem.setPos(rect.topLeft())
        
        self.in_arrows = []
        self.out_arrows = []
        self.selectedTime = None
        self.configs = []
        self.Cost = self.model.Cost
        self.Latency = self.model.Latency
        
    # mouse hover event
    #def hoverEnterEvent(self, event):
    #    app.instance().setOverrideCursor(Qt.OpenHandCursor)

    #def hoverLeaveEvent(self, event):
    #    app.instance().restoreOverrideCursor()

    def displayDetails(self):
        attrs = copy.deepcopy(vars(self.model))
        attrs.pop("InitialCores")
        attrs.pop("InitialHardware")
        attrs.pop("InitialLatency")
        attrs.pop("InitialCost")
        msg = QMessageBox()
        msg.setWindowTitle("Model Details")
        msg.setText(''.join("%s: %s\n" % item for item in attrs.items()))
        x = msg.exec_()
    
    # mouse click event
    def mousePressEvent(self, event):
        self.setSelected(True)

    def contextMenuEvent(self, event):#edit to show menu only on right click. Event filter?
        menu = QMenu()
        detailsaction = menu.addAction("Show Model Details") #adds option in menu
        detailsaction.triggered.connect(self.displayDetails)
        latencyaction = menu.addAction("Change Latency")
        latencyaction.triggered.connect(self.changeLatency)
        modesub = QMenu("Select Application Mode")
        batchaction = modesub.addAction("Batch")
        batchaction.triggered.connect(self.makeBatch)
        rtaction = modesub.addAction("Realtime")
        rtaction.triggered.connect(self.makeRealTime)
        menu.addMenu(modesub)
        serversub = QMenu("Select Server Config")
        for config in self.configs:
            serveraction = serversub.addAction(config.ID)
            serveraction.triggered.connect(lambda chk, config=config: self.addConfig(config))
        menu.addMenu(serversub)
        overheadaction = menu.addAction("Add Overhead")
        overheadaction.triggered.connect(self.overheadBox)
        cloudaction = menu.addAction("Cloud Deployment Options")
        cloudaction.triggered.connect(self.cloudOptions)
        menu.exec(event.screenPos())
    
    #Print release coordinates
    #def mouseReleaseEvent(self, event):
    #    print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))

#app = QApplication(sys.argv)

    def addInLink(self, arrow):
        self.in_arrows.append(arrow)

    def addOutLink(self,arrow):
        self.out_arrows.append(arrow)

    def itemChange(self, change, value): #update position of arrows
        if change == self.ItemPositionChange: 
            for arrow in self.in_arrows:
                arrow.trackNodes()
            for arrow in self.out_arrows:
                arrow.trackNodes()
        if(change == self.ItemSelectedChange):
            self.selectedTime = time.time()
        return super(ModelShape, self).itemChange(change, value)
    
    def pos1(self): #centre of object
        xOffset = self.rect().x() + self.rect().width()/2
        yOffset = self.rect().y() + self.rect().height()/2
        return QPointF(self.pos().x() + xOffset, self.pos().y()+yOffset)

    def changeLatency(self): 
        widget = QLineEdit()
        num, ok = QInputDialog.getInt(None, 'Change Latency', 'Enter New Latency:', self.model.Latency,1)
        if ok:
            self.model.setLatency(num)
            if(self.model.CloudCost != 0):
                self.update(self.requestsbox.value(),self.speedbox.value(),self.storagebox.value())

    def makeBatch(self):
        self.model.Mode = "Batch"

    def makeRealTime(self):
        self.model.Mode = "Realtime"

    #Functions for calculating cost of deploying model to cloud
    def cloudOptions(self): 
        self.formGroupBox = QGroupBox()
        self.formGroupBox.setWindowTitle("Cloud Deployment Options")
        self.layout = QFormLayout()
        self.currcloud = QLabel("Cloud Provider: " + self.model.CloudProvider + "\nInstance: " + self.model.CloudInstance + "\nCost: " + str(self.model.CloudCost))
        self.layout.addRow(self.currcloud)
        self.serverbutton = QCheckBox()
        if(self.model.Hardware == "Serverless"):
            self.serverbutton.setChecked(True)
        else:
            self.serverbutton.setChecked(False)
        self.layout.addRow(QLabel("Serverless"),self.serverbutton)
        self.requestsbox = QSpinBox()
        self.requestsbox.setMaximum(2147483647)
        self.speedbox = QSpinBox()
        self.speedbox.setMaximum(100000)
        self.speedbox.setSuffix(" MHz")
        self.hourbox = QSpinBox()
        self.hourbox.setMaximum(1000000)
        self.storagebox = QSpinBox()
        self.storagebox.setMaximum(100000)
        self.storagebox.setSuffix(" GB")
        self.layout.addRow(QLabel("Number of Requests:"), self.requestsbox)
        self.layout.addRow(QLabel("Core Speed (For GCP Severless):"), self.speedbox)
        self.layout.addRow(QLabel("No of hours required:"), self.hourbox)
        self.layout.addRow(QLabel("Storage Required:"), self.storagebox) #add calculation for storage cost to total cost - monthly cost?
        hbox = QHBoxLayout()
        self.r1 = QRadioButton("AWS")
        self.r2 = QRadioButton("Azure")
        self.r3 = QRadioButton("GCP")
        hbox.addWidget(self.r1)
        hbox.addWidget(self.r2)
        hbox.addWidget(self.r3)
        hbox.addStretch()
        self.layout.addRow(QLabel("Choose Cloud Provider"),hbox)
        ok = QPushButton("Display Cost")
        cancel = QPushButton("Cancel")
        self.layout.addRow(ok)
        ok.clicked.connect(lambda x: self.costText(self.requestsbox.value(),self.speedbox.value(),self.hourbox.value(),self.storagebox.value()))
        cancel.clicked.connect(self.closeForm)
        update = QPushButton("Update Configuration")
        self.layout.addRow(update,cancel)
        update.clicked.connect(lambda x: self.update(self.requestsbox.value(),self.speedbox.value(),self.storagebox.value()))

        self.formGroupBox.setLayout(self.layout)
        self.formGroupBox.show()
    
    def costText(self,requests,speed,hours,storage):
        try:
            self.costObject == None
        except AttributeError:
            self.costObject = CloudCost()
        self.costs = calcAllCosts(self.costObject,self.model.Cores,self.model.Memory,self.model.Latency,requests,speed) #gets all costs from CloudCost() class
        if(self.serverbutton.isChecked()):
            self.r1.setText("AWS (Cost: " + str(self.costs[0][1]) + "$)")
            self.r2.setText("Azure (Cost: " + str(self.costs[1][1]) + "$)")
            self.r3.setText("GCP (Cost: " + str(self.costs[2][1]) + "$)")
        else:
            self.r1.setText("AWS (Cost: " + str(self.costs[0][0][0]) + "$ hourly, Total: " + str(self.costs[0][0][0]*hours) + "$)")
            self.r2.setText("Azure (Cost: " + str(self.costs[1][0][0]) + "$ hourly, Total: " + str(self.costs[1][0][0]*hours) + "$)")
            self.r3.setText("GCP (Cost: " + str(self.costs[2][0][0]) + "$ hourly, Total: " + str(self.costs[2][0][0]*hours) + "$)")
            
    def update(self,requests,speed,storage):
        try:
            self.costObject == None
        except AttributeError:
            self.costObject = CloudCost()
        self.costs = calcAllCosts(self.costObject,self.model.Cores,self.model.Memory,self.model.Latency,requests,speed)
        if(self.serverbutton.isChecked()):
            self.model.Hardware = "Serverless"
            self.model.CloudInstance = "Serverless"
            if(self.r1.isChecked()):
                self.model.CloudProvider = "AWS"
                self.model.CloudCost = self.costs[0][1]
            elif(self.r2.isChecked()):
                self.model.CloudProvider = "Azure"
                self.model.CloudCost = self.costs[1][1]
            elif(self.r3.isChecked()):
                self.model.CloudProvider = "GCP"
                self.model.CloudCost = self.costs[2][1]
        else:
            self.model.Hardware = self.model.InitialHardware
            if(self.r1.isChecked()):
                self.model.CloudProvider = "AWS"
                self.model.CloudInstance = self.costs[0][0][1]
                self.model.CloudCost = self.costs[0][0][0]*self.hourbox.value()
            elif(self.r2.isChecked()):
                self.model.CloudProvider = "Azure"
                self.model.CloudInstance = self.costs[1][0][1]
                self.model.CloudCost = self.costs[1][0][0]*self.hourbox.value()
            elif(self.r3.isChecked()):
                self.model.CloudProvider = "GCP"
                self.model.CloudInstance = self.costs[2][0][1]
                self.model.CloudCost = self.costs[2][0][0]*self.hourbox.value()
        self.currcloud.setText("Provider: " + self.model.CloudProvider + "\nInstance: " + self.model.CloudInstance + "\nCost: " + str(self.model.CloudCost) + "$")

    def closeForm(self):
        self.formGroupBox.hide()


    #Functions for adding configuration
    def addConfig(self,config):
        attrs = vars(config)
        if(attrs["GPUModel"] != ""):
            self.model.Hardware = "GPU: " + attrs["GPUModel"]
        self.model.setCores(attrs["Cores"])
        self.model.setMemory(attrs["Memory"])
        if(self.model.CloudCost != 0):
            self.update(self.requestsbox.value(),self.speedbox.value(),self.storagebox.value())
    
    def overheadBox(self):
        self.ovbox = QGroupBox()
        self.ovbox.setWindowTitle("Add Overhead")
        layout = QFormLayout()
        l1 = QLabel("Overhead Cost: x")
        e1 = QDoubleSpinBox()
        e1.setValue(1.00)
        l2 = QLabel("Overhead Latency: x")
        e2 = QDoubleSpinBox()
        e2.setValue(1.00)
        layout.addRow(l1,e1)
        layout.addRow(l2,e2)
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        layout.addRow(ok,cancel)
        ok.clicked.connect(lambda x: self.addOverhead(e1.value(),e2.value()))
        cancel.clicked.connect(self.closeOverhead)
        self.ovbox.setLayout(layout)
        self.ovbox.show()
    
    def addOverhead(self,ovcost,ovlatency):
        if((0.1 <= ovcost <= 10.0) and (0.1 <= ovlatency <= 10.0)):
            self.model.Cost *= ovcost
            self.model.Latency  *= ovlatency
            self.closeOverhead()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Invalid Input")
            msg.setText("Enter float value between 0.1 and 10.0")
            msg.exec_()

    def closeOverhead(self):
        self.ovbox.hide()
        
    #list of attributes for saving model
    def getList(self):
        str = ["Model",self.scenePos().x(),self.scenePos().y()] 
        str += [*(vars(self.model).values())]
        return str


