import instruments as ik
from DelayReadoutClass import DelayReadout
class DG645:
    """
    CLass providing methods to interface with a DG645 delay pulse generator.
    """
    def __init__(self, comstring):
        """
        :param comstring: String of com port that it's connected to via RS232 to USB adapter
        """
        try:
            self.unit = ik.srs.SRSDG645.open_from_uri(comstring)
        except:
            self.unit = None
            raise IOError('Unable to connect to DG645 - Check your com port and ensure it was closed properly before'
                          ' connecting again')
        else:
            print('Connection was successful.')
            print(self.unit.query('*IDN?'))

        self.optlist = ['0', 't', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def sendcmd(self, command):
        """
        Sends command to box

        :param command: string of command to send to box
        :return: None
        """
        self.unit.sendcmd(command)

    def query(self, command):
        """
        Queries property of stanford box

        :param command: Command to query
        :return: None
        """
        return self.unit.query(command)

    def get_all_delays(self):
        """
        Gets and prints all delays for all channels. Deprecated - use return_all_delays() instead

        :return: None
        """
        for i in range(10):
            rtn = self.query('DLAY?' + str(i))
            rtn = rtn.split(',')
            print(self.optlist[i] + ' = ' + self.optlist[int(rtn[0])] + str(rtn[1]))

    def return_all_voltages(self):
        """
        Returns all channel voltage output levels

        :return: string of each channels output voltage delimited by a newline character
        """
        rtn = ''
        for i in range(5):
            rtn += str(self.query('LAMP?' + str(i))).rstrip() + '\n'
        return rtn

    def return_all_delays(self):
        """
        Returns all channel delay times

        :return: string of each channels delay times delimited by a newline character
        """
        string = ''
        for i in range(10):
            rtn = self.query('DLAY?' + str(i))
            rtn = rtn.split(',')
            string += self.optlist[i] + ' = ' + self.optlist[int(rtn[0])] + ' + ' + str(rtn[1][1:]) + '\n'
        return string

    def close(self):
        """
        Closes connection to dg645 properly

        :return: None
        """
        self.unit.sendcmd('IFRS 0')
        print('Connection closed successfully')

    # def displayDelayReadout(self):
    #     DelayReadout(self.return_all_delays())

if __name__ == '__main__':

    dg = DG645('serial://COM3')
    try:
        print(dg.return_all_voltages())
    except Exception as e:
        print(e)
    finally:
        dg.close()
