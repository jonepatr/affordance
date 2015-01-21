#pragma strict

import System.Collections.Generic;
var objectHolder = {};
var colliders : Array = [];
var servers = new Dictionary.<String, ServerLog>();
public var armModel : GameObject;
public var hand : GameObject;
function Awake () {
	OSCHandler.Instance.Init();
  	var collisionFields : Array = GameObject.FindGameObjectsWithTag ("CollisionField");
  	for(var collisionField : GameObject in collisionFields) {
    	colliders.push(collisionField.name);
  	}
  	oscColliders();
  	armModel = GameObject.Find("arm_model");
  	hand = GameObject.Find("hand")
}

function FixedUpdate() {
  	OSCHandler.Instance.UpdateLogs();  
  	servers = OSCHandler.Instance.Servers;
	for (item in servers) {	
		if(item.Value.packets.Count > 0) {		
			var lastPacketIndex = item.Value.packets.Count - 1;
			if (item.Value.packets[lastPacketIndex].TimeStamp == 0) {			
				switch(item.Value.packets[lastPacketIndex].Address){					
					case '/external':											
						armModel.GetComponent(SkinnedMeshRenderer).material.color = Color.red;																		
					break;
					case '/askForColliders':
						oscColliders();
					break;
					case '/positionUpdate':						
						var oscData = item.Value.packets[lastPacketIndex].Data;
						var x : float = parseOSCMessage(oscData[1]);						
					    var y : float = parseOSCMessage(oscData[2]);
					    var z : float = -parseOSCMessage(oscData[3]);
					    var qx : float = -parseOSCMessage(oscData[4]);
					    var qy : float = -parseOSCMessage(oscData[5]);
					    var qz : float = parseOSCMessage(oscData[6]);
					    var qw : float = parseOSCMessage(oscData[7]);
			    		var oscObject : objectHandler = objectHolder[oscData[0].ToString()];
			    		oscObject.updateObject([true, Vector3(x, y, z), Quaternion(qx, qy, qz, qw)]);			    		
					break;				
				}
				item.Value.packets[lastPacketIndex].TimeStamp = 1;
			}
  		}	
	}
}

private function parseOSCMessage(data) {
	return float.Parse(data, System.Globalization.CultureInfo.InvariantCulture.NumberFormat);
}

public function oscColliders() {
	OSCHandler.Instance.SendMessageToClient("Sender", "/colliders", colliders.join(","));
}

public function LeavingActionBox() {
	OSCHandler.Instance.SendMessageToClient("Sender", "/leaving_bbox", "_");
}

public function enterBoundinbox(vars: Array){
	var rayCaster : Rayscaster = hand.GetComponent("Rayscaster");
	var message = "";
	for(var each in rayCaster.listOfCol){
		if(each.Value) {
			message += each.Key + ",";
		}		
	}
	if(message != "") {
		message = message.Substring(0, message.Length - 1);
	}		
  	OSCHandler.Instance.SendMessageToClient("Sender", "/enter_boundingbox", message);
}

public function oscCollision(vars: Array) {
  	OSCHandler.Instance.SendMessageToClient("Sender", "/collision", vars.join(","));
}

public function RegisterObject(that: objectHandler) {
  	objectHolder[that.name] = that;  
  	that.gameObject.SetActive(false);
}