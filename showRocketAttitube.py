from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file
from datetime import datetime
import time
import simplepbr
import serial

read_state = False
num = 0
now_y = 0.0
now_p = 0.0
now_r = 0.0
UorD = True

COM_PORT = 'COM5'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)
time.sleep(2)
print("序列阜連線成功")

seconds = time.time()
NowTime = time.localtime(seconds)
name = "attd"+"%d"%NowTime.tm_mon+"-%d"%NowTime.tm_mday+"_%d"%NowTime.tm_hour+"-%d"%NowTime.tm_min+"-%d"%NowTime.tm_sec+".txt"
data = open(name, "wt")
data = open(name, "at")

load_prc_file("config/conf.prc")

def correction_spr(y,p,r):
    global UorD
    final_y = y
    final_p = p
    final_r = r
    if p < 90 and p > -90:
        UorD = True
    else:
        UorD = False 
    
    return [final_y, final_p, final_r]

class rocket3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        simplepbr.init()

        self.disableMouse()
        self.rocket = self.loader.loadModel("model/Rocket8.gltf")
        self.rocket.setPos(0,8,0)
        self.rocket.reparentTo(self.render)
        self.rocketD = self.loader.loadModel("model/Rocket8down.gltf")
        self.rocketD.setPos(0,8,0)
        self.rocketD.reparentTo(self.render)
        self.rocketD.hide()
        self.updateTask = self.taskMgr.add(self.looper, "looper")

    def looper(self,task):
        global read_state,now_y,now_p,now_r,num
        time_s = (datetime.now().strftime('%M:%S.%f')[:-3])
        data_raw = ser.readline()
        print(data_raw)
        data_final = data_raw.decode()
        if data_final == "python start\r\n":
            read_state = True     
        if read_state == True:
            num += 1
            print(time_s+"  "+data_final[0:24],file = data)
        
        if data_final[0] != " " and num >= 3:
            first_y = float(data_final[0:7])
            first_p = float(data_final[8:15])
            first_r = float(data_final[16:23])
            spr = correction_spr(first_y,first_p,first_r)
            print(spr,end=" ")
            print(self.rocket.getHpr())
            if UorD == True:
                self.rocket.show()
                self.rocketD.hide()
                self.rocket.setH(first_y)
                self.rocket.setP(first_p)
                self.rocket.setR(first_r)
            elif UorD == False:
                Th = 0 - self.rocket.getHpr()[0]
                self.rocket.setH(first_y-180)
                self.rocket.setP(first_p-180)
                self.rocket.setR(first_r*-1)
            
        return task.cont

app = rocket3D()
app.run()