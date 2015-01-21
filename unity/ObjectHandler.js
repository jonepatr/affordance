#pragma strict

private var osc: oscController;
private var angle = Quaternion.identity;
private var position = Vector3(0, 0, 0);
private var frameCounter = 1000;
public var controlPositions = false;
public var arm : GameObject;
public var rayCaster : GameObject;
public var armModel : GameObject;

function Start() {
	osc = GameObject.Find("GameObject").GetComponent(oscController);
  	osc.SendMessage("RegisterObject", this);  
  	arm = GameObject.Find("arm");
  	armModel = GameObject.Find("arm_model");
  	rayCaster = arm.GetComponent("Rayscaster");  	
}

function updateObject(objectData: Array) {  
	var tmpState : boolean = objectData[0];
	var tmpPosition : Vector3 = objectData[1];
	var tmpAngle : Quaternion = objectData[2];
	gameObject.SetActive(tmpState);
	position = tmpPosition;
	angle = tmpAngle;
	frameCounter = 0;
}

function disableColliders () {	
	if(arm) {		
		for(var each : GameObject in this.gameObject.FindGameObjectsWithTag("OuterCollision")) {							
   			rayCaster.listOfColliders[each.name] = false;		
		}	
		var isOneTrue = false;
		for (var each in rayCaster.listOfColliders) {
			if(each.Value == true) {
				isOneTrue = true;
			}
		}
		if(!isOneTrue) {			
   			if (armModel) {
   				armModel.GetComponent(SkinnedMeshRenderer).material.color = Color.green;
   			}   
		}
	}
}

function Update() {
	if (controlPositions) {
    	if (frameCounter > 200 && gameObject.activeSelf) {    		 	
      		gameObject.SetActive(false);    
    	}
      	gameObject.transform.position = position;	
      	gameObject.transform.rotation = angle;     
    	frameCounter++;
  	}  
}
