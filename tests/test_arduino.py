import sys
import unittest
from unittest.mock import patch, call, MagicMock

from lib.arduino import Arduino

from nose_focus import focus

class test_arduino(unittest.TestCase):
    """docstring for test_arduino"""
    
    
    def test_init(self):
        def serial_return():
            raise SerialException
      
        with patch.multiple('lib.arduino', serial=serial_return):
            ard = Arduino()
            self.assertEqual(ard.no_serial, True)
      
        with patch.multiple('lib.arduino', serial=MagicMock()):
            ard = Arduino()
            self.assertEqual(ard.no_serial, False)


    @patch.multiple('lib.arduino.Arduino', change_relay_state=MagicMock())
    def test_open_all_channels(self):
        """docstring for test_open_all_channels"""
        
        ard = Arduino()
        ard.channels = {
            'ems1': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 1000, 'last_value': 0, 'ems_on_off': False}, 
            'ems2': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 2000, 'last_value': 0, 'ems_on_off': False}
        }
        
        ard.open_all_channels()
        calls = [call("ems1", True), call("ems2", True)]        
        ard.change_relay_state.assert_has_calls(calls, True)


    @patch.multiple('lib.arduino.Arduino', send_value=MagicMock())
    def test_stop_all(self):
        ard = Arduino()
        ard.stop_all()
        ard.send_value.assert_called_with("s")
                 
       
       
    @patch.multiple('lib.arduino.Arduino', send_value=MagicMock())
    def test_change_relay_state(self):
        ard = Arduino()                 
        ard.channels = {
            'relay1': {'type': 'relay', 'state': False, 'serial_open': 'o', 'serial_close': 'c'},
            'relay2': {'type': 'relay', 'state': False, 'serial_open': 'k', 'serial_close': 'l'}
        }
        
        ard.change_relay_state("relay1", True)                
        self.assertEqual(ard.channels['relay1']['state'], True)
        ard.send_value.assert_called_with("o")

        ard.change_relay_state("relay2", True)
        self.assertEqual(ard.channels['relay2']['state'], True)
        ard.send_value.assert_called_with("k")

        ard.change_relay_state("relay1", False)
        self.assertEqual(ard.channels['relay1']['state'], False)
        ard.send_value.assert_called_with("c")

        ard.change_relay_state("relay2", 0)
        self.assertEqual(ard.channels['relay2']['state'], False)
        ard.send_value.assert_called_with("l")

  
        
    
    @patch.multiple('lib.arduino.Arduino', send_value=MagicMock(), send_ems_strength=MagicMock(), change_relay_state=MagicMock())
    def test_calibration(self):
        """docstring for test_calibration"""      
        ard = Arduino()        
        ard.channels = {
            'ems1': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 1000, 'last_value': 0, 'ems_on_off': False}, 
            'ems2': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 2000, 'last_value': 0, 'ems_on_off': False}
        }
        
        
        def test_calibration_reset():
            message = ["calibrate", "reset"]
            ard.calibration(message)
            ard.send_value.assert_called_with("r")
            
        
        def test_calibration_set_min_max():
            self.assertEqual(ard.channels['ems1']['min_max'],[0,80])
            self.assertEqual(ard.channels['ems2']['min_max'],[0,80])
            
            message = ["calibrate", "ems_min_max", "ems1", "10", "80"]
            ard.calibration(message)
            self.assertEqual(ard.channels['ems1']['min_max'],[10,80])
            self.assertEqual(ard.channels['ems2']['min_max'],[0,80])
            
            message = ["calibrate", "ems_min_max", "ems2", "6", "19"]
            ard.calibration(message)
            self.assertEqual(ard.channels['ems1']['min_max'],[10,80])
            self.assertEqual(ard.channels['ems2']['min_max'],[6,19])
            
            with self.assertRaises(ValueError):
                message = ["calibrate", "ems_min_max", "ems2", "a", "19"]
                ard.calibration(message)
            
            with self.assertRaises(IndexError):            
                message = ["calibrate", "ems_min_max"]
                ard.calibration(message)
             


        def test_calibration_ems_on_off():
            message = ["calibrate", "ems_on_off", "ems1", "true"]                                            
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems1", True)
            
            message = ["calibrate", "ems_on_off", "ems2", "true"]                                            
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems2", True)
            
            message = ["calibrate", "ems_on_off", "ems1", "false"]                                            
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems1", False)                         
                          
            message = ["calibrate", "ems_on_off", "ems1", "0"]                                            
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems1", False)       
            
            with self.assertRaises(ValueError):            
                message = ["calibrate", "ems_on_off", "ems1", "a"]                                            
                ard.calibration(message)
                
            with self.assertRaises(IndexError):            
                message = ["calibrate", "ems_on_off"]
                ard.calibration(message)
            
        def test_calibration_ems_value():
            message = ["calibrate", "ems_value", "ems1", "25"]
            ard.calibration(message)
            ard.send_ems_strength.assert_called_with({"ems1": 25})        
            
            message = ["calibrate", "ems_value", "ems2", "25"]
            ard.calibration(message)
            ard.send_ems_strength.assert_called_with({"ems2": 25})            
            

            with self.assertRaises(ValueError):            
                message = ["calibrate", "ems_value", "ems1", "a"]                                         
                ard.calibration(message)
                
            with self.assertRaises(ValueError):            
                message = ["calibrate", "ems_value", "ems1", "49.1"]
                ard.calibration(message)
            
            with self.assertRaises(ValueError):            
                message = ["calibrate", "ems_value", "ems1", "-1"]
                ard.calibration(message)
            
            
            with self.assertRaises(IndexError):            
                message = ["calibrate", "ems_value", "ems1"]
                ard.calibration(message)
            
        def test_calibration_relay():
            message = ["calibrate", "relay", "ems1", "true"]
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems1", True)
            
            message = ["calibrate", "relay", "ems2", "true"]
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems2", True)
            
            message = ["calibrate", "relay", "ems1", "false"]
            ard.calibration(message)
            ard.change_relay_state.assert_called_with("ems1", False)
            
            with self.assertRaises(ValueError):            
                message = ["calibrate", "relay", "ems1", "a"]                                         
                ard.calibration(message)
                
            with self.assertRaises(IndexError):            
                message = ["calibrate", "relay", "ems1"]
                ard.calibration(message)
            
            
                  
        test_calibration_reset()
        test_calibration_set_min_max()
        test_calibration_ems_on_off()
        test_calibration_ems_value()
        test_calibration_relay()
        
     
     
     
    def test_send_value(self):
        ar = Arduino()
        ar.ser = MagicMock()
        
        
        
        ar.no_serial = True
        
        ar.previously_sent = None
        ar.send_value("1")        
        self.assertFalse(ar.ser.write.called)
        
        
        ar.no_serial = False
                
        ar.previously_sent = None
        ar.send_value("1")    
        ar.ser.write.assert_called_with(bytes("1", "UTF-8"))
        self.assertEqual(ar.previously_sent, "1")
        ar.ser.write.reset_mock()
        
        ar.previously_sent = "1"
        ar.send_value("1")    
        self.assertFalse(ar.ser.write.called)

     
    def test_subscribe(self):
        ar = Arduino()
        ar.subscribers = []        
        cb = MagicMock()       
        ar.subscribe(cb)        
        self.assertEqual(ar.subscribers[0], cb)                
     
     
     
    def test_run(self):        
        ar = Arduino()        
        ar.stop = False
        ar.no_serial = False
        cb = MagicMock()
        ar.ser = MagicMock()
        
        def fake_readline(val):
            return b"l"
        ar.ser.readline = fake_readline
        ar.subscribers = [cb]
        ar.start()
        ar.stop = True
        ar.join()
        cb.assert_called_with("l")
        
     
     
     
        
    @patch.multiple('lib.arduino.Arduino', send_value=MagicMock())
    def test_send_ems_strength(self):
        """docstring for test_send_percentage"""
                     
        ard = Arduino()
        ard.channels = {
            'ems1': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 1000, 'last_value': 0, 'ems_on_off': False}, 
            'ems2': {'min_max': [0, 80], 'type': 'digipot', 'prefix': 2000, 'last_value': 0, 'ems_on_off': False}
        }
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 0, "ems2": 0})   
        ard.send_value.assert_called_with("$1100%$2100%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 100, "ems2": 100})        
        ard.send_value.assert_called_with("$1020%$2020%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 100})        
        ard.send_value.assert_called_with("$1020%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 100, "ems2": 0})        
        ard.send_value.assert_called_with("$1020%$2100%")        
        
        ard.last_sent_ems = 0
        ard.channels['ems1']['min_max'] = [12,100]
        ard.send_ems_strength({"ems1": 0, "ems2": 0})      
        ard.send_value.assert_called_with("$1088%$2100%")
  
        ard.last_sent_ems = 0
        ard.channels['ems1']['min_max'] = [20,67]
        ard.send_ems_strength({"ems1": 0, "ems2": 0})
        ard.send_value.assert_called_with("$1080%$2100%")
        
        ard.last_sent_ems = 0
        ard.channels['ems1']['min_max'] = [20,67]
        ard.send_ems_strength({"ems1": 100, "ems2": 0})
        ard.send_value.assert_called_with("$1033%$2100%")
        
        ard.last_sent_ems = 0
        ard.channels['ems1']['min_max'] = [20,80]
        ard.send_ems_strength({"ems1": 25, "ems2": 0})
        ard.send_value.assert_called_with("$1075%$2100%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 25.3, "ems2": 0})
        ard.send_value.assert_called_with("$1075%$2100%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": -1, "ems2": 0})
        ard.send_value.assert_called_with("$1080%$2100%")
        
        ard.last_sent_ems = 0
        ard.send_ems_strength({"ems1": 101, "ems2": 0})
        ard.send_value.assert_called_with("$1020%$2100%")        
        
        ard.last_sent_ems = 0
        with self.assertRaises(ValueError):
            ard.send_ems_strength({"ems1": "wrong", "ems2": 0})
        
        ard.last_sent_ems = 0
        with self.assertRaises(ValueError):
            ard.send_ems_strength({"ems1": 0, "ems2": "wrong"})
        
        ard.last_sent_ems = 0
        with self.assertRaises(IndexError):
            ard.send_ems_strength({"ThisWillNeverBeAnamefoooorANems": 100})
            
        