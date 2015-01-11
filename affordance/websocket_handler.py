import tornado.websocket as websocket
import bson.json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from arduino import Arduino
from hand import Hand
import json
from data_fetcher import DataFetcher
import time

class WebsocketHandler(websocket.WebSocketHandler):
    def initialize(self, uni):
        """docstring for __init__"""
        self.arduino = Arduino()
        self.arduino.start()
        self.client = MongoClient('localhost', 27017)
        self.uni = uni
        self.mongo_gestures = self.client.affordance.gestures
        self.mongo_envelopes = self.client.affordance.envelopes
        self.mongo_users = self.client.affordance.users
        self.mongo_tracking = self.client.affordance.tracking
        self.mongo_studies = self.client.affordance.studies
        self.list_obj = []
        self.current_study_participant = None
        self.data_fetcher = DataFetcher(self.client.affordance)
        self.zap_speed = 1500
        self.zap_strength = {"ems1": self.arduino.channels['ems1']['min_max'][0], "ems2": self.arduino.channels['ems2']['min_max'][0]}
        self.zap_gestures = {"squeeze": False, "shake": False, "repel": False, "tap": False, "rotate": False, "ems1": False, "ems2": False, "ems3": False, "ems4": False}
        #self.data_fetcher = DataFetcher(self.mongo_tracking, False) # Recorded data!
        self.hand = Hand(self.data_fetcher, self.client.affordance, self.arduino)

        self.uni.hand = self.hand
        #screw_driver = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["screwdriver_trackable"], "screwdriver", "Screwdriver")
        #screw_brick = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["screw_brick_trackable"], "screw_brick", "Screw brick")
        #teapot = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["teapot_trackable"], "teapot", "Teapot")
        #spray_can = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["spray_can_trackable"], "spray_can", "Spray Can")
        #lamp = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["hot_cup_trackable"], "hot_cup", "hot_cup")
        #paint_brush = AffordanceObjects(self.data_fetcher, self.uni, self.arduino, ["paint_trackable"], "paint_brush", "Paint brush")
        self.hand.start()
        self.data_fetcher.register_trackers()


    #def ar_callback(self, data):
    #  self.write_message("channel_data" + ";".join(map(lambda x: x[:-1][1:], data.split("#")))[1:])

    def collider_cb(self, list_obj):
        """Callback that sends the list of colliders to the web interface"""
        self.list_obj = list_obj
        self.write_message("colliders_init,True")

    def open(self):
        print("WebSocket opened")
        self.write_message("init," + json.dumps(self.arduino.channels).replace(",", "§") + "," + bson.json_util.dumps(self.mongo_users.find({})).replace(",", "§"))
        self.uni.ask_for_colliders(self.collider_cb)


    def on_message(self, msg):
        message = msg.split(",")
        if message[0] == "run":
            if message[1] == "true":
                self.arduino.stop = False
                self.data_fetcher.stop = False
                self.arduino.open_all_channels()
                print("run")
            else:
                self.data_fetcher.stop = True
                self.arduino.stop = True
                self.arduino.close_all_channels()
                print("stop")
        elif message[0] == "teapot":
            if message[1] == "1":
                self.hand.current_state = "none"
            elif message[1] == "2":
                self.hand.current_state = "hot"
        elif message[0] == "muscle_control":
            if message[2] == "true":
                if message[1] == "ems1":
                    self.arduino.send_ems_strength({"ems1": self.zap_strength["ems1"]})
                    self.arduino.change_relay_state("ems1", True)
                elif message[1] == "ems2":
                    self.arduino.send_ems_strength({"ems2": self.zap_strength["ems2"]})
                    self.arduino.change_relay_state("ems2", True)
                elif message[1] == "ems3":
                    self.arduino.send_ems_strength({"ems3": self.zap_strength["ems1"]})
                    self.arduino.change_relay_state("ems3", True)
                elif message[1] == "ems4":
                    self.arduino.send_value("h")
                elif message[1] == "0":
                    if self.zap_strength["ems1"] > 4:
                        self.zap_strength["ems1"] -= 5
                    self.write_message("ems_strength,ems1," + str(self.zap_strength["ems1"]))
                elif message[1] == "-":
                    self.zap_strength["ems1"] = 0
                    self.write_message("ems_strength,ems1," + str(self.zap_strength["ems1"]))
                elif message[1] == "+":
                    if self.zap_strength["ems1"] < 96:
                        self.zap_strength["ems1"] += 5
                    self.write_message("ems_strength,ems1," + str(self.zap_strength["ems1"]))
                elif message[1] == "p":
                    if self.zap_strength["ems2"] > 4:
                        self.zap_strength["ems2"] -= 5
                    self.write_message("ems_strength,ems2," + str(self.zap_strength["ems2"]))
                elif message[1] == "[":
                    self.zap_strength["ems2"] = 0
                    self.write_message("ems_strength,ems2," + str(self.zap_strength["ems2"]))
                elif message[1] == "]":
                    if self.zap_strength["ems2"] < 96:
                        self.zap_strength["ems2"] += 5
                    self.write_message("ems_strength,ems2," + str(self.zap_strength["ems2"]))
            else:
                if message[1] == "ems1":
                    self.arduino.change_relay_state("ems1", False)
                elif message[1] == "ems2":
                    self.arduino.change_relay_state("ems2", False)
                elif message[1] == "ems3":
                    self.arduino.change_relay_state("ems3", False)
                elif message[1] == "ems4":
                    self.arduino.send_value("i")

        elif message[0] == "colliders_init_cb":
            user_id = {"user_id": ObjectId(message[1])}
            gestures = bson.json_util.dumps(list(self.mongo_gestures.find(user_id, {"name": True}))).replace(",", "§")
            envelopes = []
            if len(self.list_obj) > 0:
                for envelope in self.list_obj.split(","):
                    envelope_obj = self.mongo_envelopes.find({"user_id": ObjectId(message[1]), "name": envelope})

                    if envelope_obj.count() == 0:
                        self.mongo_envelopes.insert({
                            "name": envelope,
                            "gesture": "",
                            "gesture duration": 1000,
                            "allpoints": [],
                            "individual_points": [],
                            "user_id": ObjectId(message[1])
                        })

            envelopes = self.mongo_envelopes.find({"user_id": ObjectId(message[1])})
            envelopes = bson.json_util.dumps(envelopes).replace(",", "§")
            self.write_message("colliders," + gestures + "," + envelopes)


        elif message[0] == "study_start_trial":
            self.mongo_studies.update({"_id": self.current_study_participant}, {
                "$set": {
                    "trials." + message[1] + ".type": message[2],
                    "trials." + message[1] + ".optitrack_data": [],
                    "trials." + message[1] + ".touch_data": [],
                    "trials." + message[1] + ".timestamp": time.time()
                }
            })
            self.data_fetcher.get_data_for_study(self.current_study_participant, message[1])
            self.hand.get_data_for_study(self.current_study_participant, message[1])
            if message[2][-6:] == "-noems":
                self.arduino.study_no_ems = True

            self.start_time = time.time()

        elif message[0] == "study_end_trial":
            fat_var = self.data_fetcher.done_with_study_data()
            self.mongo_studies.update({"_id": self.current_study_participant}, {
                "$set": {
                    "trials." + message[1] + ".time": time.time() - self.start_time,
                    "trials." + message[1] + ".optitrack_data": fat_var
                }
            })
            self.hand.done_with_study_data()
            self.arduino.study_no_ems = False
        elif message[0] == "calibrate":
            self.arduino.calibration(message)
        elif message[0] == "load_study":

            data = self.mongo_studies.find_one({"participant_id": message[1]})
            self.current_study_participant = data["_id"]
            self.mongo_studies.update({"_id": self.current_study_participant}, {"$set": {"name": message[2], "trials": {}}})


            self.write_message("study_data," + json.dumps(data['order']).replace(",", "§"))
        elif message[0] == "save_channels":
            self.mongo_users.update({"_id": ObjectId(message[1])}, {"$set": {
                "channels." + message[2]: {
                    "min": message[3],
                    "max": message[4]
                }
            }})
        elif message[0] == "door":
            if message[1] == "e":
                self.hand.door_mode = "enter"
            elif message[1] == "k":
                self.hand.door_mode = "knock"

        elif message[0] == "load_user":
            self.hand.user = message[2]
            gestures = list(self.mongo_gestures.find({"user_id": ObjectId(message[2])}, {"name": True}))
            if not message[1] == message[2]:
                user_gestures = list(self.mongo_gestures.find({"user_id": ObjectId(message[1])}, {"name": True}))
                new_gestures = []
                for gesture in gestures:
                    for gest in user_gestures:
                        if gest['name'] == gesture['name']:
                            gest['name'] = gest['name'] + " (modified)"
                            gesture = gest
                    new_gestures.append(gesture)
                gestures = new_gestures


            the_user = self.mongo_users.find_one({"_id": ObjectId(message[1])})
            if the_user is not None:
                for channel, val in the_user['channels'].items():
                    if channel in self.arduino.channels.keys():
                        self.arduino.channels[channel]['min_max'] = [int(val['min']), int(val['max'])]
                users = bson.json_util.dumps(the_user).replace(",", "§")
                gestures = bson.json_util.dumps(gestures).replace(",", "§")

                self.write_message("user_info," + users + "," + gestures)
        elif message[0] == "add_user":
            user_id = self.mongo_users.insert({
                "name": message[1],
                "channels": {}
            })
            self.write_message("newly_added_user_id," + bson.json_util.dumps(self.mongo_users.find_one({"_id": ObjectId(user_id)})).replace(",", "§"))

        elif message[0] == "envelope":
            if message[1] == "save":
                already_exists = 0
                if message[8] == "true":
                    already_exists = self.mongo_envelopes.find({"_id": ObjectId(message[3]), "user_id": ObjectId(message[2])}).limit(1).count()
                if already_exists == 1:
                    self.mongo_envelopes.update({"_id": ObjectId(message[3])}, {"$set": {
                        "gesture": ObjectId(message[4]),
                        "gesture duration": message[5],
                        "allpoints": json.loads(message[6].replace("§", ",")),
                        "individual_points": json.loads(message[7].replace("§", ",")),
                    }})
                else:
                    if message[8] == "true":
                        name = self.mongo_envelopes.find({"_id": ObjectId(message[3])}).limit(0)[0]['name']
                    else:
                        name = message[3]

                    self.mongo_envelopes.insert({
                        "name": name,
                        "gesture": ObjectId(message[4]),
                        "gesture duration": message[5],
                        "allpoints": json.loads(message[6].replace("§", ",")),
                        "individual_points": json.loads(message[7].replace("§", ",")),
                        "user_id": ObjectId(message[2])
                    })
        elif message[0] == "gesture":
            if message[1] == "save":
                already_exists = self.mongo_gestures.find({"_id": ObjectId(message[3]), "user_id": ObjectId(message[2])}).limit(1).count()
                if already_exists == 1:
                    self.mongo_gestures.update({"_id": ObjectId(message[3])}, {"$set": {
                        "allpoints": json.loads(message[4].replace("§", ", ")),
                        "line_segments":  json.loads(message[5].replace("§", ", "))
                    }})
                else:
                    old_thing = self.mongo_gestures.find({"_id": ObjectId(message[3])}).limit(0)[0]
                    self.mongo_gestures.insert({
                        "name": old_thing['name'],
                        "allpoints": json.loads(message[4].replace("§", ", ")),
                        "line_segments":  json.loads(message[5].replace("§", ", ")),
                        "user_id": ObjectId(message[2])
                    })
                gestures = list(self.mongo_gestures.find({"user_id": ObjectId(message[2])}, {"name": True}))
                self.write_message("reload_gestures," + bson.json_util.dumps(gestures).replace(",", "§"))

            elif message[1] == "save_new":
                self.mongo_gestures.insert({
                    "name": message[3],
                    "allpoints": json.loads(message[4].replace("§", ", ")),
                    "line_segments":  json.loads(message[5].replace("§", ", ")),
                    "user_id": ObjectId(message[2])
                })
                gestures = list(self.mongo_gestures.find({"user_id": ObjectId(message[2])}, {"name": True}))
                self.write_message("reload_gestures," + bson.json_util.dumps(gestures).replace(",", "§"))
            elif message[1] == "get":
                gesture = bson.json_util.dumps(list(self.mongo_gestures.find({"_id": ObjectId(message[2])}))[0]).replace(",", "§")
                self.write_message("gesture_info," + gesture)
            elif message[1] == "test":
                duration = 1000
                if message[3] and message[3].isdigit():
                    duration = int(message[3])
                self.arduino.perform_gesture(json.loads(message[2].replace("§", ", ")), duration)

    def on_close(self):
        print("WebSocket closed")
