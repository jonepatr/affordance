from collections import deque
from unity import Unity
import math

class ObjectInSpace(object):

    def __init__(self, df, arduino):
        """docstring for __init__"""
        self.machine_name = ""
        self.human_name = ""
        self.arduino = arduino
        self.trackables = [""]
        self.positions = deque([[0, 0, 0]], 5)
        self.angles = deque([[0, 0, 0, 1]], 5)
        self.collision_objects = dict()
        self.data_fetcher = df
        self.data_fetcher.add_trackable(self)
        self.bounding_boxes = dict()
    def on_data_callback(self, userdata, data, index):
        if index is 0:
            self.positions.appendleft(data["position"])
            self.angles.appendleft(data["quaternion"])
        self.after_on_data(data, index)
        Unity.update_position(self)

    def after_on_data(self, data, index):
        pass

    def average_dist(self, dist_list):
        distance_list = list(dist_list)
        return sum(distance_list)/float(len(distance_list))

    def unity_answer(self):
        return None

    def collision_detection(self, collision_object, distance):
        if not collision_object in self.collision_objects:
            self.collision_objects[collision_object] = deque(maxlen=3)
        self.collision_objects[collision_object].appendleft(float(distance))
        self.collision_update()

    def collision_update(self):
        pass

    def subscribe_to_arduino_listener(self):
        self.arduino.subscribe(self.arudino_callback)

    def arudino_callback(self, msg):
        pass

    @property
    def angle(self):
        return_val = [0, 0, 0, 0]
        ang = list(self.angles)
        for each in ang:
            return_val[0] += each[0]
            return_val[1] += each[1]
            return_val[2] += each[2]
            return_val[3] += each[3]

        quat_x = return_val[0]/float(len(ang))
        quat_y = return_val[1]/float(len(ang))
        quat_z = return_val[2]/float(len(ang))
        quat_w = return_val[3]/float(len(ang))
        if math.isnan(quat_x):
            quat_x = 0
        if math.isnan(quat_y):
            quat_y = 0
        if math.isnan(quat_z):
            quat_z = 0
        if math.isnan(quat_w):
            quat_w = 0

        return [quat_x, quat_y, quat_z, quat_w]

    @property
    def position(self):
        #    return self.positions
        return_val = [0, 0, 0]
        pos = list(self.positions)
        for each in pos:
            return_val[0] += each[0]
            return_val[1] += each[1]
            return_val[2] += each[2]
        #return [0,0,0]
        x_val = return_val[0]/float(len(pos))
        y_val = return_val[1]/float(len(pos))
        z_val = return_val[2]/float(len(pos))
        if math.isnan(x_val):
            x_val = 0
        if math.isnan(y_val):
            y_val = 0
        if math.isnan(z_val):
            z_val = 0

        return [x_val, y_val, z_val]
        #return [statistics.mean(list(self.positions)), statistics.mean(list(self.positions[1])), statistics.mean(list(self.positions[2]))]
