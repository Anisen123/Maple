'''Class which contains unique attributes for each model in diagram. Each UniqueModel is linked to a particular ModelShape.
Functions->
setCores: changes number of cores, along with corresponding change to cost and latency
setLatency: changes latency, along with corresponding change to cost and number of cores
setMemory: changes memory
'''

import math

class UniqueModel: #Attributes for each model
    ID: str
    Model: str
    Hardware: str
    Cores: int
    Memory: int
    Latency: float
    Cost: float
    Mode: str
    Domain: str
    Library: str
    CloudProvider: str
    CloudCost: int
    CloudInstance: str

    InitialCores: int
    InitialHardware : str
    InitialLatency: float
    InitialCost: float

    def __init__(self, id, model, hardware, ihardware, cores, icores, memory, latency, ilatency, cost, icost, mode, domain, library, cloudprovider, cloudcost, cloudinstance):
        self.ID = id 
        self.Model = model
        self.Hardware = hardware
        self.InitialHardware = ihardware
        self.Cores = cores
        self.InitialCores = icores
        self.Memory = memory
        self.Latency = latency
        self.InitialLatency = ilatency
        self.Cost = cost
        self.InitialCost = icost
        self.Mode = mode
        self.Domain = domain
        self.Library = library
        self.CloudProvider = cloudprovider
        self.CloudCost = cloudcost
        self.CloudInstance = cloudinstance

    def setCores(self,cores):
        self.Cores = cores
        self.Cost *= self.Cores/self.InitialCores
        self.Latency *= self.InitialCores/self.Cores

    def setLatency(self,latency):
        self.Latency = latency
        self.Cores = math.ceil(self.InitialCores * self.InitialLatency/latency)
        self.Cost = self.InitialCost*self.Cores/self.InitialCores

    def setMemory(self,memory):
        self.Memory = memory
       
        
