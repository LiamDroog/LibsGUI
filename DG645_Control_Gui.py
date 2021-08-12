"""
##################################################
Provides graphical interface to use the stanford
research system DG645 digital delay generator.
##################################################
# Author:   Liam Droog
# Email:    droog@ualberta.ca
# Year:     2021
# Version:  V.1.0.0
##################################################
"""
import tkinter as tk
from DG645SFS import DG645
from DelayReadoutClass import (DelayReadout, voltageReadout)
class ControlGui_645:
    def __init__(self, master):
        self.optlist = ['0', 't', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # self.window = tk.Tk(className='\DG645 Control')
        self.window = tk.Toplevel(master=master)
        self.window.title('DG645 Control Panel')
        self.screenwidth = int(self.window.winfo_screenwidth() * 0.55)
        self.screenheight = int(self.window.winfo_screenheight() * 0.55)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=25, weight=1)
        self.window.columnconfigure(self.colarr, minsize=25, weight=1)

        # self.comport = 'serial://COM3'

        self.connectionFrame = tk.Frame(master=self.window)
        tk.Label(master=self.connectionFrame, text='Connections:').grid(row=0, column=0, columnspan=4, sticky='nsew')
        self.connectbutton = tk.Button(master=self.connectionFrame, text='Connect', command=self._connectToBox)
        self.connectbutton.grid(row=1, column=0, rowspan=2, columnspan=2, sticky='nsew')
        self.resetBoxButton = tk.Button(master=self.connectionFrame, text='Reset', command=self._resetBox, width=8, height=2)
        self.resetBoxButton.grid(row=1, column=2, rowspan=2, columnspan=2, sticky='nsew')
        self.comportEntry = tk.Entry(master=self.connectionFrame, width=15)
        self.comportEntry.insert(0, 'serial://COM7')
        self.comportEntry.grid(row=3, column=1, columnspan=2, sticky='e')
        tk.Label(master=self.connectionFrame, text='Com Port:').grid(row=3, column=0)
        self.connectionFrame.grid(row=0, column=0, rowspan=2, columnspan=3, sticky='w')


        self.triggerFrame = tk.Frame(master=self.window)
        tk.Label(master=self.triggerFrame, text='Triggering Mode:').grid(row=0, column=0, columnspan=6, sticky='ew')
        self.internalTriggerbtn = tk.Button(master=self.triggerFrame, text='Internal Trigger', width=12, height=2,
                                            command=lambda: self.sendCommand('TSRC 5'))
        self.internalTriggerbtn.grid(row=1, column=0, rowspan=2, columnspan=2, sticky='nsew')

        self.externalTriggerbtn = tk.Button(master=self.triggerFrame, text='External Trigger', width=12, height=2,
                                            command=lambda: self.sendCommand('TSRC 1'))
        self.externalTriggerbtn.grid(row=1, column=2, rowspan=2, columnspan=2, sticky='nsew')

        self.triggerFrame.grid(row=0, column=3, rowspan=1, columnspan=4, sticky='w')

        # Don't think this is necessary
        # self.reprateentryLabel = tk.Label(master=self.window, text='Rep-Rate-O-Meter')
        # self.reprateentryLabel.grid(row=self.grid[1] - 4, column=0, columnspan=7, sticky='new')
        # self.reprateentrybar = tk.Entry(master=self.window)
        # self.reprateentrybar.configure(width=40)
        # self.reprateentrybar.grid(row=self.grid[1]-3, column=0, columnspan=7, sticky='new')
        # self.repratesendentrybtn = tk.Button(master=self.window, text='Send',
        #                               command=lambda: self.sendCommand('TRAT ' + str(self.reprateentrybar.get())))
        # self.repratesendentrybtn.grid(row=self.grid[1]-3, column=7, sticky='ew')

        self.commandFrame = tk.Frame(master=self.window)
        self.entryLabel = tk.Label(master=self.commandFrame, text='Command-O-Matic')
        self.entryLabel.grid(row=self.grid[1]-1, column=0, columnspan=7, sticky='new')
        self.entrybar = tk.Entry(master=self.commandFrame)
        self.entrybar.configure(width=40)
        self.entrybar.grid(row=self.grid[1], column=0, columnspan=7, sticky='w')

        self.sendentrybtn = tk.Button(master=self.commandFrame, text='Send',
                                      command=lambda: self.sendCommand(self.entrybar.get()))
        self.sendentrybtn.grid(row=self.grid[1], column=7, sticky='w')

        self.queryentrybtn = tk.Button(master=self.commandFrame, text='Query',
                                       command=lambda: self._sendQuery(self.entrybar.get(), ins=True))
        self.queryentrybtn.grid(row=self.grid[1], column=8, sticky='w')
        self.commandFrame.grid(row=4, column=0, columnspan=6, sticky='w')

        self.firingFrame = tk.Frame(master=self.window)
        tk.Label(master=self.firingFrame, text='Firing:').grid(row=0, column=0, columnspan=2, sticky='ew')
        self.triggerbtn = tk.Button(master=self.firingFrame, text='Fire!', width=10, height=3, command=self._trigger)
        self.triggerbtn.grid(row=1, column=0, sticky='nsew')

        self.repbutton = tk.Button(master=self.firingFrame, text='Fire at x hz', width=10, height=3, command=lambda: self._trigger(rep=True))
        self.repbutton.grid(row=1, column=1, sticky='nsew')

        self.firingFrame.grid(row=3, column=8, rowspan=2, columnspan=2, sticky='w')

        # Don't think this is necessary either

        # self.viewheader = tk.Label(master=self.window, text='Change View')
        # self.viewheader.grid(row=0, column=11, columnspan=3, sticky='new')

        # self.reprateview = tk.Button(master=self.window, text='Rate', command=lambda: self.sendCommand('DISP 0,0'))
        # self.reprateview.grid(row=1, column=11, sticky='nsew')
        # self.zero_view = tk.Button(master=self.window, text='t0', command=lambda: self.sendCommand('DISP 11,0'))
        # self.zero_view.grid(row=1, column=12, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='t1', command=lambda: self.sendCommand('DISP 11,1'))
        # self.t_view.grid(row=1, column=13, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='A', command=lambda: self.sendCommand('DISP 11,2'))
        # self.t_view.grid(row=2, column=11, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='B', command=lambda: self.sendCommand('DISP 11,3'))
        # self.t_view.grid(row=2, column=12, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='C', command=lambda: self.sendCommand('DISP 11,4'))
        # self.t_view.grid(row=2, column=13, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='D', command=lambda: self.sendCommand('DISP 11,5'))
        # self.t_view.grid(row=3, column=11, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='E', command=lambda: self.sendCommand('DISP 11,6'))
        # self.t_view.grid(row=3, column=12, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='F', command=lambda: self.sendCommand('DISP 11,7'))
        # self.t_view.grid(row=3, column=13, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='G', command=lambda: self.sendCommand('DISP 11,8'))
        # self.t_view.grid(row=4, column=11, sticky='nsew')
        # self.t_view = tk.Button(master=self.window, text='H', command=lambda: self.sendCommand('DISP 11,9'))
        # self.t_view.grid(row=4, column=12, sticky='nsew')

        self.delayFrame = tk.Frame(master=self.window)
        self.delayLabel = tk.Label(master=self.delayFrame, text='Set Channel Delay')
        self.delayLabel.grid(row=0, column=0, columnspan=7, sticky='ew')
        self.delayEntry = tk.Entry(master=self.delayFrame)
        self.delayEntry.configure(width=12)
        self.delayEntry.grid(row=1, column=4, columnspan=1)

        self.chosenDelayTarget = tk.StringVar(master=self.delayFrame)
        self.chosenDelayTarget.set(self.optlist[0])
        self.delayTarget = tk.OptionMenu(self.delayFrame, self.chosenDelayTarget, *self.optlist)
        self.delayTarget.grid(row=1, column=0, sticky='nsew')

        self.chosenDelayTargetLink = tk.StringVar(master=self.delayFrame)
        self.chosenDelayTargetLink.set(self.optlist[0])
        self.delayTargetLink = tk.OptionMenu(self.delayFrame, self.chosenDelayTargetLink, *self.optlist)
        self.delayTargetLink.grid(row=1, column=2, sticky='nsew')

        self.delayplus = tk.Label(master=self.delayFrame, text=' = ')
        self.delayplus.grid(row=1, column=1)
        self.delayequal = tk.Label(master=self.delayFrame, text=' + ')
        self.delayequal.grid(row=1, column=3)
        self.unitdict = {
            's'     :   'e0',
            'ms'    :   'e-3',
            'us'    :   'e-6',
            'ns'    :   'e-9',
            'ps'    :   'e-12'
        }
        self.unitList = list(i for i in self.unitdict.keys())
        self.chosenDelayUnit = tk.StringVar(master=self.delayFrame)
        self.chosenDelayUnit.set(self.unitList[0])

        self.timeTarget = tk.OptionMenu(self.delayFrame, self.chosenDelayUnit, *self.unitList)
        self.timeTarget.grid(row=1, column=5, sticky='nsew')

        self.setDelayButton = tk.Button(master=self.delayFrame, text='Set', command=self.setDelay)
        self.setDelayButton.grid(row=1, column=6, sticky='nsew')

        self.delayFrame.grid(row=3, column=0, columnspan=7, sticky='w')
        self.window.protocol("WM_DELETE_WINDOW", self._onClosing)


        self.window.mainloop()

    def _connectToBox(self):
        self.DG645 = DG645(self.comportEntry.get())
        self.readout = DelayReadout(self.DG645.return_all_delays(), self.window, posX=6, posY=0)
        self.voltagereadout = voltageReadout(self.window, self.DG645.return_all_voltages(), posX=6, posY=6)
        self.reprate = float(self._sendQuery('TRAT?'))
        self.connectbutton.config(bg='green')

    def _trigger(self, rep=False):
        if not rep:
            if not self._sendQuery('TSRC?') == '5':
                self.sendCommand('TSRC 5')
            self.sendCommand('*TRG')
        else:
            if not self._sendQuery('TSRC?') == '0':
                self.sendCommand('TSRC 0')
            self.repbutton.config(text='Stop?', command=self._stopTrigger)

    def _stopTrigger(self):
        self.sendCommand('TSRC 5')
        self.repbutton.config(text='RepRate', command=lambda: self._trigger(rep=True))

    def _resetBox(self):
        self.DG645.close()
        del self.DG645
        self._connectToBox()

    def _onClosing(self):
        try:
            self.DG645.close()
            self.window.destroy()
        except AttributeError as e:
            self.window.destroy()

    def _sendQuery(self, command, ins=False):
        self.entrybar.delete(0, 'end')
        rtn = self.DG645.query(command)
        if ins:
            self.entrybar.insert(0, rtn)
            return
        return rtn

    def sendCommand(self, command):
        self.entrybar.delete(0, 'end')
        self.DG645.sendcmd(command)
        self.readout.update(self.DG645.return_all_delays())
        self.voltagereadout.update(self.DG645.return_all_voltages())

    def setDelay(self):
        target = self.chosenDelayTarget.get()
        link = self.chosenDelayTargetLink.get()
        unit = self.chosenDelayUnit.get()
        delay = self.delayEntry.get()
        try:
            float(delay)
        except:
            print('Invalid input, ya doofus')
            return
        string = 'DLAY '
        string += str(self.optlist.index(target)) + ','
        string += str(self.optlist.index(link)) + ','
        string += str(delay) + str(self.unitdict[unit])
        print(string)
        self.sendCommand(string)


if __name__ == '__main__':
    ControlGui_645()
