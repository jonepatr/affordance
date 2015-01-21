#pragma strict

var osc : oscController;
var previousPositions : Array = [];
var previousPosition : Vector3 = Vector3.zero;
var positionOffset : Vector3;
var direction : Vector3;
//  Vector3(0.68, 0.32, 0.48)
public var listOfColliders = {};

function CompareHits(x : RaycastHit, y : RaycastHit) : int {
    return x.distance.CompareTo(y.distance);
}

function Start () {
    osc = GameObject.Find("GameObject").GetComponent(oscController);
}

function changeCol(values : Array) {
	this.listOfColliders = {};
	this.listOfColliders[values[0]] = values[1];
}


function Update () {	
	Debug.DrawRay(gameObject.transform.position+positionOffset, direction * 2, Color.green);	
	previousPositions.Add(gameObject.transform.position - previousPosition);		
	previousPosition = gameObject.transform.position;	
	if(previousPositions.length > 100) {
		previousPositions.Shift();
	}
	
	var number = 0;
	var currentCollider = "";	
	for(var collider in this.listOfColliders) {		
		if(collider.Value) {
			number++;
			currentCollider = each.Key;
		}
	}
	if (number >= 1) {
		var finalVector : Vector3 = Vector3.zero;
		for (var each : Vector3 in previousPositions) {
			finalVector.x += each.x;
			finalVector.y += each.y;
			finalVector.z += each.z;
		}	
		finalVector.x /= previousPositions.length;
		finalVector.y /= previousPositions.length;
		finalVector.z /= previousPositions.length;  
	  	var hits : RaycastHit[];  
	  	Debug.DrawRay(gameObject.transform.position, finalVector.normalized * 10, Color.green);
	  	hits = Physics.RaycastAll(gameObject.transform.position, finalVector.normalized, 10);    
	    if(hits){    
	       	System.Array.Sort(hits, CompareHits);
	       	var affordance_i = 0;
	       	if(hits.Length > 0) {
	       		var hasHitTarget = false;
	       		for(var hit : RaycastHit in hits) {       	
		       		if(hit.collider.gameObject.tag == "HitTarget") {           	             
		             	var offset = 0.20;
		             	hasHitTarget = true;			             			             
		             	//GameObject.Find("arm_model").GetComponent(SkinnedMeshRenderer).material.color = Color((hit.distance-offset*255)/255, 124/255, 10/255);			             	
		             	osc.SendMessage("oscCollision", new Array(currentCol, hit.collider.gameObject.name, (hit.distance-offset)));          
		             	break;
		           	}
	       		}
	        	if(!hasHitTarget) {	  
	        		osc.SendMessage("oscCollision", new Array(currentCol, "no_target", 999999)); 
	        	}
	       	} 
	    } else {
	    	osc.SendMessage("oscCollision", new Array(currentCol, "no_target", 999999)); 
	    }
	} else {
		osc.SendMessage("oscCollision", new Array("nothing", "no_target", 999999)); 
	
	}
}