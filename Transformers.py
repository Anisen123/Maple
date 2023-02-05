'''Class which contains transformer and list of transformers populated from ObjectData.db.
Functions->
addTransformer: form for adding transformer
saveAddTfr: saves above form
editTfr: form for editing selected transformer
saveEditTfr: saves above changes made to transformer
delTfr: deletes selected transformer
closeTfrForm: closes above form
dispTfrDet: displays details of atteibutes of selected transformer on double-click
'''

import copy
from PyQt5 import QtCore, QtWidgets
CustomObjectRole = QtCore.Qt.UserRole + 1
from PyQt5.QtWidgets import *
import sqlite3

class Transformer: #Tranformer data for Shape()
    ID: int
    Cost: float
    Latency: float
    Type: str

    def __init__(self, id, cost, latency, type):
        self.ID = id 
        self.Cost = cost
        self.Latency = latency
        self.Type = type

class TransformerList: #List of transformers displayed in Widgets() : passed as listwidget parameter
    def __init__(self,listwidget,diagram):
        self.count = 1
        self.listwidget = listwidget
        self.diagram = diagram
        self.conn = sqlite3.connect("ObjectData.db")
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT * FROM Transformers') #Displays details of transformers in database
        self.listwidget.clear()
        for row in self.cur:
            tfr = Transformer(self.count,row[0],row[1],row[2])
            item = QListWidgetItem("Transformer" + str(tfr.ID))
            listwidget.addItem(item)
            self.diagram.updateTfrList(tfr)
            item.setData(CustomObjectRole, tfr)
            self.count += 1
        

    def addTransformer(self): #form for adding transformer
        self.tfrbox = QGroupBox()
        self.tfrlayout = QFormLayout()
        self.l1 = QLabel("Cost:")
        self.e1 = QSpinBox()
        self.e1.setMaximum(9999999)
        self.e1.setSuffix("$")
        self.l2 = QLabel("Latency:")
        self.e2 = QSpinBox()
        self.e2.setMaximum(9999999)
        self.e2.setSuffix(" ms")
        self.l3 = QLabel("Type:")
        self.e3 = QLineEdit()
        self.tfrlayout.addRow(self.l1,self.e1)
        self.tfrlayout.addRow(self.l2,self.e2)
        self.tfrlayout.addRow(self.l3,self.e3)
        self.ok = QPushButton("Save Transformer")
        self.cancel = QPushButton("Cancel")
        self.tfrlayout.addRow(self.ok, self.cancel)
        self.ok.clicked.connect(lambda x: self.saveAddTfr(self.e1.value(),self.e2.value(),self.e3.text()))
        self.cancel.clicked.connect(self.closeTfrForm)
        self.tfrbox.setLayout(self.tfrlayout)
        self.tfrbox.show()

    def saveAddTfr(self,cost,latency,type):
        tfr = Transformer(self.count,cost,latency,type)
        item = QtWidgets.QListWidgetItem("Transformer" + str(tfr.ID))
        self.listwidget.addItem(item)
        item.setData(CustomObjectRole, tfr)
        self.count = self.count + 1
        self.diagram.updateTfrList(tfr)
        self.tfrbox.hide()
        transformer = (cost,latency,type)
        sql = ''' INSERT INTO Transformers VALUES(?,?,?) '''
        self.cur.execute(sql, transformer)
        self.conn.commit()
        
    def editTfr(self,item): #form for editing transformer
        tfr = item.data(CustomObjectRole)
        self.tfrbox = QGroupBox()
        self.tfrlayout = QFormLayout()
        self.l1 = QLabel("Cost:")
        self.e1 = QSpinBox()
        self.e1.setSuffix("$")
        self.l2 = QLabel("Latency:")
        self.e2 = QSpinBox()
        self.e2.setSuffix(" ms")
        self.l3 = QLabel("Type:")
        self.e3 = QLineEdit()
        self.tfrlayout.addRow(self.l1,self.e1)
        self.tfrlayout.addRow(self.l2,self.e2)
        self.tfrlayout.addRow(self.l3,self.e3)
        self.e1.setValue(copy.deepcopy(tfr.Cost))
        self.e1.setMaximum(9999999)
        self.e2.setValue(copy.deepcopy(tfr.Latency))
        self.e2.setMaximum(9999999)
        self.e3.setText(copy.deepcopy(tfr.Type))
        self.edit = QPushButton("Save Changes")
        self.cancel = QPushButton("Cancel")
        self.edit.clicked.connect(lambda x: self.saveEditTfr(self.e1.value(),self.e2.value(),self.e3.text(),tfr))
        self.cancel.clicked.connect(self.closeTfrForm)
        self.tfrlayout.addRow(self.edit, self.cancel)
        self.delete = QPushButton("Delete Transformer")
        self.tfrlayout.addRow(self.delete)
        self.delete.clicked.connect(lambda x: self.delTfr(item))
        self.tfrbox.setLayout(self.tfrlayout)
        self.tfrbox.show()
        
    def saveEditTfr(self,cost,latency,type,tfr):
        transformer = (cost,latency,type,tfr.Cost,tfr.Latency,tfr.Type)
        sql = ''' UPDATE Transformers SET Cost = ? ,Latency = ? ,Type = ? WHERE Cost=? AND Latency=? AND Type =?'''
        self.cur.execute(sql, transformer)
        self.conn.commit()
        self.tfrbox.hide()
        tfr.Cost = cost
        tfr.Latency = latency
        tfr.Type = type
        self.view()

    def delTfr(self,item):
        tfr = item.data(CustomObjectRole)
        cost = tfr.Cost
        latency = tfr.Latency
        type = tfr.Type
        sql = ''' DELETE FROM Transformers WHERE Cost=? AND Latency=? AND Type =? '''
        self.cur.execute(sql, (cost,latency,type))
        self.conn.commit()
        self.listwidget.takeItem(self.listwidget.currentRow())
        self.tfrbox.hide()
        self.diagram.removeTfrFromList(tfr)

    def closeTfrForm(self):
        self.tfrbox.hide()

    def dispTfrDet(self,item):
        tfr = item.data(CustomObjectRole)
        attrs = vars(tfr)
        msg = QMessageBox()
        msg.setWindowTitle("Data Transformer Details")
        msg.setText(''.join("%s: %s\n" % item for item in attrs.items()))
        x = msg.exec_()