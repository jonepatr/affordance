
import unittest
from unittest.mock import call, MagicMock
#sys.modules['pickle'] = MagicMock()
#sys.modules['pickle'].load = self.fake_pickle_load
import numpy as np
import math
from lib.hand import Hand


class test_hand(unittest.TestCase):
    """docstring for test_hand"""
    
    def fake_mongo_envelope_reply(self, argument):
        return [{
            "name": "envelope_1",
            "gesture": "test_gesture",
            "allpoints": self.envelope_allpoints
            
        }]
        
    def fake_mongo_gesture_reply(self, argument):
        return [{
            "_id": "test_gesture",
            "allpoints": self.gesture_allpoints
        }]
    
    def setUp(self):
        """docstring for setUp"""
        self.gesture_allpoints = {
            "ems1": [1,2,3,4,5,10,4,2,5,6,4,5,6,1,44],
            "ems2": [1] * 15
        }
        self.envelope_allpoints = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        
        self.df = MagicMock()
        self.db = MagicMock()
        self.ar = MagicMock()
        self.db.envelopes.find = self.fake_mongo_envelope_reply
        self.db.gestures.find = self.fake_mongo_gesture_reply    
    
    
    
    ###### TESTS 
   
   
   
    def test_reload_db(self):  
        hand = Hand(self.df, self.db, self.ar)
        self.assertEqual(hand.envelopes, self.fake_mongo_envelope_reply({}))
        self.envelope_allpoints = [1,5,4]
        hand.reload_db()
        self.assertEqual(hand.envelopes, self.fake_mongo_envelope_reply({}))
    
    def test_collision_detected(self):
        self.ar.channels = {
            'ems1': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 1000, 'last_value': 0, 'ems_on_off': False}, 
            'ems2': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 2000, 'last_value': 0, 'ems_on_off': False}
        }
        hand = Hand(self.df, self.db, self.ar)
        hand.collision_detected("hand", "envelope_1", 1.0)
        self.assertFalse(self.ar.send_value.called)
        hand.collision_detected("hand", "envelope_1", 0.5)
        self.ar.send_ems_strength.assert_called_with({"ems1": 0.54, "ems2": 0.09})
        hand.collision_detected("hand", "envelope_1", 0.2)
        self.ar.send_ems_strength.assert_called_with({"ems1": 0.2, "ems2": 0.04})
        
        self.ar.reset_mock()
        
        
        multiplied_list_ems1 = self.multiply_lists(self.gesture_allpoints['ems1'],self.envelope_allpoints)
        multiplied_list_ems2 = self.multiply_lists(self.gesture_allpoints['ems2'],self.envelope_allpoints)
        assertions = []
        for each in range(50):
            dist = 1 - (each/50)
            hand.collision_detected("hand", "envelope_1", dist)
            if dist < 0.8:             
                index = int(Hand.my_round( 14 * (dist/0.8) ) )
                val_ems1 =  multiplied_list_ems1[index]
                val_ems2 =  multiplied_list_ems2[index]
                assertions.append(call.send_ems_strength({"ems1": val_ems1, "ems2": val_ems2}))
                
        self.ar.assert_has_calls(assertions)
        
        
        hand.gesture_list['test_gesture']['allpoints'] = {
            "ems1": [3,2,99],
            "ems2": [1,1,1]
        }        
        hand.envelope_list['envelope_1']['allpoints'] = [9,5,13]
        

        hand.collision_detected("hand", "envelope_1", 0.4)
        self.ar.send_ems_strength.assert_called_with({"ems1": 0.1, "ems2": 0.05})
        
        
        hand.collision_detected("hand", "no_target", 999999)
        self.ar.send_ems_strength.assert_called_with({"ems1": 0, "ems2": 0}, True)
        
        # Test when hand stops moving
        
        # Only do action once until person leaves bounding box
        
        # if hand has higher speed, increase speed of gesture, if slower, slow down until minimum. if hand has negative acceleration for x seconds, stop gesture. 
        
        


    ## Helpers

    def multiply_lists(self, list1, list2):
        return list(map(lambda x: x/100, [a*b for a,b in zip(list1, list2)]))

    def my_round(x):
        return int(x + math.copysign(0.5, x))
        
        