'''Class which contains canvas (self.scene) for inserting nodes and creating pipeline.
Functions->
addObjectModel: assigns model to self.shape
addObject: assigns non-model objects to self.shape
mouseDoubleClickEvent: inserts object in self.shape to diagram at position of double-click
addArrow: inserts arrow from first object selected to second object
getTotalCost: returns total cost of models in diagram
keyPressEvent: deletes selected object from diagram
calcCloudCost: returns total cost of deploying models in diagram to cloud 
updateConfigList: updates list of configurations in each model
updateTfrList: updates list of transformers in each non-model object
removeTfrFromList: removes transformer from list
getNetLatency: returns latency of pipeline
'''


from PyQt5 import QtCore
from UniqueModel import UniqueModel
from CloudCost import *
from Arrow import Arrow
from Shape import Shape
from ModelShape import ModelShape
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QPointF, Qt
CustomObjectRole = QtCore.Qt.UserRole + 1

class GraphicView(QGraphicsView):  #Canvas for inserting nodes and creating pipeline
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)       
        self.setSceneRect(0, 0, 1200, 1000)
        self.shape = None
        self.prevShape = None
        self.connectorActive = False
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.configs = []
        self.tfrs = []

    def addObjectModel(self,model):
        self.shape = ModelShape(model)

    def addObject(self,text:str,a,b,cost,latency,type1):
        self.shape = Shape(text,a,b,cost,latency,type1)

    def mouseDoubleClickEvent(self, event): #add object in self.shape to location clicked, if location is empty
        position = self.mapToScene(event.pos()) 
        if(self.shape is not None):
            if(self.itemAt(position.x(),position.y()) is None):
                if(self.prevShape is None or self.prevShape != self.shape): 
                    self.scene.addItem(self.shape)
                    self.shape.setPos(QPointF(position.x(), position.y()))
                    if(self.shape.type() == QGraphicsRectItem().type()):
                        self.shape.configs = self.configs
                    elif(self.shape.type() == QGraphicsEllipseItem().type()):
                        self.shape.tfrs = self.tfrs
                    self.prevShape = self.shape
                    
                    
    def addArrow(self): #add arrow from first object clicked to second object clicked, connected to 'Connector' button
        items = self.scene.selectedItems()
        if(len(items) == 2):
            if(items[0].selectedTime < items[1].selectedTime):
                start_item = items[0]
                end_item = items[1]
            else:
                start_item = items[1]
                end_item = items[0]
            if((items[0].type() == QGraphicsRectItem().type()) & (items[1].type() == QGraphicsRectItem().type())):
                selector = Shape("",20,20,0,0,"")
                self.scene.addItem(selector)
                selector.tfrs = self.tfrs
                arrow1 = Arrow(start_item,selector)
                arrow2 = Arrow(selector,end_item)
                selector.setPos((start_item.scenePos()+end_item.scenePos())/2)
                self.scene.addItem(arrow1)
                self.scene.addItem(arrow2)
            else:
                arrow = Arrow(start_item,end_item)
                self.scene.addItem(arrow)

            items[0].setSelected(False)
            items[1].setSelected(False)


    def getTotalCost(self):
        items = self.scene.items()
        totalcost = 0
        for item in items:
            if(item.type() == QGraphicsRectItem().type() or item.type() == QGraphicsEllipseItem().type()):
                totalcost += item.Cost
        return totalcost

    def keyPressEvent(self, event): #for deleting object from scene. Error: object gets removed but not deallocated
        if event.key() == Qt.Key_Backspace:
            items = self.scene.selectedItems()
            for item in items:
                self.scene.removeItem(item)
                if(item.type() != QGraphicsLineItem().type()):
                    for arrow in item.in_arrows:
                        self.scene.removeItem(arrow)
                    for arrow in item.out_arrows:
                        self.scene.removeItem(arrow)

    def calcCloudCost(self): #cost for cloud for all item in scene
        totalsum = 0
        items = self.scene.items()
        for item in items:
            if(item.type() == QGraphicsRectItem().type()):
                    totalsum += item.model.CloudCost
        return totalsum

    def updateConfigList(self,config):
        self.configs.append(config)
        for item in self.scene.items():
            if(item.type() == QGraphicsRectItem().type()):
                item.configs = self.configs

    def updateTfrList(self,tfr):
        self.tfrs.append(tfr)
        for item in self.scene.items():
            if(item.type() == QGraphicsEllipseItem().type()):
                item.tfrs = self.tfrs
    
    def removeTfrFromList(self,tfr):
        self.tfrs.remove(tfr)
        for item in self.scene.items():
            if(item.type() == QGraphicsEllipseItem().type()):
                item.tfrs = self.tfrs

    def getNetLatency(self):
        def longestPath(graph):
            ans = 0
            n = len(graph)
            table = [-1] * n

            def dfs(u):
                if table[u] != -1:
                    return table[u]
                p_len = 0
                for v in graph[u]:
                    p_len = max(p_len, v[1] + dfs(v[0]))
                table[u] = p_len
                return p_len

            for i in range(n):
                ans = max(ans, dfs(i))    #graph[u] contains arrays of outgoing nodes; graph is an adjacency list
            return ans

        source = Shape("",10,10,0,0,"") #virtual node connected to all sources
        nodelist = [source]
        items = self.scene.items()
        for item in items:
            if((item.type() == QGraphicsRectItem().type()) | (item.type() == QGraphicsEllipseItem().type())):
                nodelist.append(item)
                if((item.in_arrows == []) and (item is not source)):
                    Arrow(source,item)

        graph = [[(nodelist.index(arrow.end_item),arrow.end_item.Latency) if arrow.end_item.type() == QGraphicsRectItem().type() or arrow.end_item.type() == QGraphicsEllipseItem().type() else (nodelist.index(arrow.end_item),0) for arrow in node.out_arrows] for node in nodelist]
        for arrow in source.out_arrows:
            arrow.end_item.in_arrows = []
        source.out_arrows = []
        return longestPath(graph)

        