import threading
import serial
import time
import distutils.util
import math
from numpy import interp
import statistics
import config

class Arduino(threading.Thread):
    """docstring for Arduino"""
    daemon = True
    previously_sent = None
    actioations_per_second = 15
    time_between_ems = 30

    def __init__(self):
        super(Arduino, self).__init__()
        self.channels = {
            'ems1': {
                'min_max': [20, 100],
                'type': 'digipot',
                'prefix': 1000,
                'last_value': 0,
                'ems_on_off': False,
                'name': 'A1',
                'color': 'green',
                'serial_open': 'a',
                'serial_close': 'b'
            },
            'ems2': {
                'min_max': [20, 100],
                'type': 'digipot',
                'prefix': 2000,
                'last_value': 0,
                'ems_on_off': False,
                'name': 'B1',
                'color': 'red',
                'serial_open': 'f',
                'serial_close': 'g'
            },
            'ems3': {
                'min_max': [20, 100],
                'type': 'digipot',
                'prefix': 3000,
                'last_value': 0,
                'ems_on_off': False,
                'name': 'A2',
                'color': 'blue',
                'serial_open': 'c',
                'serial_close': 'e'
            },
            'ems4': {
                'min_max': [20, 100],
                'type': 'digipot',
                'prefix': 4000,
                'last_value': 0,
                'ems_on_off': False,
                'name': 'B2',
                'color': 'blue',
                'serial_open': 'h',
                'serial_close': 'i'
            }
        }
        # 'ems3': {
        #               'min_max': [20, 100],
        #               'type': 'digipot',
        #               'prefix': 3000,
        #               'last_value': 0,
        #               'ems_on_off': False,
        #               'name': 'EMS3',
        #               'color': 'violet',
        #               'serial_open': 'b',
        #               'serial_close': 'n'
        #           },
                  #'ems3': {'min_max': [20, 100], 'type': 'digipot', 'prefix': 3000, 'last_value': 0, 'ems_on_off': False, 'name': 'EMS3', 'color': 'orange'}
                  #'relay1': {'type': 'relay', 'state': False, 'serial_open': 'o', 'serial_close': 'c'}

        self.subscribers = []
        self.stop = True
        self.last_sent_ems = 0
        self.list_with_ems_strength = {}
        self.stop_gesture = False
        self.study_no_ems = False
        self.arduino_value_callback = None

        try:
            self.ser = serial.Serial(port=config.EMS_SERIAL, baudrate=19200, timeout=0.05, writeTimeout=0)
            self.no_serial = False
        except:
            self.no_serial = True


        try:
            self.ser_capacitive = serial.Serial(port=config.CAPACITIVE_SERIAL, baudrate=19200, timeout=0, writeTimeout=0)
            self.no_serial_cap = False
        except:
            self.no_serial_cap = True
            print("failed getting cap arduino...")

    def stop_all(self):
        self.send_value("s")

    def open_all_channels(self):
        for channel in self.channels.keys():
           self.change_relay_state(channel, True)

    def close_all_channels(self):
        for channel in self.channels.keys():
           self.change_relay_state(channel, False)

    def perform_gesture(self, gesture, duration, ignore_channels=False):
        #self.stop_gesture = False
        sampled_gestures = []
        for ges, val in gesture.items():
            new_value = val[::int(math.ceil(len(val)/self.actioations_per_second/(duration/1000)))]
            sampled_gestures.append([new_value, ges])
        samples = dict()

        channels = {}

        for index, sampled_gesture in enumerate(sampled_gestures):
            for idx, cord in enumerate(sampled_gesture[0]):
                if not idx in samples:
                    samples[idx] = []
                channels[sampled_gesture[1]] = True
                samples[idx].append([int(interp(cord, [0, 100], self.channels[sampled_gesture[1]]['min_max'])), sampled_gesture[1]])
                samples[idx].append([int(cord), sampled_gesture[1]])



        for channel in channels:
            self.change_relay_state(channel, True)

        for index, val in samples.items():
            final_list = {}
            for thing in val:
                final_list[thing[1]] = thing[0]
            if not self.stop_gesture:
                self.send_ems_strength(final_list)
                time.sleep(1/self.actioations_per_second)
            else:
                break
        if not ignore_channels:
            stop_ems = {}
            for channel in self.channels.keys():
                stop_ems[channel] = 0
            self.send_ems_strength(stop_ems, True)
            for channel in channels:
                self.change_relay_state(channel, False)

            self.stop_all()


    def change_relay_state(self, channel, state):
        if state:
            self.send_value(self.channels[channel]['serial_open'])
        else:
            self.send_value(self.channels[channel]['serial_close'])
        self.channels[channel]['state'] = state


    def calibration(self, message):
        if message[1] == "reset":
            self.send_value("r")
        if message[1] == "ems_min_max":
            if message[2] in self.channels:
                self.channels[message[2]]['min_max'] = [int(message[3]), int(message[4])]
        if message[1] == "ems_on_off":
            self.change_relay_state(message[2], distutils.util.strtobool(message[3]))
        if message[1] == "ems_value":
            if message[3] and message[3].isdigit() and int(message[3]) >= 0 and int(message[3]) <= 100:
                self.send_ems_strength({message[2]: int(message[3])})
            else:
                raise ValueError
        if message[1] == "relay":
            self.change_relay_state(message[2], distutils.util.strtobool(message[3]))


    def send_ems_strength(self, values, force=False):

        final_list = []
        too_short = False
        if time.time() - self.last_sent_ems < self.time_between_ems/1000 and force is not True:
            too_short = True
        for channel, val in sorted(values.items()):
            if channel in self.channels:
                new_val = int(val)
                if new_val < self.channels[channel]['min_max'][0] and new_val < self.channels[channel]['min_max'][1]:
                    new_val = self.channels[channel]['min_max'][0]
                if new_val > self.channels[channel]['min_max'][1] and new_val > self.channels[channel]['min_max'][0]:
                    new_val = self.channels[channel]['min_max'][1]
                if not channel in self.list_with_ems_strength:
                    self.list_with_ems_strength[channel] = []
                self.list_with_ems_strength[channel].append(int(new_val))
                if not too_short:
                    final_list.append(str(self.channels[channel]['prefix'] + round(100 - statistics.mean(self.list_with_ems_strength[channel]))))
                #final_list.append(str((self.channels[channel]['prefix']) + int(interp(val, [0,100], self.channels[channel]['min_max'][::-1]))))
            else:
                raise IndexError
        if not too_short:
            #print(final_list)
            self.send_value("$" + "%$".join(final_list) + "%")
            self.list_with_ems_strength = {}
            self.last_sent_ems = time.time()


    def send_value(self, value):
        if value != self.previously_sent and not self.no_serial and not self.study_no_ems:
            self.ser.write(bytes(value, "UTF-8"))
            self.previously_sent = value
            print(value)

    def subscribe(self, callback):
        self.subscribers.append(callback)

    # def run(self):
#         """docstring for run"""
#         while True:
#
#           if not self.no_serial:
#             #print(self.ser.readline(1))
#             data = self.ser.readline(1024)
#             if data:
#                 if self.arduino_value_callback != None:
#                   self.arduino_value_callback(data.decode("utf-8").replace('\n', '').replace('\r', ''))
#           if not self.no_serial_cap:
#               data = self.ser_capacitive.readline(1)
#               if data and data != bytes("\n", "utf-8") and data != bytes("\r", "utf-8") and not self.stop:
#                   for subscriber in self.subscribers:
#                       subscriber(data.decode("utf-8").replace('\n', '').replace('\r', ''))
#           time.sleep(0.01)




