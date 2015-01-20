using UnityEngine;
using System.Collections;

public class GizmoStuff : MonoBehaviour {
    public float distance = 0;
    public Vector3 gizmoPosition = new Vector3 (0,0,0);
    
    public void SetDistance(float dist){
        distance = dist;
    }
    
    void OnDrawGizmos() {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(gizmoPosition, distance);
    }
}