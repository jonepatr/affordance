#include <Wire.h>
#include <CapacitiveSensor.h>
//#include <EEPROM.h>
CapacitiveSensor   cs_11_12 = CapacitiveSensor(11,12);
CapacitiveSensor   cs_11_10 = CapacitiveSensor(11,10);
//CapacitiveSensor   cs_11_9 = CapacitiveSensor(11,9);
//CapacitiveSensor   cs_11_8 = CapacitiveSensor(11,8);


#define LED 13

boolean debug = true;


boolean touchedSprayCan = false;
boolean touchedDoorHandle = false;
boolean touchedPowerCord = false;
boolean ScrewIsIn = false;
void printer(String msg, boolean force = false) {
  if (debug || force) {
    Serial.println(msg);
  } 
}




void setup(void){
  pinMode(LED, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(4, INPUT);
  digitalWrite(2,HIGH);
  Serial.begin(19200);    
}


void loop(void){
  long total1 =  cs_11_12.capacitiveSensor(30);
    long total2 =      cs_11_10.capacitiveSensor(30);

  //printer(String(total2));

  //long total2 =  cs_11_9.capacitiveSensor(30);
  //long total3 =  cs_11_9.capacitiveSensor(30);
  //Serial.println(total1);
  //printer(total2);
  //printer(total3);
    
//    if(total1>2000 &&  !touchedDoorHandle) {
//      printer("t", true);     
//      touchedDoorHandle = true; 
//    } else if (total1<2000 && t;ouchedDoorHandle) {
//      printer("r", true);
//      touchedDoorHandle = false;
//    }
  //printer(String(total1));
  if(total2>2500 && !touchedSprayCan) {      
    
    //printer("z", true);
    //touchedSprayCan = true;
  } else if (total2<2500 && touchedSprayCan) {
    //printer("x", true);
    //touchedSprayCan = false;
  }
  
  if(total1>2500 && !touchedDoorHandle) {      
    printer("a", true);
    touchedDoorHandle = true;
  } else if (total1<2500 && touchedDoorHandle) {
    printer("w", true);
    touchedDoorHandle = false;
  }
  
//  
//  int val = digitalRead(4);
//  //Serial.println(val);
//  if(val == HIGH && ScrewIsIn == false) {
//    ScrewIsIn = true;
//    printer("g", true);
//  } else if (val == LOW && ScrewIsIn == true){
//    ScrewIsIn = false;
//    printer("h", true);
//  }
  
// 
//    if(total3>400 && !touchedPowerCord) {      
//      printer("u", true);
//      touchedPowerCord = true;
//    } else if (total3<1500 && touchedPowerCord) {
//      printer("i", true);
//      touchedPowerCord = false;
//    }
//       
//    
  if(touchedSprayCan || touchedDoorHandle || touchedPowerCord || ScrewIsIn) {
    digitalWrite(LED,HIGH);
  } else {
    digitalWrite(LED,LOW);
  }

}



