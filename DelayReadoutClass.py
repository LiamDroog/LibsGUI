import tkinter as tk

# class DelayReadout:
#     def __init__(self, text):
#         # self.window = tk.Tk(className='DelayReadout')   # toplevel for integration
#         self.window = tk.Toplevel()
#         self.window.title('Delay Readout')
#         for i, k in enumerate(text.rstrip().split('\n')):
#             j = k.split()
#             channelReadout(self.window, j[0], j[2], j[-1], row=i)
#         self.window.mainloop()
#
#     def update(self, text):
#         for i, k in enumerate(text.rstrip().split('\n')):
#             j = k.split()
#             channelReadout(self.window, j[0], j[2], j[-1], row=i)

class DelayReadout:
    def __init__(self, text, master, posX, posY):
        # self.window = tk.Tk(className='DelayReadout')   # toplevel for integration
        self.frame = tk.Frame(master=master)
        self.x = posX
        self.y = posY
        self.master = master
        tk.Label(master=self.frame, text='Delays:', font=('Courier', 12)).grid(row=0, column=0, sticky='ew')
        for i, k in enumerate(text.rstrip().split('\n')):
            j = k.split()
            channelReadout(self.frame, j[0], j[2], j[-1], row=i+1)
        self.frame.grid(row=posX, column=posY, columnspan=20, sticky='w')

    def update(self, text):
        for i, k in enumerate(text.rstrip().split('\n')):
            j = k.split()
            channelReadout(self.frame, j[0], j[2], j[-1], row=i)
        self.frame.grid(row=self.x, column=self.y, columnspan=20, sticky='w')


class channelReadout:
    def __init__(self, master, channel, target, delay, row=0, col=0):
        units = ['s', 'ms', 'us', 'ns', 'ps']
        self.frame = tk.Frame(master=master)
        threeDigitSection(self.frame, channel, row=0, col=0)
        threeDigitSection(self.frame, ' = ', row=0, col=1)
        threeDigitSection(self.frame, target, row=0, col=2)
        threeDigitSection(self.frame, ' + ', row=0, col=3)
        delay = delay.split('.')
        threeDigitSection(self.frame, delay[0] + '.', unit=units[0], row=0, col=4)
        for i, k in enumerate([delay[1][j:j+3] for j in range(0, len(delay[1]), 3)]):
            threeDigitSection(self.frame, k, unit=units[1+i], row=0, col=5+i)

        self.frame.grid(row=row, column=col, sticky='e')


class threeDigitSection:
    def __init__(self, master, text, unit='', row=0, col=0):
        self.frame = tk.Frame(master=master)
        self.toptext = tk.Label(master=self.frame, text=text.upper(), font=('Courier', 12))
        self.bottomtext = tk.Label(master=self.frame, text=unit)
        self.toptext.grid(row=0, column=0, sticky='sew')
        self.bottomtext.grid(row=1, column=0, sticky='new')
        self.frame.grid(row=row, column=col, sticky='ew')


class voltageReadout:
    def __init__(self, master, text, posX, posY):
        self.master = master
        self.x = posX
        self.y = posY
        self.frame = tk.Frame(master=master)
        self.update(text)

    def update(self, text):
        del self.frame
        self.frame = tk.Frame(master=self.master)
        text = text.split('\n')
        tk.Label(master=self.frame, text='Voltages:', font=('Courier', 12)).grid(row=0, column=0, sticky='nw')
        for i, j in enumerate(['T0', 'AB', 'CD', 'EF', 'GH']):
            tk.Label(master=self.frame, text=str(j + ':' + text[i] + ' V'),  font=('Courier', 12)).grid(row=i+1, column=0, sticky='nw')
        self.frame.grid(row=self.x, column=self.y, columnspan=3, sticky='nw')

if __name__ == '__main__':
    DelayReadout()