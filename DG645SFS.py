import instruments as ik
from DelayReadoutClass import DelayReadout
class DG645:
    def __init__(self, comstring):
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
        self.unit.sendcmd(command)

    def query(self, command):
        return self.unit.query(command)

    def get_all_delays(self):
        for i in range(10):
            rtn = self.query('DLAY?' + str(i))
            rtn = rtn.split(',')
            print(self.optlist[i] + ' = ' + self.optlist[int(rtn[0])] + str(rtn[1]))

    def return_all_voltages(self):
        rtn = ''
        for i in range(5):
            rtn += str(self.query('LAMP?' + str(i))).rstrip() + '\n'
        return rtn

    def return_all_delays(self):
        string = ''
        for i in range(10):
            rtn = self.query('DLAY?' + str(i))
            rtn = rtn.split(',')
            string += self.optlist[i] + ' = ' + self.optlist[int(rtn[0])] + ' + ' + str(rtn[1][1:]) + '\n'
        return string

    def close(self):
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
