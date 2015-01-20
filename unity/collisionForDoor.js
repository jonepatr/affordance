#pragma strict

private var osc: oscController;
private var angle = Quaternion.identity;
private var position = Vector3(0, 0, 0);
private var timesSinceUpdate = 1000;
public var controlPositions = false;

function Start() {
	osc = GameObject.Find("GameObject").GetComponent(oscController);
  	osc.SendMessage("RegisterObject", this);  
}

function changeStuffs(stuffs: Array) {  
	var change1 : boolean = stuffs[0];
	var change2 : Vector3 = stuffs[1];
	var change3 : Quaternion = stuffs[2];
	gameObject.SetActive(change1);
	position = change2;
	angle = change3;
	timesSinceUpdate = 0;
}

function disableColliders () {	
	var hand_stuff : GameObject = GameObject.Find("arm");
	if(hand_stuff) {
		var hh : Rayscaster = hand_stuff.GetComponent("Rayscaster");
		for(var each : GameObject in this.gameObject.FindGameObjectsWithTag("OuterCollision")) {							
   			hh.listOfCol[each.name] = false;		
		}	
		var isOneTrue = false;
		for (var each in hh.listOfCol) {
			if(each.Value == true) {
				isOneTrue = true;
			}
		}
		if(!isOneTrue) {
			var arm_model = GameObject.Find("arm_model");
   			if (arm_model) {
   				arm_model.GetComponent(SkinnedMeshRenderer).material.color = Color.green;
   			}   
		}
	}
}

function Update() {
	if (controlPositions) {
    	if (timesSinceUpdate > 200 && gameObject.activeSelf) {
    		//this.disableColliders();    	
      		gameObject.SetActive(false);    
    	}
      	gameObject.transform.position = position;	
      	gameObject.transform.rotation = angle;     
    	timesSinceUpdate++;
  	}  
}
