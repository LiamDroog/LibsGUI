
import tkinter as tk

class DelayReadout:
    """
    Class-based infrastructure to display the individual
    channel delays of the stanford box.
    Important note: as this stands now, this will eat
    RAM for breakfast if you run it for a long time,
    as there are continually new labels being created.
    A smarter way to do this would have been to have
    a better thought-through update funtion in each
    class, but the rate at which it'll use up RAM is
    very low so it is not yet a priority to refactor
    # Author:   Liam Droog
    # Email:    droog@ualberta.ca
    # Year:     2021
    # Version:  V.1.0.0
    """
    def __init__(self, text, master, posX, posY):
        self.frame = tk.Frame(master=master)
        self.x = posX
        self.y = posY
        self.master = master
        self.list_of_channels = []
        # header label
        tk.Label(master=self.frame, text='Delays:', font=('Courier', 12)).grid(row=0, column=0, sticky='ew')
        for i, k in enumerate(text.rstrip().split('\n')):
            j = k.split()
            # create a channel readout for each line of input (each channel has it's own line)
            # hardcoding this isn't great but it shouldnt change
            self.list_of_channels.append(channelReadout(self.frame, j[0], j[2], j[-1], row=i+1))
        self.frame.grid(row=posX, column=posY, columnspan=20, sticky='w')

    def update(self, text):
        """
        Updates the delay readout with a given text input,
        obtained from querying the standford box

        :param text: Text to split
        :return: None
        """
        for i, k in enumerate(text.rstrip().split('\n')):
            j = k.split()
            channelReadout(self.frame, j[0], j[2], j[-1], row=i)
        self.frame.grid(row=self.x, column=self.y, columnspan=20, sticky='w')


class channelReadout:
    """
    Class for an individual channel's readout.
    """
    def __init__(self, master, channel, target, delay, row=0, col=0):
        units = ['s', 'ms', 'us', 'ns', 'ps']
        self.frame = tk.Frame(master=master)
        # create respective portions of readout to mimic stanford box layout
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
    """
    Class for each individual three digit delay section for display
    """
    def __init__(self, master, text, unit='', row=0, col=0):
        self.frame = tk.Frame(master=master)
        self.toptext = tk.Label(master=self.frame, text=text.upper(), font=('Courier', 12))
        # bottom text meme
        self.bottomtext = tk.Label(master=self.frame, text=unit)
        self.toptext.grid(row=0, column=0, sticky='sew')
        self.bottomtext.grid(row=1, column=0, sticky='new')
        self.frame.grid(row=row, column=col, sticky='ew')


class voltageReadout:
    """
    Class for displaying each channels voltage output level
    """
    def __init__(self, master, text, posX, posY):
        self.master = master
        self.x = posX
        self.y = posY
        self.frame = tk.Frame(master=master)
        self.update(text)

    def update(self, text):
        """
        Updates text frame based on input text obtained from querying the stanford box

        :param text: Text to update frame with
        :return: None
        """
        del self.frame
        self.frame = tk.Frame(master=self.master)
        text = text.split('\n')
        tk.Label(master=self.frame, text='Voltages:', font=('Courier', 12)).grid(row=0, column=0, sticky='nw')
        for i, j in enumerate(['T0', 'AB', 'CD', 'EF', 'GH']):
            tk.Label(master=self.frame, text=str(j + ':' + text[i] + ' V'),  font=('Courier', 12)).grid(row=i+1, column=0, sticky='nw')
        self.frame.grid(row=self.x, column=self.y, columnspan=3, sticky='nw')

if __name__ == '__main__':
    DelayReadout()