#pragma strict

private var osc: oscController;
public var collisionColor: Color = Color.red;
public var hh : Rayscaster;
var arm_model : GameObject;

function Awake () {
  	osc = GameObject.Find("GameObject").GetComponent(oscController); 
  	arm_model = GameObject.Find("arm_model"); 	
}

function OnTriggerEnter(other: Collider) {			
	
   	if (other.gameObject.name == "screw_hole") {
   		osc.SendMessage("extraInfo", new Array("screw_driver", true));
   		Debug.Log("ho");
   	} else if (this.gameObject.name != "screw_hole" && hh && this.gameObject){
   		Debug.Log(this.gameObject.name);
   		arm_model.GetComponent(SkinnedMeshRenderer).material.color = collisionColor;   		   	
   		hh.SendMessage("changeCol", new Array(this.gameObject.name, true));
   	}
   	//GameObject.Find("bounding_box_stop").SetActive(true);
   	//GameObject.Find("bounding_box_stop").transform.position = other.gameObject.transform.position;
}

function OnTriggerExit(other: Collider) { 
if (other.gameObject.name == "screw_hole" || this.gameObject.name == "screw_hole") {
   		osc.SendMessage("extraInfo", new Array("screw_driver", false));
   	} else if (this.gameObject.name != "screw_hole" && hh) {
   		hh.SendMessage("changeCol", new Array(this.gameObject.name, false)); 
   		arm_model.GetComponent(SkinnedMeshRenderer).material.color = Color.green;   		   		
   	}
}