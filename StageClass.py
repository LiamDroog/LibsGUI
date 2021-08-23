import tkinter as tk
from tkinter import messagebox
import tkinter.font as font
import serial
import time
import numpy as np
import os
# import h5py
# from beta_QueueClass import Queue
import multiprocessing as mp


class LIBS_2AxisStage:
    """
    Class file for controlling the libs 2 axis stage
    Author:   Liam Droog
    Email:    droog@ualberta.ca
    Year:     2021
    Version:  V.1.0.0
    """
    def __init__(self, port, baud, startupfile, owd):
        self.owd = owd
        os.chdir(self.owd)
        self.s = None
        self.window = tk.Toplevel()
        self.window.title('Stage Control')
        self.pos = [0., 0.]
        self.currentpos = 'X0 Y0'
        self.rate = 1
        self.grid = [5, 9]
        self.rowLen = 5
        self.colLen = 9
        self.port = port
        self.baud = baud
        self.startupfile = startupfile
        self.connected = False
        self.queue = None
        self.tempFile = None
        self.temprunning = False
        self.filename = None
        self.buttonx = 12
        self.buttony = 6
        self.feedrate = 0
        self.shotnum = 0
        self.datafile = None
        self.datafilename = None
        self.parameters = {
            'Data Format': ['grbl reference #', 'value'],
            'stepPulseLength': [0, None],
            'stepIdleDelay': [1, None],
            'axisDirection': [3, None],
            'statusReport': [10, None],
            'feedbackUnits': [13, None],
            'xSteps/mm': [100, None],
            'ySteps/mm': [101, None],
            'xMaxRate': [110, None],
            'yMaxRate': [111, None],
            'xMaxAcc': [120, None],
            'yMaxAcc': [121, None],
        }
        # self.param_number = 2  ###########

        # draws all on-screen controls and assigns their event commands
        self.rowarr = list(i for i in range(self.grid[0]))
        self.colarr = list(i for i in range(self.grid[1]))

        self.window.rowconfigure(self.rowarr, minsize=50, weight=1)
        self.window.columnconfigure(self.colLen, minsize=50, weight=1)

        # On screen control grid
        self.btn_w = tk.Button(master=self.window, text="\u219F", command=lambda: self.jogY(self.rate))
        self.btn_w['font'] = font.Font(size=18)
        self.btn_w.grid(row=1, column=2, sticky="nsew")

        self.btn_a = tk.Button(master=self.window, text="\u219E", command=lambda: self.jogX(-1 * self.rate))
        self.btn_a['font'] = font.Font(size=18)
        self.btn_a.grid(row=2, column=1, sticky="nsew")

        self.btn_s = tk.Button(master=self.window, text="\u21A1", command=lambda: self.jogY(-1 * self.rate))
        self.btn_s['font'] = font.Font(size=18)
        self.btn_s.grid(row=2, column=2, sticky="nsew")

        self.btn_d = tk.Button(master=self.window, text="\u21A0", command=lambda: self.jogX(self.rate))
        self.btn_d['font'] = font.Font(size=18)
        self.btn_d.grid(row=2, column=3, sticky="nsew")

        # # serial connect button
        # self.connect_btn = tk.Button(master=self.window, text='connect', fg='red',
        #                              command=lambda: self.initSerial(self.port, self.baud, self.startupfile))
        # self.connect_btn.grid(row=1, column=5, sticky='nsew')

        # serial connect button
        self.connect_btn = tk.Button(master=self.window)
        self.connect_btn.grid(row=1, column=5, sticky='nsew')

        # 10 button
        self.btn_10 = tk.Button(master=self.window, text='10', command=lambda: self.switchRate(10))
        self.btn_10.grid(row=3, column=1, sticky='nsew')
        self.btn_10.configure(width=self.buttonx, height=self.buttony)
        # 1 button
        self.btn_1 = tk.Button(master=self.window, text='1', command=lambda: self.switchRate(1))
        self.btn_1.grid(row=3, column=2, sticky='nsew')
        self.btn_1.configure(width=self.buttonx, height=self.buttony)

        # 0.1 button
        self.btn_01 = tk.Button(master=self.window, text='0.5', command=lambda: self.switchRate(0.5))
        self.btn_01.grid(row=3, column=3, sticky='nsew')
        self.btn_01.configure(width=self.buttonx, height=self.buttony)
        # 0.01 button
        self.btn_001 = tk.Button(master=self.window, text='0.1', command=lambda: self.switchRate(0.1))
        self.btn_001.grid(row=3, column=4, sticky='nsew')
        self.btn_001.configure(width=self.buttonx, height=self.buttony)

        self.btn_0001 = tk.Button(master=self.window, text='0.05', command=lambda: self.switchRate(0.05))
        self.btn_0001.grid(row=3, column=5, sticky='nsew')
        self.btn_0001.configure(width=self.buttonx, height=self.buttony)

        # DRO frame
        self.lbl_frame = tk.Frame(master=self.window, relief=tk.RAISED, borderwidth=3)
        self.lbl_pos = tk.Label(master=self.lbl_frame, text='X: %1.3f, Y:%1.3f, Feedrate: %d, Units: mm'
                                                            % (self.pos[0], self.pos[1], self.feedrate))
        self.lbl_pos['font'] = font.Font(size=18)

        self.lbl_frame.grid(row=0, column=0, columnspan=self.colLen + 1, sticky='ew')
        self.lbl_pos.pack()

        # gcode input box
        self.gcode_entry = tk.Entry(master=self.window)
        self.gcode_entry.configure(width=40)
        self.gcode_entry.grid(row=4, column=6, sticky='wn')

        # gcode button
        self.gcode_send = tk.Button(master=self.window, text='Send',
                                    command=lambda: self.sendCommand(self.gcode_entry.get().rstrip() + '\n',
                                                                     resetarg=True,
                                                                     entry=self.gcode_entry))
        self.gcode_send.grid(row=4, column=9, sticky='ewn')
        self.gcode_send.configure(width=5)

        # file input box
        self.file_entry = tk.Entry(master=self.window)
        self.file_entry.grid(row=4, columnspan=3, sticky='new')

        # file input button
        self.file_input = tk.Button(master=self.window, text='Get File',
                                    command=lambda: self.getFile(self.file_entry.get()))
        self.file_input.grid(row=4, column=3, sticky='ew')
        self.file_input.configure(width=self.buttonx, height=self.buttony)

        # file run button
        self.file_run = tk.Button(master=self.window, text='Run', command=self.runFile)
        # self.file_run = tk.Button(master=self.window, text='Run')
        self.file_run.grid(row=4, column=4, sticky='ew')
        self.file_run.configure(width=self.buttonx)

        self.kill_btn = tk.Button(master=self.window, text='Kill', command=self.killSwitch)
        self.kill_btn.grid(row=2, column=5, sticky='nsew')
        self.kill_btn.configure(width=self.buttonx)

        self.increment_btn = tk.Button(master=self.window, text='Relative moves', command=self.setG91)
        self.increment_btn.grid(row=1, column=1, sticky='nsew')
        self.increment_btn.configure(width=self.buttonx, height=self.buttony)

        self.absolute_btn = tk.Button(master=self.window, text='Absolute moves', command=self.setG90)
        self.absolute_btn.grid(row=1, column=3, sticky='nsew')
        self.absolute_btn.configure(width=self.buttonx, height=self.buttony)

        # go home button
        self.home_btn = tk.Button(master=self.window, text='Go\nHome',
                                  command=lambda: self.sendCommand('G90 X0 Y0 F' + str(self.parameters['xMaxRate'][1])))
        self.home_btn.grid(row=2, column=4, sticky='nsew')
        self.home_btn.configure(width=self.buttonx, height=self.buttony)

        # set home button
        self.set_home = tk.Button(master=self.window, text='Set\nHome', command=lambda: self.sendCommand('G92 X0 Y0'))
        self.set_home.grid(row=1, column=4, sticky='nsew')
        self.set_home.configure(width=self.buttonx, height=self.buttony)

        self.help_button = tk.Button(master=self.window, text='Help', command=self.help)
        self.help_button.grid(row=2, column=5, sticky='nesw')
        self.help_button.configure(width=self.buttonx, height=self.buttony)

        self.output = tk.Listbox(master=self.window)
        self.output.grid(columnspan=4, rowspan=self.grid[1] - 6, row=1, column=6, sticky='nsew')
        self.output.configure(bg='white')
        self.window.bind('<Return>', (lambda x: self.sendCommand(self.gcode_entry.get(), entry=self.gcode_entry,
                                                                 resetarg=True)))
        #GRID ME


        # self.__setTempFile()
        self.setKeybinds()
        self.Refresh()
        self.window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.initSerial(self.port, self.baud, self.startupfile)
        self.window.geometry('800x400+%d+%d' % (self.window.winfo_screenwidth() / 4,
                                                self.window.winfo_screenheight() / 5))

        self.window.bind('<Up>', self.moveup)
        self.window.bind('<Down>', self.movedown)
        self.window.bind('<Left>', self.moveleft)
        self.window.bind('<Right>', self.moveright)


    def start(self):
        """
        Starts stage gui by parsing last known position

        :return: None
        """
        self.__getLastPos()
        self.window.mainloop()

    def __on_closing(self):
        """
        Runs on closing to ensure proper cleanup

        :return: None
        """
        if messagebox.askokcancel("Quit", "Quit?"):
            os.chdir(self.owd)
            self.__setLastPos()
            self.connected = False
            self.s.close()
            self.s = None
            self.queue = None
            print('Connection closed')
            self.window.destroy()

    def setKeybinds(self):
        """
        binds keypress event to the onKeyPress function

        :return: None
        """
        self.window.bind('<KeyPress>', self.onKeyPress)

    def Refresh(self):
        """
        Sets recurring event to update GUI every 50ms

        :return: None
        """
        self.lbl_pos.configure(text='X: %1.3f, Y:%1.3f, Feedrate: %d' % (self.pos[0], self.pos[1], self.feedrate))
        self.window.after(5, self.Refresh)


    def isOpen(self):
        """
        Used to detect if connection is open or nah

        :return: True if software is connected to grbl box and false if else
        """
        if self.s:
            return self.s.is_open
        else:
            return False

    def onKeyPress(self, event):
        """
        Allows for stage control via WASD - Not sure if keeping implementation

        :param event: onKeyPress event
        :return: None
        """
        if event.char.lower() == '<up>':
            self.jogY(self.rate)
        elif event.char.lower() == '<left>':
            self.jogX(-1 * self.rate)
        elif event.char.lower() == '<down>':
            self.jogY(-1 * self.rate)
        elif event.char.lower() == '<right>':
            self.jogX(self.rate)

    def moveup(self, event):
        """
        Moves the stage up.

        :param event: Event
        :return: None
        """
        self.jogY(self.rate)

    def movedown(self, event):
        """
        Moves the stage down.

        :param event: Event
        :return: None
        """
        self.jogY((-1*self.rate))

    def moveleft(self, event):
        """
        Moves the stage left.

        :param event: Event
        :return: None
        """
        self.jogX(-1*self.rate)

    def moveright(self, event):
        """
        Moves the stage right.

        :param event: Event
        :return: None
        """
        self.jogX(self.rate)

    def jogX(self, v):
        """
        Jogs the X stage by the specified rate within the GUI

        :param v: float rate
        :return: None
        """
        if not self.temprunning:
            c = 'G91 x' + str(v) + '\n'
            self.sendCommand(c)
            self.setG90()


    def jogY(self, v):
        """
        Jogs the Y stage by the specified rate within the GUI

        :param v: float rate
        :return: None
        """
        if not self.temprunning:
            c = 'G91 y' + str(v) + '\n'
            self.sendCommand(c)
            self.setG90()

    def switchRate(self, v):
        """
        Switches current jog rate to specified input

        :param v: float jog rate
        :return:
        """
        # used to switch the rate's order of magnitude corresponding to pressed button
        self.rate = v

    def readOut(self):
        """
        Reads out the reply from GRBL

        :return: None
        """
        # implement own method?
        out = self.s.readline()  # Wait for grbl response with carriage return
        # print('> ' + out.strip().decode('UTF-8'))
        # self.output['text'] += '\n>' + out.decode('UTF-8').strip()
        self.output.insert('end', '\n' + '> ' + out.decode('UTF-8').rstrip())
        self.output.yview(tk.END)

    def sendCommand(self, gcode, resetarg=False, entry=None):
        """
        Sends command to GRBL. Checks if it is a comment, then sends command and updates DRO position accordingly

        :param gcode: command to be sent
        :param resetarg: used to detect if a command was sent via the input box so it knows to clear it
        :param entry: entry box instance to clear
        :return: None
        """
        # check if it's a comment
        if self.s:
            if gcode.strip() == '' or gcode.strip()[0] == ';':
                return
            t = gcode.rstrip().lower().split(' ')
            # check if it's a manual entry to clear entry box
            if resetarg and entry is not None:
                entry.delete(0, 'end')

            if 'g90' in t:
                self.setG90(cmd=False)
            if 'g91' in t:
                self.setG91(cmd=False)
            for i in t:
                if i.lower().strip()[0] == 'f':
                    self.__setFeed(int(i.strip()[1:]))

            self.output.insert('end', '\n' + '~> ' + gcode.rstrip())
            self.output.yview(tk.END)

            gcode = gcode.rstrip() + '\n'
            self.s.write(gcode.encode('UTF-8'))
            self.readOut()
            # self.__writeData([time.time_ns(), gcode.rstrip()])
            self.setPos(gcode)

    def initSerial(self, port, baud, filename):
        """
        Initalizes serial connection with grbl doohickey. Parses all startup commands from a text file input

        :param port: USB port board is plugged into
        :param baud: communication baud rate
        :param filename: startup filename containing startup grbl code
        :return: None
        """
        if not self.connected:
            try:
                self.s = serial.Serial(port, baud)
            except Exception as e:
                self.stop()
                raise (e)
            else:
                # Wake up grbl
                self.s.write(b"\r\n\r\n")
                # allow grbl to initialize
                time.sleep(2)
                # flush startup from serial
                self.s.flushInput()
                # open startup file
                with open(filename, 'r') as f:
                    for line in f:
                        # strip EOL chars
                        l = line.strip()
                        self.sendCommand(l + '\r')
                print('Connected to GRBL')
                # self.connect_btn.configure(fg='green', text='Connected')
                self.connected = True
                self.__parseParameters()

        else:
            self.connected = False
            self.s.close()
            self.s = None
            self.queue = None
            print('Connection closed')
            self.connect_btn.configure(fg='red', text='Connect')

    def setG91(self, cmd=True):
        """
        Sets relative movements active

        :param cmd: If true, send the G91 command, regardless, switch button text color to match
        :return: None
        """
        if self.s:
            if cmd:
                self.sendCommand('G91')
            self.increment_btn.configure(fg='green')
            self.absolute_btn.configure(fg='black')

    def setG90(self, cmd=True):
        """
        Sets absolute movements active

        :param cmd: If true, send the G90 command, regardless, switch button text color to match
        :return: None
        """
        if self.s:
            if cmd:
                self.sendCommand('G90')
            self.increment_btn.configure(fg='black')
            self.absolute_btn.configure(fg='green')

    def getPos(self):
        """
        returns position of stage

        :return: position of stage
        """
        return self.pos

    def setPos(self, cmd):
        """
        sets position of table on DRO

        :param cmd: gcode command containing new location
        :return: None
        """
        # g91 iterates, not sets
        if cmd[:3].lower() == 'g91':
            for i in cmd.split(' '):
                if i.lower()[0] == 'x':
                    self.pos[0] += float(i[1:])
                if i.lower()[0] == 'y':
                    self.pos[1] += float(i[1:])
        else:
            for i in cmd.split(' '):
                if i.lower()[0] == 'x':
                    self.pos[0] = float(i[1:])
                if i.lower()[0] == 'y':
                    self.pos[1] = float(i[1:])

    def sendOutput(self, text):
        """
        Sends output into output view

        :param text: Text to input
        :return: None
        """
        self.output.insert('end', text)
        self.output.yview(tk.END)

    def __parsePosition(self, ipos):
        """
        Parses position for use with DRO

        :param ipos: input position
        :return: [x, y] list of current position
        """
        pos = [0, 0]
        for i in ipos.split(' '):
            if i.lower()[0] == 'x':
                pos[0] = float(i[1:])
            if i.lower()[0] == 'y':
                pos[1] = float(i[1:])
        return pos

    def __parseParameters(self):
        """
        Parses parameters from a given input file into the parameters dictionary for usage

        :return: None
        """
        tmp = []
        with open(self.startupfile, 'r') as f:
            for line in f:
                if line != '' and line[0] == '$':
                    tmp.append(line.strip().strip('$'))
        f.close()
        for i in tmp:
            for key, value in self.parameters.items():
                if i.split('=')[0] == str(value[0]):
                    self.parameters[key] = [i.split('=')[0], i.split('=')[1]]

        self.feedrate = int(self.parameters['xMaxRate'][1])

    def getStageParameters(self):
        """
        Returns stage parameters

        :return: Stage parameters, string
        """
        return self.parameters

    def __setFeed(self, feedrate):
        """
        Sets feedrate based on input

        :param feedrate: New feedrate in mm/min
        :return: None
        """
        self.feedrate = feedrate

    def help(self):
        """
        HELP! Spawns a new window with the help file

        :return: Stuff that might help.
        """
        cwd = os.getcwd()
        p = mp.Process(target=os.system, args=(os.path.join(cwd, 'README.txt'),))
        p.start()
        # os.system(os.path.join(cwd, 'Config/Help.txt'))

    def __setLastPos(self):
        """
        Saves last known position

        :return: None
        """
        np.save('Config/Config.npy', self.pos)

    def __getLastPos(self):
        """
        Obtains the last known position on startup

        :return: None
        """
        try:
            self.pos = np.load('Config/Config.npy')
        except:
            print('Could not load last known position')


    def __blinkButton(self, button, c1, c2, delay):
        """
        Blinks a button between two colors, c1 and c2. Has logic for specific buttons to cease switching given a
        specific string as the text.

        :param button: target button instance
        :param c1: First color to switch to, string
        :param c2: Second color to switch to, string
        :param delay: Delay in ms
        :return: None
        """
        if button['text'] == 'Start?':
            return
        else:
            if button['fg'] == c1:
                button.configure(fg=c2)
            else:
                button.configure(fg=c1)
            self.window.after(delay, lambda: self.__blinkButton(button, c1, c2, delay))

    def calcDelay(self, currentpos, nextpos):
        """
        Calculates a lower end of the required delay between moved for the queue command system

        :param currentpos: Current position
        :param nextpos: Next position
        :return: time delay in ms
        """

        ipos = self.__parsePosition(currentpos)
        fpos = self.__parsePosition(nextpos)
        assert len(ipos) == len(fpos), 'Input arrays must be same length'

        v = float(self.parameters['xMaxRate'][1]) / 60
        a = float(self.parameters['xMaxRate'][1])  # becomes very choppy changing to xMaxAcc... idk wtf

        delta = list(ipos[i] - fpos[i] for i in range(len(ipos)))
        d = np.sqrt(sum(i ** 2 for i in delta))
        deltaT = ((2 * v) / a) + ((d - (v ** 2 / a)) / v)
        print('next move in ' + str(int(np.floor(deltaT * 1000))) + 'ms')
        return int(np.floor(deltaT * 1000))  # in ms

    def killSwitch(self):
        """
        effectively kills current gcode run by clearing queue. Note this isn't instantaneous

        :return: None
        """
        if self.s:
            self.queue.clear()
            self.temprunning = False
            self.output.insert('end', '\n' + '!> ' + 'Current motion killed')
            self.output.yview(tk.END)


    def getFile(self, filename):
        """
        Opens file containing gcode. Does not parse for correctness.
        Inputs all non blank lines / comments into a queue for usage

        :param filename: File to open
        :return: None
        """
        # queue with timing calculation for next move
        # wipe queue
        self.queue = None
        try:
            self.filename = filename
            f = open(filename, 'r')
            self.queue = Queue()
            for line in f:
                if line != '' and line[0] != ';':
                    self.queue.enqueue(line)
            self.output.insert('end', '\n' + '> ' + ' Loaded ' + filename)
            self.output.yview(tk.END)
        except FileNotFoundError:
            self.file_entry.delete(0, 'end')
            self.output.insert('end', '\n' + '!> ' + ' File does not exist')
            self.output.yview(tk.END)

    def __startFromDeath(self):
        """
        Starts from an unexpected power loss. Retreives last known position from temp file.
        Issues: Target stage *could* be manually moved on us prior to reviving. User initiative to ensure
        nothing moves.

        :return: None
        """
        if self.s:
            self.queue = None
            currentline = self.__retrieveTempData()
            try:
                f = open(self.filename, 'r')
                self.queue = Queue()
                positionFound = False
                for line in f:
                    if line == currentline:
                        positionFound = True
                    if positionFound:
                        if line != '' and line[0] != ';':
                            self.queue.enqueue(line)
                print('Loaded ' + self.filename)
                self.start_from_death_btn.configure(text='Start?', fg='green', command=self.runFile)
            except:
                return
            # except FileNotFoundError:
                # self.file_entry.delete(0, 'end')
                # self.file_entry.insert(0, 'File does not exist')
        else:
            self.start_from_death_btn.configure(text='Not\nconnected')
            self.window.after(5000, lambda: self.start_from_death_btn.configure(text='Load\nData?'))

    def __removeTempFile(self):
        """
        removes temp file at end of program run

        :return: None
        """
        os.remove(self.tempFile)
        self.tempFile = None

    def __saveTempData(self):
        """
        Saves temp data to temp file, if program is currently running it calls itself every 1000ms

        :return: None
        """
        if self.temprunning:
            if self.queue.size() > 0:
                np.save(self.tempFile, [self.queue.peek(), time.asctime(), self.filename, self.shotnum])
                self.window.after(1000, self.__saveTempData)
                return True
        else:
            return False

    def __retrieveTempData(self):
        """
        Retrieves temp data from temp.npy if it exists and user calls it. Needs to be updated
        to reflect final changes in temp data stored once integrated into laser system

        :return: Last line that runfile stored before unexpected power loss
        """
        self.tempFile = 'temp.npy'
        currentline, t, self.filename, self.shotnum = np.load(self.tempFile)
        print(currentline, t, self.filename)
        return currentline

    def __setTempFile(self):
        """
        Sets the temporary file name, unless it exists

        :return: None
        """
        pass
        # if os.path.exists('temp.npy') or self.tempFile is not None:
        #     self.start_from_death_btn.configure(text='Load\nData?', fg='red')
        #     self.__blinkButton(self.start_from_death_btn, 'red', 'blue', 1000)
        # else:
        #     self.tempFile = 'temp.npy'

    def finishRun(self):
        """
        Runs after file completion, removes contingency file since it is not needed.

        :return: None
        """
        print('File run complete')
        self.__removeTempFile()

    def runFile(self):
        """
        Used to run a file obained with getFile()

        :return: None
        """
        if self.s:
            if not self.temprunning:
                self.temprunning = True
                self.__saveTempData()

            nextpos = self.queue.dequeue()
            self.sendCommand(nextpos)

            if self.queue.size() > 0:
                self.window.after(self.calcDelay(self.currentpos, nextpos), self.runFile)
                self.currentpos = nextpos

            elif self.queue.size() == 0:
                self.window.after(self.calcDelay(self.currentpos, nextpos), self.finishRun)

            else:
                self.temprunning = False
                return

if __name__ == '__main__':
    LIBS_2AxisStage()
