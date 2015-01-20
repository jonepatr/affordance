using UnityEngine;
using System.Collections;

[System.Serializable]
public class ColliderList
{
    public string name = "";
    public float distance = 0;
    public Vector3 center = new Vector3();
    public Vector3 size = new Vector3();   
}




public class colliders : MonoBehaviour {

    
    
    public ColliderList[] colliderList;
    private GameObject mygameobject;
    
    

    
    
	// Use this for initialization
	void Start () {
        
        
        foreach (ColliderList each in colliderList)
        {
            mygameobject = new GameObject();
            mygameobject.name = gameObject.name + "_" + each.name + "_outer";
            mygameobject.AddComponent("BoxCollider");
            mygameobject.AddComponent("GizmoStuff");
            //mygameobject.SendMessage("SetDistance", each.distance);
            
            BoxCollider bc = mygameobject.collider as BoxCollider;

            bc.size = each.size;
            bc.center = each.center;
            mygameobject.tag = "OuterCollision";
            mygameobject.transform.parent = gameObject.transform;
            mygameobject.transform.localPosition = new Vector3(0,0,0);
            mygameobject.transform.localRotation = Quaternion.identity;
            mygameobject.transform.localScale = new Vector3(1,1,1);
            mygameobject.GetComponent<GizmoStuff>().distance = each.distance;
            //mygameobject.GetComponent<GizmoStuff>().gizmoPosition = new Vector3(bc.transform.position.x + ( bc.center.x + bc.size.x/2 ), bc.transform.position.y + ( bc.center.y + bc.size.y/2 ), bc.transform.position.z + ( bc.center.z + bc.size.z/2 )); 

            
            
            
            
            
        }
        
        
        
	    
	}
	
	// Update is called once per frame
	void Update () {
	
	}
}
