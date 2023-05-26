from tkinter import *
from tkinter import messagebox, filedialog
import os.path


root = Tk()
v = StringVar()

exists = BooleanVar()
Savelocation = StringVar()
directory = "./"
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