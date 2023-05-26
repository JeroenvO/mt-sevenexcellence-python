import re
import serial
from tkinter import *
import serial.tools.list_ports
from matplotlib.pylab import *
import matplotlib.animation as animation
import datetime

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Seven Excellence" in p[1]:
        comport = p[0]



#enter name
    #check if name exist
        #moet unique zijn

try:
    ser = serial.Serial(
        port=comport,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=100)
    print("connected to: " + ser.portstr)
except:
    print('unsuccesfull connection!')

result = []
temp = []
date = []
unit = []


# Setup figure and subplots
f0 = figure(num = 0, figsize = (13, 9))#, dpi = 100)
f0.suptitle('Measurements', fontsize=12)


def updateData(self):
    print('print time '+str(datetime.datetime.now()))

def readline(self):
    global result
    s = ser.readline().decode('utf-8')
    #result = re.search('<resultValue>(.*)</resultValue>', s) #raw string
    if len(result) >= 2:
        result = []
    result.append(re.search('<resultValue>(.*)</resultValue>', s).group(1))
    temp = re.search('<rawTemperature>(.*)</rawTemperature>', s).group(1)
    date = re.search('<timeStamp>(.*)</timeStamp>', s).group(1)
    unit = re.search('<resultUnit>(.*)</resultUnit>', s).group(1)
    if len(result) == 2:
        result.append(temp)
        result.append(date)
        print(result)
        return result

#while True:
#   readline()

simulation = animation.FuncAnimation(f0, readline, blit=False, interval=500)
plt.show()