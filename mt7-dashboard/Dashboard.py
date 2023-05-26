from matplotlib.pylab import *
import matplotlib.animation as animation
from datetime import datetime, timedelta
import serial.tools.list_ports
from tkinter import *
from tkinter import messagebox, filedialog
import os.path



ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Seven Excellence" in p[1]:
        comport = p[0]


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
timelist=[]

root = Tk()
v = StringVar()

exists = BooleanVar()
Savelocation = StringVar()
directory = "./" #default location
root.title('Ph/ORP data acquisition menu')
Label(root, text = "Enter name of safe file").grid(row = 0, sticky = W)
Label(root, text = "x-axis width in minutes").grid(row = 1, sticky = W)
Label(root, textvariable=v, text="Not Unique").grid(row = 2, sticky = W)
Label(root, text = "Location:").grid(row = 3, sticky = W)
Label(root, textvariable=Savelocation).grid(row = 3, sticky = W, column=1)
Savelocation.set(directory)
v2=StringVar(root, value='PhORP')
Fname = Entry(root, textvariable=v2)
Fname.grid(row=0, column=1)
v3=StringVar(root, value='5')
Xaxis = Entry(root, textvariable=v3)
Xaxis.grid(row=1, column=1)



def StartMeasuring():
    global filename
    global plottime
    filename = Fname.get()

    if not filename:
        messagebox.showinfo("Error", "Filename is empty")
        return
    checkuniquename()
    if exists.get():
        messagebox.showinfo("Error", "File already exists or directory is not correct")
        return
    try:
        plottime = int(Xaxis.get())
    except:
        messagebox.showinfo("Error", "Xaxis time is not an integer number (default is 5min)")
        return
    root.destroy()

def checkuniquename():

    if os.path.isfile(directory+'/'+Fname.get()+'.txt'):
        v.set('File already exist')
        exists.set(True)
    else:
        v.set('File doesnt exist yet')
        exists.set(False)


def changelocation():
    global directory
    directory = filedialog.askdirectory()
    Savelocation.set(directory)
    print('changing directory to: '+directory)
    checkuniquename()

Button(root, text="Check File Name", command=checkuniquename).grid(row=5, sticky=W,column=0)
Button(root, text="Change Save Location", command=changelocation).grid(row=5, sticky=W,column=1)
Button(root, text="Start!", command=StartMeasuring).grid(row=5, sticky=W, column=2)
mainloop()

print(filename)
print(directory)

plottimeseconds=60*plottime

#constants:
secondspermeasurement = 5 #amount of seconds per measurement point


#create some empty data arrays and values
PH = []
ORP = []
time = []
temperature = []

# Sent for figure
font = {'size'   : 9}
matplotlib.rc('font', **font)


# Setup figure and subplots
f0 = figure(num = 0, figsize = (14, 19))#, dpi = 100)

f0.suptitle('Measurements', fontsize=12)
ax01 = subplot2grid((2, 1), (0, 0))
ax02 = subplot2grid((2, 1), (1, 0))
ax11=ax01.twinx()
ax22=ax02.twinx()
#par1=ax01.twinx()

#tight_layout()

# Set titles of subplots
ax01.set_title('PH/Orp vs time')
ax02.set_title('Temperature vs time')

# set y-limits
ax01.set_ylim(0,50)
ax02.set_ylim(0,50)

# sex x-limits
#ax01.set_xlim(0,100.0*secondspermeasurement)
#ax02.set_xlim(0,10.0*secondspermeasurement)

# Turn on grids
ax01.grid(True)
ax02.grid(True)


# set label names
ax01.set_xlabel("time(seconds)")
ax01.set_ylabel("Ph", color='r')
ax11.set_ylabel("ORP (mV)", color='b')
ax02.set_xlabel("time(seconds)")
ax02.set_ylabel("Temperature (°C)", color='g')
#ax22.set_ylabel("PPM my setup", color='y')

# set plots
p011, = ax01.plot(time,PH,'r-', label="Ph")
p012, = ax11.plot(time,ORP,'b-', label="ORP")
p021, = ax02.plot(time,temperature,'g-', label="Temperature")



def plotdata():
    print('help')


def readline(self):
    global result
    global unit
    global temporp
    global tempph
    global orpbuffer
    s = ser.readline().decode('utf-8')
    #print(s)
    pause(0.05)
    if len(result) >= 2:
        result = []
        unit = []
    result.append(re.search('<resultValue>(.*)</resultValue>', s).group(1))
    temp = re.search('<rawTemperature>(.*)</rawTemperature>', s).group(1)
    date = re.search('<timeStamp>(.*)</timeStamp>', s).group(1)
    #print(date)
    unit.append(re.search('<resultUnit>(.*)</resultUnit>', s).group(1))
    if len(result) == 2: #receive to separate lines over serial (one with ph and the other with orp)
        result.append(temp)
        result.append(date)
        savedata = open(directory+'/'+filename+'.txt', "a+")
        if int(unit[0]) == 11:
            temporp=result[0]
            tempph=result[1]
        else:
            temporp = result[1]
            tempph = result[0]
        if float(temporp) < 14: #orp is interpetreted as ph so last known value is used(buffer)
            temporp = orpbuffer
            print('some serial reading went wrong')
        else:
            orpbuffer =temporp
        print(tempph + '\t' + temporp + '\t' + result[2] + '\t'+result[3])
        savedata.write(tempph + '\t' + temporp + '\t' + result[2] + '\t'+result[3]+'\n')  # save data file
        savedata.close()
        dateformat = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timelist.append(dateformat)
        PH.append(float(tempph))
        ORP.append(float(temporp))
        temperature.append(float(temp))
        #print((timelist[-1]-timelist[0]).total_seconds())

        if int(((timelist[-1]-timelist[0]).total_seconds())) >= plottimeseconds: # calculate the seconds of the xlim
            timelist.pop(0)
            PH.pop(0)
            ORP.pop(0)
            temperature.pop(0)
        if len(timelist) >= 2:
            ax01.axes.set_ylim(min(PH)-0.1*mean(PH), max(PH)+0.1*mean(PH))
            try:
                ax11.axes.set_ylim(min(ORP)-0.1*mean(ORP), max(ORP)+0.1*mean(ORP))
            except:
                ax11.axes.set_ylim(0, 2)
                print('error in orp value!')
            ax02.axes.set_ylim(min(temperature)-0.1*mean(temperature), max(temperature)+0.1*mean(temperature))
            p011.axes.set_xlim(timelist[-1]-timedelta(seconds=plottimeseconds), timelist[-1])
            p021.axes.set_xlim(timelist[-1]-timedelta(seconds=plottimeseconds), timelist[-1])
            p011.set_data(timelist, PH)
            p012.set_data(timelist, ORP)
            p021.set_data(timelist, temperature)
        #print(str(PH)+str(ORP)+str(temperature))
        return p011, p012, p021


pause(3)
while True:
    try:
        print('Starting Plotting')
        simulation = animation.FuncAnimation(f0, readline, blit=False, interval=100)
        plt.show()
    except:
        print('rerun the script')
        plt.close()
