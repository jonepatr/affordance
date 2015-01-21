#include <Wire.h>
#include <CapacitiveSensor.h>
//#include <EEPROM.h>
CapacitiveSensor   cs_11_12 = CapacitiveSensor(11,12);
CapacitiveSensor   cs_11_10 = CapacitiveSensor(11,10);


#define LED 13
boolean debug = true;
boolean currentlyActive = false;
int threshold = 2500;

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
  long valueFromSensor =  cs_11_12.capacitiveSensor(30);
  if(valueFromSensor >= threshold && !currentlyActive) {      
    printer("ext_touch=1", true);
    currentlyActive = true;
  } else if (valueFromSensor < threshold && currentlyActive) {
    printer("ext_touch=0", true);
    currentlyActive = false;
  }
  if(currentlyActive) {
    digitalWrite(LED,HIGH);
  } else {
    digitalWrite(LED,LOW);
  }
}



