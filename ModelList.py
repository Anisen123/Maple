'''Class which contains list which shows all models in sql database/applicable models from selected constraints.
Functions->
view: displays alternate view in model list widget which shows all models in order to add/edit/delete from database
addModel: form for adding model
saveAddMd: saves above form
editModel: form for editing selected model
saveEditMd: saves above changes
delMd: deletes selected model
closeMdForm: hides form
createCombo: combobox which displays list of models in form for setting similar to
setSimilar: assigns attributes from selected model to new model
dispMdDet: displays models details of selected model: on double-clicking
'''



from math import cos
from filemapping import *
from UniqueModel import UniqueModel
import copy
from PyQt5 import QtCore, QtWidgets
CustomObjectRole = QtCore.Qt.UserRole + 1
from PyQt5.QtWidgets import *
import sqlite3

class ModelList:
    def __init__(self,mdlist):
        self.count = 1
        self.mdlist = mdlist
        self.conn = sqlite3.connect("ObjectData.db") 
        self.cur = self.conn.cursor()#cursor object connected to sql database
        
    def view(self): #alternate view in model list which shows all models in order to add/edit/delete from database
        self.count = 1
        self.cur.execute('SELECT * FROM models')
        self.mdlist.clear()
        for row in self.cur:
            md = UniqueModel("#" + str(self.count) + " " + row[Model], row[Model], row[Hardware], row[Hardware], row[Cores], row[Cores], row[Memory], row[Latency], row[Latency], row[Cost], row[Cost], "Not Selected", row[Domain], row[Library], "Not Selected", 0.0, "None")
            item = QtWidgets.QListWidgetItem(str(md.ID))
            self.mdlist.addItem(item)
            item.setData(CustomObjectRole, md)
            self.count += 1
    
    def addModel(self): #form for adding model
        self.view()
        self.mdbox = QGroupBox("Add new model to database")
        self.mdlayout = QFormLayout()
        self.l0 = QLabel("Model Name:")
        self.e0 = QLineEdit()
        self.ch = QCheckBox("Set Similar To")
        self.ch.toggled.connect(self.setSimilar)
        self.mdcombo = QComboBox()
        self.createCombo()
        self.mdcombo.currentIndexChanged.connect(self.setSimilar)
        self.l1 = QLabel("Cores:")
        self.e1 = QSpinBox()
        self.e1.setMaximum(999999)
        self.l2 = QLabel("Memory:")
        self.e2 = QSpinBox()
        self.e2.setMaximum(999999)
        self.l3 = QLabel("Latency:")
        self.e3 = QDoubleSpinBox()
        self.e3.setMaximum(999999)
        self.e3.setSuffix(" ms")
        self.l4 = QLabel("Hardware:")
        self.e4 = QLineEdit()
        self.l5 = QLabel("Cost:")
        self.e5 = QDoubleSpinBox()
        self.e5.setMaximum(9999999)
        self.e5.setSuffix("$")
        self.l6 = QLabel("Application Domain:")
        self.e6 = QLineEdit()
        self.l7 = QLabel("Library:")
        self.e7 = QLineEdit()
        
        self.mdlayout.addRow(self.l0,self.e0)
        self.mdlayout.addRow(self.l6,self.e6)
        self.mdlayout.addRow(self.ch,self.mdcombo)
        self.mdlayout.addRow(self.l1,self.e1)
        self.mdlayout.addRow(self.l2,self.e2)
        self.mdlayout.addRow(self.l3,self.e3)
        self.mdlayout.addRow(self.l4,self.e4)
        self.mdlayout.addRow(self.l5,self.e5)
        self.mdlayout.addRow(self.l7,self.e7)

        self.ok = QPushButton("Save Model")
        self.cancel = QPushButton("Cancel")
        self.mdlayout.addRow(self.ok, self.cancel)
        self.ok.clicked.connect(lambda x: self.saveAddMd(self.e0.text(),self.e1.value(),self.e2.value(),self.e3.value(),self.e4.text(),self.e5.value(),self.e6.text(),self.e7.text()))
        self.cancel.clicked.connect(self.closeMdForm)
        self.mdbox.setLayout(self.mdlayout)
        self.mdbox.show()

    def saveAddMd(self,model,cores,memory,latency,hardware,cost,domain,library):
        md = UniqueModel("#" + str(self.count) + " " + model, model, hardware, hardware, cores, cores, memory, latency, latency, cost, cost, "Not Selected", domain, library, "Not Selected", 0.0, "None")
        item = QtWidgets.QListWidgetItem(str(md.ID))
        self.mdlist.addItem(item)
        item.setData(CustomObjectRole, md)
        self.count = self.count + 1
        self.mdbox.hide()
        model = (model,hardware,cores,memory,latency,cost,domain,library,"")
        sql = ''' INSERT INTO models VALUES(?,?,?,?,?,?,?,?,?) '''
        self.cur.execute(sql, model)
        self.conn.commit()
        self.view()
        
    def editModel(self,item): #form for editing model
        md = item.data(CustomObjectRole)
        self.view()
        self.mdbox = QGroupBox()
        self.mdlayout = QFormLayout()
        self.l0 = QLabel("Model: " + md.ID)
        self.l1 = QLabel("Cores:")
        self.e1 = QSpinBox()
        self.e1.setValue(copy.deepcopy(md.Cores))
        self.e1.setMaximum(999999)
        self.l2 = QLabel("Memory:")
        self.e2 = QSpinBox()
        self.e2.setValue(md.Memory)
        self.e2.setMaximum(999999)
        self.l3 = QLabel("Latency:")
        self.e3 = QDoubleSpinBox()
        self.e3.setMaximum(999999)
        self.e3.setSuffix(" ms")
        self.e3.setValue(md.Latency)
        self.l4 = QLabel("Hardware:")
        self.e4 = QLineEdit()
        self.e4.setText(md.Hardware)
        self.l5 = QLabel("Cost:")
        self.e5 = QDoubleSpinBox()
        self.e5.setMaximum(9999999)
        self.e5.setSuffix("$")
        self.e5.setValue(md.Cost)
        self.l6 = QLabel("Application Domain:")
        self.e6 = QLineEdit()
        self.e6.setText(copy.deepcopy(md.Domain))
        self.l7 = QLabel("Library:")
        self.e7 = QLineEdit()
        self.e7.setText(md.Library)

        self.mdlayout.addRow(self.l0)
        self.mdlayout.addRow(self.l1,self.e1)
        self.mdlayout.addRow(self.l2,self.e2)
        self.mdlayout.addRow(self.l3,self.e3)
        self.mdlayout.addRow(self.l4,self.e4)
        self.mdlayout.addRow(self.l5,self.e5)
        self.mdlayout.addRow(self.l6,self.e6)
        self.mdlayout.addRow(self.l7,self.e7)

        self.ok = QPushButton("Save Changes")
        self.cancel = QPushButton("Cancel")
        self.mdlayout.addRow(self.ok, self.cancel)
        self.ok.clicked.connect(lambda x: self.saveEditMd(self.e1.value(),self.e2.value(),self.e3.value(),self.e4.text(),self.e5.value(),self.e6.text(),self.e7.text(),md))
        self.cancel.clicked.connect(self.closeMdForm)
        self.delete = QPushButton("Delete Model")
        self.delete.clicked.connect(lambda x: self.delMd(md))
        self.mdlayout.addRow(self.delete)
        self.mdbox.setLayout(self.mdlayout)
        self.mdbox.show()
        
    def saveEditMd(self,cores,memory,latency,hardware,cost,domain,library,md): #unique id can be added to identify model uniquely, and delete with respect to that id. Maybe rowid?
        model = (cores,memory,latency,hardware,cost,domain,library,md.Model,md.Cores,md.Domain)
        sql = ''' UPDATE models SET Cores = ?, Memory = ? ,Latency = ?, Hardware = ?, Cost = ?, Domain = ?, Framework = ? WHERE Model=? AND Cores=? AND Domain =?''' #Identification of model is not unique in this case, but temporarily workable 
        self.cur.execute(sql, model)
        self.conn.commit()
        self.mdbox.hide()
        md.Cores = cores
        md.Memory = memory
        md.Latency = latency
        md.Hardware = hardware
        md.Cost = cost
        md.Domain = domain
        md.Library = library
        self.view()

    def delMd(self,md): #same comments as above for edit are applicable for delete
        domain = md.Domain
        cores = md.Cores
        model = md.Model
        sql = ''' DELETE FROM models WHERE Model=? AND Cores=? AND Domain=? ''' 
        self.cur.execute(sql, (model,cores,domain))
        self.conn.commit()
        self.mdlist.takeItem(self.mdlist.currentRow())
        self.mdbox.hide()
        self.view()

    def closeMdForm(self):
        self.mdbox.hide()

    def createCombo(self):
        self.mdcombo.addItem("Select Model")
        for i in range(self.mdlist.count()):
            self.mdcombo.addItem(self.mdlist.item(i).text(),self.mdlist.item(i).data(CustomObjectRole))

    def setSimilar(self,index):
        if(index == 0):
            return
        if(self.ch.isChecked()):
            model = self.mdcombo.itemData(index)
            self.e1.setValue(model.Cores)
            self.e2.setValue(model.Memory)
            self.e3.setValue(model.Latency)
            self.e5.setValue(model.Cost)
       
    def dispMdDet(self,item):
        md = item.data(CustomObjectRole)
        attrs = vars(md)
        msg = QMessageBox()
        msg.setWindowTitle("Model Details")
        msg.setText(''.join("%s: %s\n" % item for item in attrs.items()))
        x = msg.exec_()