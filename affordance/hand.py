"""This module contains the hand class"""
import math
from object_in_space import ObjectInSpace
from collections import deque
import time
import threading
from unity import Unity

class Hand(ObjectInSpace, threading.Thread):
    """This class represents the hand of the user"""
    deamon = True

    def __init__(self, df, db, ar):
        """docstring for __init__"""
        ObjectInSpace.__init__(self, df, ar)
        threading.Thread.__init__(self)
        self.arduino = ar
        self.database = db
        self.data_fetcher = df
        self.human_name = "Hand"
        self.machine_name = "arm"
        self.user = -1
        self.velocity = 0.0
        self.acceleration = 0.0
        self.unity_velocity = deque([0], maxlen=2)
        self.unity_acceleration = deque([0], maxlen=2)
        self.unity_previous_distance = 0
        self.unity_previous_vel_cal = 0
        self.previous_time = 0
        self.previous_data = None
        self.record_for_study = False
        self.study_data = []
        self.reload_db()
        self.trackables = ["arm_trackable", "hand_trackable"]
        self.hand_angle = deque([[0, 0, 0, 1]], maxlen=5)
        self.hand_positions = deque([[0, 0, 0]], maxlen=5)
        self.max_angles = [0, 0]
        self.envelope_list = {}
        self.gesture_list = {}
        self.distance_to_current_target = -1
        self.previous_envelope = ""
        self.inside_bbox = False
        self.touching_spray_can = False
        self.subscribe_to_arduino_listener()
        self.envelope_name = ""
        self.distance = 9999999
        self.stop_distance_gestures = False
        self.touch_started = 0
        self.shaked_can = False
        self.inside_bbox_name = ""
        self.stopped_ems = False
        self.direction_target = None
        self.current_state = ""
        self.small_counter = 0
        self.small_counter2 = 0
        self.screw_direction = "screw"
        self.leaving_bbox = False
        self.door_mode = "enter"

        for gesture in self.gestures:
            self.gesture_list[str(gesture['_id'])] = gesture

        for envelope in self.envelopes:
            self.envelope_list[envelope['name']] = envelope

    def get_data_for_study(self, current_study_participant, q_index):
        self.record_for_study = True
        self.study_data = [current_study_participant, q_index]

    def done_with_study_data(self):
        self.record_for_study = False
        self.study_data = []


    def run(self):
        while True:
            if not self.data_fetcher.stop and not self.arduino.stop:
                if self.inside_bbox and not self.touching_spray_can and not self.leaving_bbox:
                    if self.inside_bbox_name == "spray_open_outer" and not self.shaked_can:
                        self.arduino.send_ems_strength({'ems2': 50, 'ems1': 0})
                    elif self.inside_bbox_name == "lamp_on_outer":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 60})
                    elif self.inside_bbox_name == "lamp_off_outer":
                        self.arduino.send_ems_strength({'ems2': 70, 'ems1': 0})
                    elif self.inside_bbox_name == "cup_body_outer" and self.envelope_name == "cup_body_hit_target":
                        self.arduino.send_ems_strength({'ems2': 70, 'ems1': 0})
                    elif self.inside_bbox_name == "cup_body_outer" and self.envelope_name == "cup_ear_hit_target":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 60})
                    elif self.inside_bbox_name == "door_handle_repel" and self.door_mode != "enter":
                        self.arduino.send_ems_strength({'ems2': 70, 'ems1': 0})
                    elif self.inside_bbox_name == "knock_outer" and self.envelope_name == "knock_hit_target":
                        #self.arduino.send_ems_strength({'ems2': 0, 'ems1': 60})
                        print(750 - abs(400*self.distance))
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 850 - abs(400*self.distance))
                        self.arduino.open_all_channels()
                    elif self.inside_bbox_name == "knock_hit_target2" and  self.door_mode == "knock":
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        self.arduino.open_all_channels()
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        self.arduino.open_all_channels()
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        self.arduino.open_all_channels()
                    elif self.inside_bbox_name == "spray_grasp_outer" and not self.shaked_can:
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 35})
                    elif self.inside_bbox_name == "paint_brush_repel_outer":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif self.inside_bbox_name == "paint_brush_grasp_outer":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 40})
                    elif (self.inside_bbox_name == "screw_2_outer" or self.inside_bbox_name == "screw_3_outer") and self.current_state == "get_screw_1":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif (self.inside_bbox_name == "screw_1_outer" or self.inside_bbox_name == "screw_3_outer") and self.current_state == "get_screw_2":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif (self.inside_bbox_name == "screw_1_outer" or self.inside_bbox_name == "screw_2_outer") and self.current_state == "get_screw_3":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif (self.inside_bbox_name == "tool_2_outer" or self.inside_bbox_name == "tool_3_outer") and self.current_state == "get_tool_1":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif (self.inside_bbox_name == "tool_1_outer" or self.inside_bbox_name == "tool_3_outer") and self.current_state == "get_tool_2":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif (self.inside_bbox_name == "tool_1_outer" or self.inside_bbox_name == "tool_2_outer") and self.current_state == "get_tool_3":
                        self.arduino.send_ems_strength({'ems2': 60, 'ems1': 0})
                    elif self.inside_bbox_name == "screw_1_outer" and self.current_state == "get_screw_1":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.inside_bbox_name == "screw_2_outer" and self.current_state == "get_screw_2":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.inside_bbox_name == "screw_3_outer" and self.current_state == "get_screw_3":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.inside_bbox_name == "tool_1_outer" and self.current_state == "get_tool_1":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.inside_bbox_name == "tool_2_outer" and self.current_state == "get_tool_2":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.inside_bbox_name == "tool_3_outer" and self.current_state == "get_tool_3":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 43})
                    elif self.current_state == "neutral":
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 0})
                    elif self.inside_bbox_name == "repel_teapot_outer" and self.envelope_name == "repel_teapot_hit_target":
                        if self.current_state == "hot":
                            proc_dist = self.distance/0.5
                            if proc_dist > 1:
                                proc_dist = 0
                            self.arduino.send_ems_strength({'ems2': (1-proc_dist)*60, 'ems1': 0})
                        else:
                            self.arduino.send_ems_strength({'ems2': 0, 'ems1': 0})
                    elif self.inside_bbox_name == "grasp_teapot_outer" and self.envelope_name == "grasp_teapot_hit_target":
                        proc_dist = self.distance/0.5
                        if proc_dist > 1:
                            proc_dist = 0
                        if self.distance < 0.01:
                            proc_dist = 1
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': (1-proc_dist)*43})
                    elif self.inside_bbox_name == "grasp_screwdriver_outer" and self.envelope_name == "screwdriver_hit_target":
                        proc_dist = self.distance/0.8
                        if proc_dist > 1:
                            proc_dist = 0
                        if self.distance < 0.01:
                            proc_dist = 1
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': (1-proc_dist)*43})
                    elif self.inside_bbox_name == "screw_driver":
                        if self.screw_direction == "unscrew":
                            self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                            self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        else:
                            ems1 = self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints']['ems1']
                            ems2 = self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints']['ems2']
                            inverted_gesture = {'ems1': ems2, 'ems2': ems1}
                            self.arduino.perform_gesture(inverted_gesture, 750)
                            self.arduino.perform_gesture(inverted_gesture, 750)
                        self.inside_bbox_name = ""
                        self.inside_bbox = False
                    else:
                        self.arduino.send_ems_strength({'ems2': 0, 'ems1': 0})
                    time.sleep(0.005)
                elif self.touching_spray_can:
                    if time.time() - self.touch_started > 0.5 and self.touch_started != 0 and not self.shaked_can:
                        print("0")
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        print("1")
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        print("2")
                        self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 750)
                        print("done!")
                        Unity.send_msg("done_shaking")
                        self.arduino.open_all_channels()
                        self.shaked_can = True
                        self.touch_started = 0
                        self.touching_spray_can = False
                    time.sleep(0.005)
                else:
                    self.small_counter += 1
                    if self.small_counter > 10:
                        stop_ems = {}
                        self.inside_bbox = False
                        self.inside_bbox_name = "no_target"
                        self.distance = 999999
                        self.stopped_ems = True
                        for channel in self.arduino.channels.keys():
                            stop_ems[channel] = 0
                        self.arduino.send_ems_strength(stop_ems, True)
                        self.small_counter = 0
                    time.sleep(0.01)
            else:
                self.small_counter += 1
                self.touch_started = 0
                if self.small_counter > 10:
                    self.shaked_can = False
                    self.inside_bbox = False
                    self.inside_bbox_name = ""
                    self.small_counter = 0
                time.sleep(0.2)
         #
   #
   #
   #
   #
   #
   #
   #
   #
   #
   #
   #
   #
   #        bb = 0
   #        spray_open = False
   #        spray_grasp = False
   #        # Divide into time gesture and distance gesture
   #        while True:
   #            time.sleep(0.1)
   #            #print(time.time() - self.touch_started)
   #            if self.stop_distance_gestures:
   #                #print(time.time() - self.touch_started)
   #                if time.time() - self.touch_started > 0.75 and not 0 and not self.shaked_can:
   #                   self.stopped_ems = False
   #                   self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 1500)
   #                   self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 1500)
   #                   self.arduino.perform_gesture(self.gesture_list['53f3718d805aee10a48a7bd3']['allpoints'], 1500)
   #                   self.touch_started = 0
   #                   self.shaked_can = True
   #            else:
   #                # if self.inside_bbox_name == "spray_open_outer" and not spray_open:
   #   #                  spray_open = True
   #   #                  print("spray_open_outer")
   #   #                  self.arduino.perform_gesture(self.gesture_list['53f35079805aee36a4e0787c']['allpoints'], 1500)
   #   #              elif self.inside_bbox_name == "spray_grasp_outer" and not spray_grasp:
   #   #                  spray_grasp = True
   #   #                  print("spray_grasp_outer")
   #   #                  self.arduino.perform_gesture(self.gesture_list['53f350ae805aee36a4e0787d']['allpoints'], 1500)
   #                # else:
   # #                    stop_ems = {}
   # #                    self.stopped_ems = True
   # #                    for channel in self.arduino.channels.keys():
   # #                        stop_ems[channel] = 0
   # #                    self.arduino.send_ems_strength(stop_ems, True)
   #
   #                self.envelope_name = ""
   #                if bb%5 == 5:
   #                  self.distance = 9999999
   #                  bb = 0
   #                bb += 1
   #                time.sleep(0.02)


    def shake_spray(self):
        self.arduino.perform_gesture(self.gesture_list['53e125c0fda21d82430a7a7f']['allpoints'], 3000)

    def arudino_callback(self, msg):
        mongo_state = ""
        print("From ar: " + msg)
        if msg == "a" and not self.touching_spray_can:
            self.stop_distance_gestures = True
            self.touching_spray_can = True
            self.arduino.stop_gesture = False
            #thread.start_new_thread(self.shake_spray, ())
            mongo_state = "touched"
            self.touch_started = time.time()
            Unity.send_msg("init_bbox")
        elif msg == "w":
            self.stop_distance_gestures = False
            self.arduino.stop_gesture = True
            self.touching_spray_can = False
            mongo_state = "released"
            self.touch_started = 0
            Unity.send_msg("done_shaking")
        elif msg == "g":
            self.screw_direction = "unscrew"
        elif msg == "h":
            self.screw_direction = "screw"
        if self.record_for_study and mongo_state != "":
            self.database.studies.update({"_id": self.study_data[0]}, {"$push": {"trials." + self.study_data[1] + ".touch_data": {"action": mongo_state, "timestamp": time.time()}}})



    def reload_db(self):
        find = {}
        if self.user != -1:
            find = {"user_id": self.user}
        self.gestures = list(self.database.gestures.find(find))
        self.envelopes = list(self.database.envelopes.find(find))


    def unity_answer(self):
        return [[
            self.machine_name,
            self.position[0],
            self.position[1],
            self.position[2],
            self.angle[0],
            self.angle[1],
            self.angle[2],
            self.angle[3]
        ], [
            "hand",
            self.hand_position_avg[0],
            self.hand_position_avg[1],
            self.hand_position_avg[2],
            self.hand_angle_avg[0],
            self.hand_angle_avg[1],
            self.hand_angle_avg[2],
            self.hand_angle_avg[3]
        ]]


    def after_on_data(self, data, index):
        """This method deals with the callback from DataFetcher"""
        if index is 0:
            if data is not None and self.previous_data is not None:
                time_difference = data["time"] - self.previous_data["time"]
                seconds_in_between = time_difference.total_seconds()
                previous_position = self.previous_data["position"]
                diff_x = data["position"][0] - previous_position[0]
                diff_y = data["position"][1] - previous_position[1]
                diff_z = data["position"][2] - previous_position[2]
                dist = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
                if seconds_in_between == 0:
                    seconds_in_between = 0.0000001
                new_velocity = dist / seconds_in_between
                self.acceleration = (self.velocity-new_velocity)/seconds_in_between
                self.velocity = new_velocity
            self.previous_data = data
        elif index is 1:
            self.hand_angle.appendleft(data["quaternion"])
            self.hand_positions.appendleft(data["position"])




    def collision_detected(self, bbox_name, envelope_name, distance):
        """docstring for collision_detected"""
        self.inside_bbox_name = bbox_name
        self.inside_bbox = True
        self.envelope_name = envelope_name
        self.distance = distance

    def my_round(x):
        return int(x + math.copysign(0.5, x))

    @property
    def hand_angle_avg(self):
        return_val = [0, 0, 0, 0]
        ang = list(self.hand_angle)
        for each in ang:
            return_val[0] += each[0]
            return_val[1] += each[1]
            return_val[2] += each[2]
            return_val[3] += each[3]
        return [return_val[0]/float(len(ang)), return_val[1]/float(len(ang)), return_val[2]/float(len(ang)), return_val[3]/float(len(ang))]

    @property
    def hand_position_avg(self):
        #    return self.positions
        return_val = [0, 0, 0]

        pos = list(self.hand_positions)
        for each in pos:
            return_val[0] += each[0]
            return_val[1] += each[1]
            return_val[2] += each[2]
        #return [0,0,0]
        return [return_val[0]/float(len(pos)), return_val[1]/float(len(pos)), return_val[2]/float(len(pos)), ]
