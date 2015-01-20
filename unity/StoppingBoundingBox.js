#pragma strict
private var osc: oscController;
public var on : boolean = false;
var arm : GameObject;
function Start () {
	osc = GameObject.Find("GameObject").GetComponent(oscController);  
	//GameObject.Find("bounding_box_stop").SetActive(false);
	arm = GameObject.Find("arm_model");
}

function setOn(state : boolean) {
on = true;
}

function OnTriggerExit(other: Collider) { 
if (on) {
Debug.Log("left");
	osc.SendMessage("LeavingActionBox");
	if(arm) {
		arm.GetComponent(SkinnedMeshRenderer).material.color = Color.green;			
	}
	on = false;
}
	
	
	//GameObject.Find("bounding_box_stop").SetActive(false);
}