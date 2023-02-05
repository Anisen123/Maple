class Config: #Data stored for server configuration
    ID: str
    Cores: int
    Memory: int
    GPUModel: str

    def __init__(self, id, cores, memory, gpumodel):
        self.ID = id 
        self.Cores = cores
        self.Memory = memory
        self.GPUModel = gpumodel
        
    def getList(self): #returns list used for saving a config
        return ["Config",self.ID,self.Cores,self.Memory,self.GPUModel]
