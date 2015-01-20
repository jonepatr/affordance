#pragma strict

import System.Collections.Generic;

var objectHolder = {};
var colliders : Array = [];
var servers = new Dictionary.<String, ServerLog>();
var lastCol : String = "";
public var bbox_stuff : GameObject;
public var arm_model : GameObject;
public var hand : GameObject;

function Awake () {
	OSCHandler.Instance.Init();
  	var cols : Array = GameObject.FindGameObjectsWithTag ("CollisionField");
  	for(var each : GameObject in cols) {
    	colliders.push(each.name);
  	}
  	oscColliders();
  	arm_model = GameObject.Find("arm_model");
}

function FixedUpdate() {
  	OSCHandler.Instance.UpdateLogs();  
  	servers = OSCHandler.Instance.Servers;
	for (item in servers) {	
		if(item.Value.packets.Count > 0) {		
			var lastPacketIndex = item.Value.packets.Count - 1;
			if (item.Value.packets[lastPacketIndex].TimeStamp == 0) {			
				switch(item.Value.packets[lastPacketIndex].Address){					
					case '/done_shaking':
						if(arm_model) {
							arm_model.GetComponent(SkinnedMeshRenderer).material.color = Color.green;						
						}
						
					break;
					case '/init_bbox':
						
						arm_model.GetComponent(SkinnedMeshRenderer).material.color = Color.red;						
												
						var stopping : StoppingBoundingBox = bbox_stuff.GetComponent("StoppingBoundingBox");						
						stopping.SendMessage("setOn", true);
						bbox_stuff.transform.position = hand.transform.position;
						
						
					break;
					case '/askForColliders':
						oscColliders();
					break;
					case '/positionUpdate':						
						var oscData = item.Value.packets[lastPacketIndex].Data;
						var x : float = float.Parse(oscData[1], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);				
					    var y : float = float.Parse(oscData[2], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);
					    var z : float = -float.Parse(oscData[3], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);					  
					    var qx : float = -float.Parse(oscData[4], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);
					    var qy : float = -float.Parse(oscData[5], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);
					    var qz : float = float.Parse(oscData[6], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);
					    var qw : float = float.Parse(oscData[7], System.Globalization.CultureInfo.InvariantCulture.NumberFormat);   			
			    		var oscObject : collisionForDoor = objectHolder[oscData[0].ToString()];
			    		oscObject.changeStuffs([true, Vector3(x, y, z), Quaternion(qx, qy, qz, qw)]);			    		
					break;				
				}
				item.Value.packets[lastPacketIndex].TimeStamp = 1;
			}
  		}	
	}
}

public function oscColliders() {
	OSCHandler.Instance.SendMessageToClient("Sender", "/colliders", colliders.join(","));
}

public function extraInfo(vars: Array) {
	OSCHandler.Instance.SendMessageToClient("Sender", "/extra_info", vars.join(","));
}

public function LeavingActionBox() {
Debug.Log("leave");
	OSCHandler.Instance.SendMessageToClient("Sender", "/leaving_bbox", "_");
}

public function enterBoundinbox(vars: Array){
	var a : Rayscaster = GameObject.Find("arm").GetComponent("Rayscaster");
	var q = "";
	for(var each in a.listOfCol){
		if(each.Value) {
			q += each.Key + ",";
		}		
	}
	if(q != "") {
		q = q.Substring(0,q.Length-1);
	}	
	
  	OSCHandler.Instance.SendMessageToClient("Sender", "/enter_boundingbox", q);
}

public function oscCollision(vars: Array) {
  	OSCHandler.Instance.SendMessageToClient("Sender", "/collision", vars.join(","));
}

public function RegisterObject(that: collisionForDoor) {
  	objectHolder[that.name] = that;  
  	that.gameObject.SetActive(false);
}