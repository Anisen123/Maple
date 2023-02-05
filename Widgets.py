'''Class which contains all widgets in GUI window. It is itself placed in MainWindow.
Functions->
UIComponents: adds all widgets to window
attribute_changed: populates list of applicable models from ObjectData.db under specifed constraints
listwidgetdoubleclicked: displays details of model double-clicked in model list
listwidgetclicked: adds selected model to self.shape in diagram or show edit form in edit-model mode (on clicking edit/delete model button)
tfrListClicked: allows transformer in transformer list to be edited if edit/delete transformer button is clicked
extrapolate_cost: extrapolates cost of model with reduced cost, from existing list of models having the same name. Returns dictionary of (model name: polynomial fitted to existing data of cost vs cores)
buttonCloudClicked: displays total cost of deploying all models in diagram to cloud
cloudCostSelected: makes above button visible 
dispTotCost: displays total cost of all objects in diagram
dispTotLat: displays total latency of diagram pipeline. Calls Netlatency function in diagram class.
configButtonClicked: form for adding new config to config list
saveConfig: saves aboves form
closeConfigForm: closes above form
gpuchecked: shows options for gpu type in above form, only when gpu option is checked
dispConfigDet: displays details of configuration when double-clicked
addApp: form for adding new application to application list
saveApp: saves above form
closeApp: closes above form
save: saves diagram, applications and configs to csv
load: loads saved diagram
load_helper: helper function for load
'''

from ModelShape import ModelShape
from Shape import Shape
from Arrow import Arrow
from ModelList import ModelList
from Transformers import TransformerList
from Config import Config
from PyQt5.QtGui import QFont
from Diagram import GraphicView
from PyQt5 import QtWidgets
from UniqueModel import UniqueModel
from filemapping import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import copy
import numpy as np
import sqlite3
from numpy.polynomial import Polynomial
import csv
CustomObjectRole = QtCore.Qt.UserRole + 1

db_conn = sqlite3.connect("ObjectData.db")
c = db_conn.cursor()

class Widgets(QWidget):  #Displays all the widgets in Main Window

    def __init__(self, parent):
        super(Widgets, self).__init__(parent)
        self.extrapolated_cost = self.extrapolate_cost()
        self.sindex = 1
        self.UIComponents()
    
    '''def addTableRow(self, table, row_data):
        row = table.rowCount()
        table.setRowCount(row+1)
        col = 0
        for item in row_data:
            cell = QTableWidgetItem(str(item))
            table.setItem(row, col, cell)
            col += 1'''
        
    def UIComponents(self):    
        layout = QGridLayout()

        #Diagram Window
        global diagram
        diagram = GraphicView()
        layout.addWidget(diagram,1,5,18,18)  #Canvas for making pipeline

        #add label for buttons
        buttonlabel = QLabel("Other Components:")
        layout.addWidget(buttonlabel,0,2,1,2)

        #add buttons
        button1 = QPushButton()
        button1.setText("Input")
        layout.addWidget(button1,0,5,1,1)
        button1.clicked.connect(lambda x: diagram.addObject("I",100,50,0,0,""))

        button2 = QPushButton()
        button2.setText("Output")
        layout.addWidget(button2,0,6,1,1)
        button2.clicked.connect(lambda x: diagram.addObject("O",100,50,0,0,""))

        button3 = QPushButton()
        button3.setText("Storage")
        layout.addWidget(button3,0,7,1,1)
        button3.clicked.connect(lambda x: diagram.addObject("S",50,25,0,0,""))

        button4 = QPushButton()
        button4.setText("Model Selector")
        layout.addWidget(button4,0,8,1,1)
        button4.clicked.connect(lambda x: diagram.addObject("",20,20,0,0,""))

        button5 = QPushButton()
        button5.setText("Connector")
        layout.addWidget(button5,0,9,1,1)
        button5.clicked.connect(diagram.addArrow)

        #add button for total cost
        cost_button = QPushButton("Display Total Cost")
        cost_button.clicked.connect(self.dispTotCost)
        layout.addWidget(cost_button,0,10,1,1)

        #add button for total cost
        latency_button = QPushButton("Display Total Latency")
        latency_button.clicked.connect(self.dispTotLat)
        layout.addWidget(latency_button,0,12,1,2)

        #add table -> to show table of models in GUI (for testing purposes only)
        #global table
        #table = QTableWidget(self)
        #table.setColumnCount(len(sheet[1]))
        
        #table.rowCount()
        #table.setHorizontalHeaderLabels(cell.value for cell in sheet[1])

        #for value in sheet.iter_rows(min_row = 2, values_only = True):
        #    self.addTableRow(table, value)
        #Using Excel

        #c.execute('SELECT * FROM models') #using sql
        #for row in c:
        #   self.addTableRow(table, row)  #using sqlite3
        #layout.addWidget(table,1,0,2,4) -> to see table of models in GUI

        #add Label
        label0 = QLabel("Application Domain:")  
        layout.addWidget(label0,3,0,1,2)

        #add Checkboxes for application domains
        global domainlist
        domainlist = QListWidget()
        layout.addWidget(domainlist,4,0,1,2)
        c.execute('SELECT Domain FROM models')
        for domain in c:
            if(len(domainlist.findItems(domain[0],QtCore.Qt.MatchExactly)) == 0):
                item = QtWidgets.QListWidgetItem(domain[0])
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                domainlist.addItem(item)
        domainlist.itemClicked.connect(self.attribute_changed)

        #add Application
        addapp = QPushButton("Add Application")
        layout.addWidget(addapp,3,1,1,1)
        addapp.clicked.connect(self.addApp)

        savedappslabel = QLabel("Saved Applications:")
        layout.addWidget(savedappslabel,3,2,1,1)
        self.savedapps = QListWidget()
        layout.addWidget(self.savedapps,4,2,1,2)
        self.savedapps.itemDoubleClicked.connect(self.listwidgetdoubleclicked)

        #add Label
        label1 = QLabel("Model Name:")
        layout.addWidget(label1,5,0,1,4)

        #add Checkboxes for model names
        global modellist
        modellist = QListWidget()  #models checked in this list will show up in applicable models by name irrespective of whether they match given constraints
        layout.addWidget(modellist,6,0,1,4)  
        c.execute('SELECT Model FROM models')
        for modelName in c:
            if(len(modellist.findItems(modelName[0],QtCore.Qt.MatchExactly)) == 0):
                item = QtWidgets.QListWidgetItem(modelName[0])
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
                modellist.addItem(item)
        modellist.itemClicked.connect(self.attribute_changed)

        #add Label
        label2 = QLabel("Latency Bound:")
        layout.addWidget(label2,7,0,1,4)

        #add SpinBox for latency constraint
        global widget3
        widget3 = QSpinBox()
        widget3.setMinimum(0)
        widget3.setSingleStep(1)
        widget3.setValue(10)
        widget3.setSuffix(" ms")
        widget3.editingFinished.connect(self.attribute_changed)
        layout.addWidget(widget3,8,0,1,4)

        #add Label
        label3 = QLabel("Cost/Inference:")
        layout.addWidget(label3,9,0,1,4)

        #add SpinBox for cost constraint
        global widget4
        widget4 = QSpinBox()
        widget4.setMinimum(0)
        widget4.setMaximum(99999)
        widget4.setSingleStep(100)
        widget4.setValue(1000)
        widget4.setSuffix("$")
        widget4.editingFinished.connect(self.attribute_changed)
        layout.addWidget(widget4,10,0,1,4)

        #add Label
        label4 = QLabel("Applicable Models:")
        layout.addWidget(label4,11,0,1,1)

        #List for displaying applicable models
        global widget5
        widget5 = QListWidget()
        layout.addWidget(widget5,12,0,2,4)
        widget5.itemDoubleClicked.connect(self.listwidgetdoubleclicked)
        widget5.itemClicked.connect(self.listwidgetclicked)

        button6 = QPushButton("Add Model")
        self.allmodels = ModelList(widget5)
        layout.addWidget(button6,11,1,1,1)
        button6.clicked.connect(self.allmodels.addModel) 
        global button7
        button7 = QPushButton("Edit/Delete Model")
        button7.setCheckable(True)
        layout.addWidget(button7,11,2,1,1)
        button7.clicked.connect(self.allmodels.view)

        #add Label
        label5 = QLabel("Data Transformers:")
        layout.addWidget(label5,16,0,1,1)

        #List for displaying data transformers
        global widget7
        widget7 = QListWidget()
        layout.addWidget(widget7,17,0,1,4)
        self.tfrlist = TransformerList(widget7,diagram)
        widget7.itemDoubleClicked.connect(self.tfrlist.dispTfrDet)
        global edit_tfr_button
        edit_tfr_button = QPushButton("Edit/Delete Transformer")
        edit_tfr_button.setCheckable(True)
        layout.addWidget(edit_tfr_button,16,2,1,1)
        widget7.itemClicked.connect(self.tfrListClicked)
        add_tfr_button = QPushButton("Add Transformer")
        layout.addWidget(add_tfr_button,16,1,1,1)
        add_tfr_button.clicked.connect(self.tfrlist.addTransformer)

        #List for Server Configs
        global widget6
        widget6 = QListWidget()
        layout.addWidget(widget6,22,10,1,1)
        widget6.itemDoubleClicked.connect(self.dispConfigDet)
        widget6.addItem("Temp")
        widget6.setMaximumHeight(widget6.sizeHintForRow(0) + 5)
        widget6.takeItem(0)
    
        #add Label
        label6 = QLabel("Deployment\nResources")
        layout.addWidget(label6,20,2,3,2)
        label6.setFont(QFont("Arial",20))

        #add Radio Buttons
        radio1 = QRadioButton()
        radio1.setText("Local")
        layout.addWidget(radio1,20,5,1,1)

        radio2 = QRadioButton()
        radio2.setText("Cloud")
        layout.addWidget(radio2,21,5,1,1)
        radio2.toggled.connect(self.cloudCostSelected)

        radio3 = QRadioButton()
        radio3.setText("Hybrid")
        layout.addWidget(radio3,22,5,1,1)

        global buttoncloud
        buttoncloud = QPushButton("Calculate Cost")
        layout.addWidget(buttoncloud,20,6,2,1)
        buttoncloud.clicked.connect(self.buttonCloudClicked)
        buttoncloud.setVisible(False)

        buttonsave = QPushButton("Save Logic")
        layout.addWidget(buttonsave,20,8,1,1)
        buttonsave.clicked.connect(lambda x: self.save(self.savedapps,widget6))

        buttonload = QPushButton("Load Logic")
        layout.addWidget(buttonload,20,9,1,1)
        buttonload.clicked.connect(self.load)

        buttonconfig = QPushButton("Add New Server Config")
        layout.addWidget(buttonconfig,20,10,1,1)
        buttonconfig.clicked.connect(self.configButtonClicked)

        serverlabel = QLabel("Saved Configurations:")
        layout.addWidget(serverlabel,21,10,1,1)

        self.setLayout(layout)

    #Functions
    
    #Filtering models by constraints
    def attribute_changed(self):
        if((widget3.value() != 0) & (widget4.value() != 0)):
            #table.setRowCount(0)
            widget5.clear()
            ex_polys = self.extrapolated_cost
            for model,points in ex_polys.items():
                ex_polys[model][1] = 1
            c.execute('SELECT * FROM models')
            for row in c:
                checkmodel = modellist.findItems(row[Model],QtCore.Qt.MatchFlag.MatchExactly) #returns list of one item only
                bool1 = checkmodel[0].checkState() == 2
                bool2 = (float(row[Latency]) <= widget3.value())
                checkdomain = domainlist.findItems(row[Domain],QtCore.Qt.MatchExactly) #returns list of one item only
                bool3 = checkdomain[0].checkState() == 2
                if((bool1 or bool2) and bool3):
                    cost = float(row[Cost]) if (float(row[Cost]) <= widget4.value()) else widget4.value()
                    cores = round(ex_polys.get(row[Model])[0](cost))
                    i = ex_polys.get(row[Model])[1]
                    if(cores > 0):
                        model = UniqueModel(row[Model] + "#" + str(i), row[Model], row[Hardware], row[Hardware], cores, cores, int(row[Memory]), float(row[Latency]), float(row[Latency]), cost, cost, "Not Selected", row[Domain], row[Library], "Not Selected", 0.0, "None")
                        #self.addTableRow(table, [row[Model], row[Hardware], cores, int(row[Memory]), float(row[Latency]), cost, row[Domain], row[Library]])
                        item = QtWidgets.QListWidgetItem(model.ID)
                        widget5.addItem(item)
                        item.setData(CustomObjectRole, model)
                        ex_polys.get(row[Model])[1] = ex_polys.get(row[Model])[1] + 1
    

    #(Add object to canvas) helper functions

    def listwidgetdoubleclicked(self, item):
        try:
            model = item.data(CustomObjectRole)
        except TypeError:
            return
        attrs = copy.deepcopy(vars(model))
        attrs.pop('InitialCores')
        attrs.pop('InitialHardware')
        attrs.pop('InitialLatency')
        attrs.pop('InitialCost')
        msg = QMessageBox()
        msg.setWindowTitle("Model Details")
        msg.setText(''.join("%s: %s\n" % item for item in attrs.items()))
        x = msg.exec_()
        
    def listwidgetclicked(self, item):
        if(button7.isChecked()):
            self.allmodels.editModel(item)
        else:
            model = copy.deepcopy(item.data(CustomObjectRole))
            diagram.addObjectModel(model)

    def tfrListClicked(self,item):
        if(edit_tfr_button.isChecked()):
            self.tfrlist.editTfr(item)
        else:
            pass

    #Cost functions

    def extrapolate_cost(self): #extrapolate cost of model with reduced cost, from existing list of models having the same name
        model_polys = {} 
        c.execute('SELECT * FROM models')
        for row in c:
            point = (row[Cost],row[Cores])
            if row[Model] not in model_polys:
                model_polys[row[Model]] = [(0,0), point]
            else:
                if(point not in model_polys[row[Model]]):
                    model_polys[row[Model]].append(point)

        for model_name, model_points in model_polys.items():
            model_x = np.array(model_points)[:,0]
            model_y = np.array(model_points)[:,1]
            model_poly = Polynomial.fit(model_x, model_y, deg = len(model_points))
            model_polys[model_name] = [model_poly,1]
            
        return model_polys #return dictionary of (model name: polynomial fitted to existing data of cost vs cores)

    def buttonCloudClicked(self): #For cost of deployment to cloud
        msg = QMessageBox()
        msg.setWindowTitle("Deployment Cost (Cloud)")
        cost = diagram.calcCloudCost()
        msg.setText("Total Cost(Cloud): " + str(cost) + "$")
        x = msg.exec_()

    def cloudCostSelected(self,check):
        buttoncloud.setVisible(check)

    def dispTotCost(self):
        msg = QMessageBox()
        msg.setWindowTitle("Total Cost")
        cost = diagram.getTotalCost()
        msg.setText("Total Cost: " + str(cost) + "$")
        x = msg.exec_()

    #Latency function

    def dispTotLat(self):
        msg = QMessageBox()
        msg.setWindowTitle("Pipeline Latency")
        lat = diagram.getNetLatency()
        msg.setText("Total Latency: " + str(lat) + " ms")
        x = msg.exec_()

    #Config functions

    def configButtonClicked(self):
        self.ConfigBox = QGroupBox()
        self.configlayout = QFormLayout()
        ch = QCheckBox("GPU")
        ch.clicked.connect(self.gpuchecked)
        l1 = QLabel("CPU Cores:")
        e1 = QSpinBox()
        l2 = QLabel("Memory:")
        e2 = QSpinBox()
        global l3,e3
        l3 = QLabel("GPU Model:")
        e3 = QLineEdit()
        e3.setVisible(False)
        l3.setVisible(False)
        self.configlayout.addRow(ch)
        self.configlayout.addRow(l1,e1)
        self.configlayout.addRow(l2,e2)
        self.configlayout.addRow(l3,e3)
        ok = QPushButton("Save Config")
        cancel = QPushButton("Cancel")
        self.configlayout.addRow(ok, cancel)
        ok.clicked.connect(lambda x: self.saveConfig(e1.value(),e2.value(),e3.text()))
        cancel.clicked.connect(self.closeConfigForm)
        self.ConfigBox.setLayout(self.configlayout)
        self.ConfigBox.show()

    def saveConfig(self,cores,memory,gpumodel):
        sconfig = Config("Server Config " + str(self.sindex),cores,memory,gpumodel)
        item = QtWidgets.QListWidgetItem(sconfig.ID)
        widget6.addItem(item)
        item.setData(CustomObjectRole, sconfig)
        self.sindex = self.sindex + 1
        diagram.updateConfigList(sconfig)
        self.ConfigBox.hide()

    def closeConfigForm(self):
        self.ConfigBox.hide()

    def gpuchecked(self,bool): #shows option for gpu type only when gpu option is checked
        l3.setVisible(bool)
        e3.setVisible(bool)

    def dispConfigDet(self,item): #displays details of server configuration
        sconfig = item.data(CustomObjectRole)
        attrs = copy.deepcopy(vars(sconfig))
        if(attrs["GPUModel"] == ""):
            attrs.pop('GPUModel')
        msg = QMessageBox()
        msg.setWindowTitle("Server Config Details")
        msg.setText(''.join("%s: %s\n" % item for item in attrs.items()))
        x = msg.exec_()

    #Application functions

    def addApp(self):  #connected with Add Application button, form for adding application from user input
        num = 0
        domain = ""
        for i in range(domainlist.count()):
            if(num > 1):
                break
            if(domainlist.item(i).checkState()==2):
                domain = domainlist.item(i).text()
                num += 1
        if(num != 1):
            msg = QMessageBox()
            msg.setWindowTitle("Error Message")
            msg.setText("Select exactly one domain to create application")
            msg.exec_()
            return
        self.appbox = QGroupBox()
        layout = QFormLayout()
        appmodellist = QListWidget()
        sql = ''' SELECT * FROM models WHERE Domain=? '''
        c.execute(sql,(domain,))
        i = 1
        for row in c:
            item = QtWidgets.QListWidgetItem("   #" + str(i) + ": " + row[Model])
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            appmodellist.addItem(item)
            model = UniqueModel("#" + str(i) + ": " + row[Model], row[Model], row[Hardware], row[Hardware], row[Cores], row[Cores], int(row[Memory]), float(row[Latency]), float(row[Latency]), row[Cost], row[Cost], "Not Selected", row[Domain], row[Library], "Not Selected", 0.0, "None")
            item.setData(CustomObjectRole, model)
            i += 1
        l1= QLabel("Applicable Models")
        layout.addRow(l1)
        layout.addRow(appmodellist)
        l2 = QLabel("Application Name")
        le = QLineEdit()
        layout.addRow(l2,le)
        ok = QPushButton("Save Application")
        cancel = QPushButton("Cancel")
        layout.addRow(ok, cancel)
        ok.clicked.connect(lambda x: self.saveApp(appmodellist,le.text()))
        cancel.clicked.connect(self.closeApp)
        self.appbox.setLayout(layout)
        self.appbox.show()
    
    def saveApp(self,appmodellist,name):
        self.savedapps.addItem(name + ":")
        for i in range(appmodellist.count()):
            if(appmodellist.item(i).checkState()==2):
                item = QListWidgetItem(appmodellist.item(i).text())
                self.savedapps.addItem(item)
                item.setData(CustomObjectRole, appmodellist.item(i).data(CustomObjectRole))

        self.appbox.hide()

    def closeApp(self):
        self.appbox.hide()

    #Save/Load functions

    def save(self,applist,configlist): #save applications, configs and diagram into CSV file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(diagram,"Save Logic","","CSV File (*.csv)", options=options)
        if fileName:
            with open(fileName, mode='w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                items = diagram.scene.items()
                for item in items:
                    if(item.type() == QGraphicsLineItem().type()):
                        writer.writerow("A")
                        writer.writerow(item.start_item.getList())
                        writer.writerow(item.end_item.getList())
                    elif ((item.type() != QGraphicsTextItem().type()) & (item.type() != QGraphicsPixmapItem().type())):
                        if((item.in_arrows == []) & (item.out_arrows == [])):
                            writer.writerow(item.getList())
                
                approw = ""
                for i in range(applist.count()):
                    if(approw != "" and applist.item(i).text()[0] != " "):
                        csv_file.write("Application," + approw[:-1:] + "\n")
                        approw = applist.item(i).text() + ","
                    else:
                        approw += applist.item(i).text() + ","
                if(approw != ""):
                    csv_file.write("Application," + approw[:-1:] + "\n")
                
                for i in range(configlist.count()):
                    config = configlist.item(i).data(CustomObjectRole)
                    writer.writerow(config.getList())

    def load(self): #load saved diagram from CSV
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(diagram,"Load Logic", "","CSV File (*.csv)", options=options)
        if fileName:
            diagram.scene.clear()
            with open(fileName,'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                self.load_helper(reader,False,None)
            items = diagram.scene.items()
            for item in items:
                item.setVisible(True)
            
    def load_helper(self,reader,bool,first_item):
        try:
            curr = next(reader)
        except StopIteration:
            return
        type = curr.pop(0)
        if(type == "Model"):
            x = float(curr.pop(0))
            y = float(curr.pop(0))
            if(diagram.itemAt(x,y) is None):
                item = ModelShape(UniqueModel(curr[0],curr[1],curr[2],curr[3],int(curr[4]),int(curr[5]),int(curr[6]),float(curr[7]),float(curr[8]),float(curr[9]),float(curr[10]),curr[11],curr[12],curr[13], curr[14],float(curr[15]),curr[16]))
                item.textItem.setVisible(False) #to prevent interference with scene.itemAt function
                diagram.scene.addItem(item)
                item.setPos(x,y)
            else:
                item = diagram.itemAt(x,y)
        elif(type == "Shape"):
            x = float(curr.pop(0))
            y = float(curr.pop(0))
            if(diagram.itemAt(x,y) is None):
                item = Shape(curr[0],int(curr[1]),int(curr[2]),float(curr[3]),float(curr[4]),curr[5])
                item.textItem.setVisible(False)
                diagram.scene.addItem(item)
                item.setPos(x,y)
                item.tfrs = diagram.tfrs
            else:
                item = diagram.itemAt(x,y)
        elif(type == "A"):
            self.load_helper(reader,True,None)
        elif(type == "Config"):
            config = Config(curr[0],int(curr[1]),int(curr[2]),curr[3])
            configitem = QtWidgets.QListWidgetItem(config.ID)
            widget6.addItem(configitem)
            configitem.setData(CustomObjectRole, config)
            diagram.updateConfigList(config)
        elif(type == "Application"):
            for item in curr:
                self.savedapps.addItem(item)

        if(bool == True):
            if(first_item is None):
                self.load_helper(reader,True,item)
            else:
                diagram.scene.addItem(Arrow(first_item,item))
                self.load_helper(reader,False,None)
        else:
            self.load_helper(reader,False,None)

        self.load_helper(reader,False,None)
