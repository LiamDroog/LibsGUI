import tkinter as tk
from StageClass import LIBS_2AxisStage
import serial.tools.list_ports
import os


class StageLauncher:
    def __init__(self, master, owd):
        # Stuff for launching stage
        # self.window = tk.Tk(className='Launcher')
        os.chdir(owd)
        self.window = tk.Toplevel(master=master)
        self.window.title('Stage Control Launcher')
        self.stage = None
        # configure grid for widget layout
        self.grid = [5, 2]
        self.rowarr = list(i for i in range(self.grid[0]))
        self.colarr = list(i for i in range(self.grid[1]))
        self.window.rowconfigure(self.rowarr, minsize=0, weight=1)
        self.window.columnconfigure(self.colarr, minsize=0, weight=1)

        self.screenwidth = int(self.window.winfo_screenwidth() * 0.1)
        self.screenheight = int(self.window.winfo_screenheight() * 0.15)
        self.window.geometry(
            '%dx%d+%d+%d' % (self.screenwidth, self.screenheight, self.window.winfo_screenwidth() / 3,
                             self.window.winfo_screenheight() / 5))

        self.stagelabel = tk.Label(master=self.window, text='Stage Control Launcher')
        self.stagelabel.grid(row=0, column=0, columnspan=2, sticky='ew')
        # stage gui launch btn
        self.start_stage_btn = tk.Button(master=self.window, text='Launch Stage Control',
                                         command=self.__startStage)
        self.start_stage_btn.grid(row=4, column=0, columnspan=2, sticky='nsew')

        # Com port
        comlist = [comport.device for comport in serial.tools.list_ports.comports() if 'USB-SERIAL CH340' in comport.description]
        self.comval = tk.StringVar(self.window)
        self.comval.set('Select Com Port')
        self.comlabel = tk.Label(master=self.window, text='COM Port:')
        self.comlabel.grid(row=1, column=0, sticky='news')
        self.com = tk.OptionMenu(self.window, self.comval, *comlist)
        self.com.grid(row=1, column=1, sticky='ew')

        # baud
        baudlist = [9600, 115200]
        self.baudval = tk.IntVar(self.window)
        self.baudval.set('115200')
        self.baudlabel = tk.Label(master=self.window, text='Baud Rate: ')
        self.baudlabel.grid(row=2, column=0, sticky='ew')
        self.baud = tk.OptionMenu(self.window, self.baudval, *baudlist)
        self.baud.grid(row=2, column=1, sticky='ew')

        # startup file
        self.filelabel = tk.Label(master=self.window, text='Startup File: ')
        self.filelabel.grid(row=3, column=0, sticky='ew')
        self.startfile = tk.Entry(master=self.window)
        self.startfile.insert(0, 'Config/startup.txt')
        self.startfile.grid(row=3, column=1, sticky='ew')

        self.window.protocol("WM_DELETE_WINDOW", self.__onclosing)
        self.window.mainloop()

    def __onclosing(self):
        self.window.destroy()

    def __startStage(self):
        try:
            self.stage = LIBS_2AxisStage(self.comval.get(), self.baudval.get(), self.startfile.get()).start()
        except Exception as e:
            self.stagelabel.config(text='Could not start stage', fg='Red')
            print(e)
            self.window.after(5000, lambda : self.stagelabel.config(text='Stage Control Launcher', fg='Black'))

if __name__ == '__main__':
    StageLauncher()
