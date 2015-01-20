//#pragma strict
// var door : GameObject;
// var doorHandle : GameObject;
// var hand : GameObject;
// var knife : GameObject;
//
//
// function CreateObject(name, vertices, triangles, color, boundingBox : Array){
//   var obj : GameObject = new GameObject(name);
//   obj.transform.position = Vector3(0,0,0);
//   obj.AddComponent("MeshFilter");
//   obj.AddComponent("MeshRenderer");
//   var mesh : Mesh = obj.GetComponent(MeshFilter).mesh;
//   mesh.Clear();
//   mesh.vertices = vertices;
//   mesh.triangles = triangles;
//   obj.AddComponent("Rigidbody");
//   obj.rigidbody.useGravity = false;
//   obj.rigidbody.isKinematic = true;
//   var meshRenderer = obj.GetComponent(MeshRenderer);
//   meshRenderer.material.color = color;
//
//
//   var objMeshCollider : MeshCollider = obj.AddComponent("MeshCollider");
//   objMeshCollider.isTrigger = true;
//
//
//   var objBoxCollider : BoxCollider = obj.AddComponent("BoxCollider");
//   objBoxCollider.isTrigger = true;
//
//   var i = 0;
//   for (each in boundingBox) {
//     if (!each) {
//       if (i < 3) {
//         each = objBoxCollider.size[i];
//       } else {
//         each = objBoxCollider.center[i%3];
//       }
//     }
//     i++;
//   }
//
//   objBoxCollider.size = Vector3(boundingBox[0], boundingBox[1], boundingBox[2]);
//   objBoxCollider.center = Vector3( boundingBox[3], boundingBox[4], boundingBox[5]);
//
//
//
//   return obj;
// }

  //Application.runInBackground = true
  //var door : GameObject;
  //boxCollider.center = Vector3(0.26, boxCollider.center[1], boxCollider.center[2]);
  //boxCollider.size = Vector3(0.5, boxCollider.size[1], boxCollider.size[2]);

  //
  // var knifeWidth = 0.33;
  // var knifeHeight = 0.02;
  // var knifeThickness = 0.04;
  //
  // var knife_startpoint_z = 0;
  // var knife_startpoint_x = 0;
  // var knife_startpoint_y = 0;
  //
  // var knifeVertices = [ Vector3(knife_startpoint_x,knife_startpoint_y,knife_startpoint_z), Vector3(knife_startpoint_x,knife_startpoint_y,knifeWidth), Vector3(knifeThickness, knife_startpoint_y,knifeWidth), Vector3(knifeThickness, knife_startpoint_y, knife_startpoint_z), Vector3(knife_startpoint_x, knifeHeight, knife_startpoint_z), Vector3(knife_startpoint_x, knifeHeight, knifeWidth), Vector3(knifeThickness, knifeHeight, knifeWidth), Vector3(knifeThickness, knifeHeight, knife_startpoint_z)];
  // var knifeTriangles = [0, 3, 2, 0, 2, 1, 4, 6, 7, 4, 5, 6, 0, 5, 4, 0, 1, 5, 1, 6, 5, 1, 2, 6, 2, 7, 6, 2, 3, 7, 3, 4, 7, 3, 0, 4];
  //
  //
  //
  //   var startpoint_y = 0.04;
  //   var startpoint_z = -0.2530;
  //   var startpoint_x = -0.0336;
  //   var width : float = 0.54;
  //   var thickness : float = 0.01;
  //   var height : float = 0.42;
  //
  //   var doorVertices = [ Vector3(startpoint_x,startpoint_y,startpoint_z), Vector3(startpoint_x,startpoint_y,width), Vector3(thickness, startpoint_y,width), Vector3(thickness, startpoint_y, startpoint_z), Vector3(startpoint_x, height, startpoint_z), Vector3(startpoint_x, height, width), Vector3(thickness, height, width), Vector3(thickness, height, startpoint_z)];
  //   var doorTriangles = [ 0, 3, 2, 0, 2, 1, 4, 6, 7, 4, 5, 6, 0, 5, 4, 0, 1, 5, 1, 6, 5, 1, 2, 6, 2, 7, 6, 2, 3, 7, 3, 4, 7, 3, 0, 4];
  //
  //
  //
  //
  //
  //   var max_length = 0.25;
  //   var max_width = 0.09;
  //   var max_height = 0.05;
  //
  //   var start_x = -max_length/2;
  //   var start_y = -max_height/2;
  //   var start_z = -max_width/2;
  //
  //   var arm_width : float = 0.06;
  //   var palm_width : float = 0.09;
  //   var palm_arm_width : float = (palm_width-arm_width)/2;
  //   var palm_length : float = 0.12;
  //   var arm_length : float = 0.25;
  //
  //   var arm_height : float = start_y + max_height;
  //
  //
  //   var handVertices = [ Vector3(start_x,start_y,start_z), Vector3(start_x + palm_length,start_y,start_z), Vector3(start_x + palm_length,start_y,start_z + palm_arm_width), Vector3(start_x + arm_length,start_y,start_z + palm_arm_width), Vector3(start_x + arm_length,start_y,start_z + arm_width + palm_arm_width), Vector3(start_x + palm_length,start_y,start_z + arm_width + palm_arm_width), Vector3(start_x + palm_length,start_y,start_z + palm_width), Vector3(start_x,start_y,start_z + palm_width), Vector3(start_x,arm_height,start_z), Vector3(start_x + palm_length,arm_height,start_z), Vector3(start_x + palm_length,arm_height,start_z + palm_arm_width), Vector3(start_x + arm_length,arm_height,start_z + palm_arm_width), Vector3(start_x + arm_length,arm_height,start_z + arm_width + palm_arm_width), Vector3(start_x + palm_length,arm_height,start_z + arm_width + palm_arm_width), Vector3(start_x + palm_length,arm_height,start_z + palm_width), Vector3(start_x,arm_height,start_z + palm_width)];
  //   var handTriangles = [ 7, 0, 1, 7, 1, 6, 15, 9, 8, 15, 14, 9, 5, 2, 3, 5, 3, 4, 13, 11, 10, 13, 12, 11, 15, 7, 6, 15, 6, 14, 14, 6, 5, 14, 5, 13, 13, 5, 4, 13, 4, 12, 12, 4, 3, 12, 3, 11, 11, 3, 2, 11, 2, 10, 10, 2, 1, 10, 1, 9, 9, 1, 0, 9, 0, 8, 8, 0, 7, 8, 7, 15 ];
  //
  //


  //var door  = CreateObject("door", doorVertices, doorTriangles, Color.black, [0.5, null, null, 0.26, null, null]);
  //door = GameObject.Find("/door");
  //door.SetActive(false);
  
  //doorHandle = GameObject.Find("/door_handle");
  //doorHandle.SetActive(false);
  
  //knife = GameObject.Find("/knife");
  //knife.SetActive(false);
  
  // var hand : GameObject = GameObject.Find("/hand");
  // var door : GameObject = GameObject.Find("/door");
  // var door_handle : GameObject = GameObject.Find("/door_handle");
  // var knife : GameObject = GameObject.Find("/knife");
  // var power_outlet : GameObject = GameObject.Find("/power_outlet");
  // var spray_can : GameObject = GameObject.Find("/spray_can");
  //
  // door.SetActive(false);
  // door_handle.SetActive(false);
  // knife.SetActive(false);
  // power_outlet.SetActive(false);
  // spray_can.SetActive(false);
  
  //hand  = CreateObject("hand", handVertices, handTriangles, Color.green, [max_length, max_height, max_width, null, null, null]);

   
    //    0.16
//    0.482279
//    0.225425
//    
//    0.3
//    0.964558
//    0.45085

    

   // door.AddComponent("collisionForDoor");
    
    

// }


