'''Class which calculates cost of deployment of a particular model to cloud: AWS, Azure or GCP, including serverless mode for each.
Functions->
calcAwsEC2Cost, calcAwsSvrlessCost, calcGCPECCost, calcGCPSvrlessCost, calcAzureFsCost, calcAzureSvrlessCost: self-explanatory. calculates cost of cloud deployment as specified.
calcAllCosts: returns list containing all costs by calling all previous functions
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

class CloudCost():
    def __init__(self):
        options = Options()
        options.headless = True
        DRIVER_PATH = '/Users/ssen/Downloads/chromedriver' #chromedriver location
        self.driver = webdriver.Chrome(options = options, executable_path=DRIVER_PATH)
        self.driver.implicitly_wait(10) #wait for html elements to load
        self.driver.get('https://calculator.aws/#/createCalculator/EC2')
        self.cores = self.driver.find_element_by_xpath('//*[@id="awsui-input-10"]') #input box for cores
        self.memory = self.driver.find_element_by_xpath('//*[@id="awsui-input-11"]') #input box for memory
        

def calcAwsEC2Cost(self,cores,memory): #Pricing in US East(Ohio), Linux
    self.cores.clear()
    self.memory.clear()
    self.cores.send_keys(cores)
    self.memory.send_keys(memory)
    cores_got = self.driver.find_element_by_xpath('//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/div[2]/div/div/div[1]/div[2]/div/div[1]/span[1]/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/span/div/div/div[3]/div[3]/div/div[2]/div[2]/div[2]')
    memory_got = self.driver.find_element_by_xpath('//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/div[2]/div/div/div[1]/div[2]/div/div[1]/span[1]/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/span/div/div/div[3]/div[3]/div/div[3]/div[2]/div[2]')  #Output displayed on calculator
    hourlycost = self.driver.find_element_by_xpath('//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/div[2]/div/div/div[1]/div[2]/div/div[1]/span[1]/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/span/div/div/div[3]/div[3]/div/div[2]/div[2]/div[1]')
    instance_type = self.driver.find_element_by_xpath('//*[@id="e-c2next"]/div/div[2]/awsui-form/div/div[2]/span/span/div[2]/div/div/div[1]/div[2]/div/div[1]/span[1]/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/span/div/div/div[3]/div[3]/div/div[1]/div/h3')
    instance_type = instance_type.text
    hourlycost = float(hourlycost.text)
    cores_got = int(cores_got.text)
    memory_got = float(re.findall(r"[-+]?\d*\.\d+|\d+", memory_got.text)[0])
    return [hourlycost,instance_type]

def calcAwsSvrlessCost(self,memory,latency,requests):
    compute_charge = requests*3600*latency/1000*memory*0.00001667
    request_charge = requests*3600/1000000*0.2
    total_charge = compute_charge + request_charge
    return total_charge

def calcGCPC2Cost(self,cores,memory): #Pricing in Iowa(us-central1), Linux
    n = cores
    text = "Custom Instance"
    if((memory == n*4) and (n==4) or (n==8) or (n==8) or (n==16) or (n==30) or (n==60)):
        text = "c2-standard-" + str(n)
    return [0.03398*cores + 0.00455*memory,text]  #data as of 21 June, 2021

def calcGCPSvrlessCost(self,memory,latency,requests,speed):
    compute_charge_memory =  memory * latency/1000 * requests * 3600 * 0.0000025
    compute_charge_speed = speed/1000 * latency/1000 * requests * 3600 * 0.00001
    request_charge = requests * 3600 * 0.0000004
    total_charge = compute_charge_memory + compute_charge_speed + request_charge
    return total_charge

def calcAzureFsCost(self,cores,memory): #Pricing in Central US, CentOS or Ubuntu Linux
    availcores = [2,48,16,32,48,64,72]
    reqcores = 0 # number of cores required
    for i in availcores:
        if(cores <= i):
            reqcores = i
    hourlycost = reqcores * 0.051   #data as of 1 July, 2021
    instance = "F" + str(reqcores) + "s v2"
    if(reqcores == 0):
        hourlycost = 0.0
        instance = "Not Available"
    return [hourlycost,instance] #Assuming RAM provided is <= 2*vCPU's
        
        
def calcAzureSvrlessCost(self,memory,latency,requests):
    compute_charge = requests*3600*latency/1000*memory*0.00001667
    request_charge = requests*3600/1000000*0.2
    total_charge = compute_charge + request_charge
    return total_charge

def calcAllCosts(self,cores,memory,latency,requests,speed):
    return [[calcAwsEC2Cost(self,cores,memory),calcAwsSvrlessCost(self,memory,latency,requests)],[calcAzureFsCost(self,cores,memory),calcAzureSvrlessCost(self,memory,latency,requests)],[calcGCPC2Cost(self,cores,memory),calcGCPSvrlessCost(self,memory,latency,requests,speed)]]



