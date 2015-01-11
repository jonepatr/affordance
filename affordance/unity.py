from pythonosc import osc_message_builder, dispatcher, osc_server, udp_client
import threading
import distutils.util
import math

class Unity(threading.Thread):
    """Class to communicate with unity"""

    daemon = True
    client = udp_client.UDPClient("127.0.0.1", 12000)
    osc_object_counter = {}
    spray_open = False
    spray_grasp = False

    def collision_handler(self, unused_addr, data):
        """Callback with collision data from unity"""
        #print(data)
        split_data = data.split(",")
        if self.hand is not None:
            self.hand.collision_detected(split_data[0], split_data[1], float(split_data[2]))

    def colliders_handler(self, unused_addr, list_obj):
        """Callback from unity about collider objects"""
        if self.collider_callback and list_obj:
            self.collider_callback(list_obj)

    def bbox_handler(self, unused_addr, data):
        split_data = data.split(",")
        #print(split_data)
        if self.hand:
            self.hand.inside_bbox_name = split_data
            self.leaving_bbox = False

    def extra_info_handler(self, unused_addr, data):
        split_data = data.split(",")
        if split_data[0] == "screw_driver":
            self.hand.inside_bbox_name = "screw_driver"
            self.hand.inside_bbox = distutils.util.strtobool(split_data[1])
            #self.hand.screw_driver_in_bbox = distutils.util.strtobool(split_data[1])
            
    def leaving_bbox_handler(self, unused_addr, data):
        self.hand.leaving_bbox = True
        self.hand.stop_distance_gestures = False
        self.hand.ar.stop_gesture = True
        self.hand.touching_spray_can = False
        self.hand.touch_started = 0

    def add_trackable(self, trackable, name):
        """Add object so that data is being sent to unity"""
        self.trackables[name] = trackable

    def __init__(self):
        """docstring for __init__"""
        super(Unity, self).__init__()
        self.trackables = dict()
        self.collider_callback = None
        self.hand = None

    def run(self):
        """Run thread"""
        disp = dispatcher.Dispatcher()
        disp.map("/collision", self.collision_handler)
        disp.map("/colliders", self.colliders_handler)
        disp.map("/enter_boundingbox", self.bbox_handler)
        disp.map("/extra_info", self.extra_info_handler)
        disp.map("/leaving_bbox", self.leaving_bbox_handler)
        server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 3201), disp)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()

    def ask_for_colliders(self, callback):
        """Ask unity for collider objects"""
        self.collider_callback = callback
        msg = osc_message_builder.OscMessageBuilder(address="/askForColliders")
        msg.add_arg("_")
        msg = msg.build()
        Unity.client.send(msg)

    def send_msg(message):
        msg = osc_message_builder.OscMessageBuilder(address="/" + message)
        msg.add_arg("_")
        msg = msg.build()
        Unity.client.send(msg)

    def update_position(object_in_space):
        """docstring for update_position"""
        unity_answer = object_in_space.unity_answer()
        for uanswer in unity_answer:
            if not uanswer is None:
                msg = osc_message_builder.OscMessageBuilder(address="/positionUpdate")
                first = True
                for msg_part in uanswer:
                    if not first and math.isnan(msg_part):
                        msg_part = 0
                    msg.add_arg(str(msg_part))
                    first = False
                msg = msg.build()
                if not uanswer[0] in Unity.osc_object_counter:
                    Unity.osc_object_counter[uanswer[0]] = 0
                Unity.osc_object_counter[uanswer[0]] += 1
                if Unity.osc_object_counter[uanswer[0]] % (len(Unity.osc_object_counter)*4) == 0:
                    Unity.client.send(msg)
