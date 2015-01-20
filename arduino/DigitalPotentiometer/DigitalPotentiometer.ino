//pins from digital potenciometer, according to INTERSIL 3-wire PROTOCOL
#define CS_1 2
#define UD_1 3
#define INC_1 4
#define RELAY_1 5

#define CS_2 6
#define UD_2 7
#define INC_2 8
#define RELAY_2 9

#define CS_3 10
#define UD_3 11
#define INC_3 12
#define RELAY_3 14

#define CS_4 15
#define UD_4 16
#define INC_4 17
#define RELAY_4 18

#define LED 13

#define NUMBER_OF_CHANNELS 4

int serIn;
int delta = 1; //do not change
boolean debug = false;
byte potPos[] = {0, 0, 0, 0};
byte wantedPosition[] = {100, 100, 100, 100};
int channelPrefix[] = {1000, 2000, 3000, 4000};
boolean changed[] = {true, true, true, true};

byte cs[] = {CS_1, CS_2, CS_3, CS_4};
byte ud[] = {UD_1, UD_2, UD_3, UD_4};
byte inc[] = {INC_1, INC_2, INC_3, INC_4};
byte relays[] = {RELAY_1, RELAY_2, RELAY_3, RELAY_4};

void printer(String msg, boolean force = false) {
  if (debug || force) {
    Serial.println(msg);
  }
}


void resetP() {
  for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
    digitalWrite(inc[i], HIGH); //INC Change from high to low
    digitalWrite(cs[i], LOW); //UD Hight increase / Low decrease
    digitalWrite(ud[i], HIGH); // CD High hold value/ Low cange is possible
  }
  
  for (int i = 0; i <= 100; i++) {
    for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
      digitalWrite(inc[i], HIGH); //INC Change from high to low
      delay(delta);
      digitalWrite(inc[i], LOW);    // sets the pin off
      delay(delta);
      printer("reset"); 
    }
  }
  digitalWrite(inc[i], HIGH);
  digitalWrite(cs[i], HIGH);
  printer("\n");
  delay(20);
  for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
    potPos[i] = 100;
  }
}

void openRelay(byte channel) {
  printer("Open relay");
  digitalWrite(relays[channel], HIGH); 
}

void closeRelay(byte channel) {
  printer("Close relay!");
  digitalWrite(relays[channel], LOW);
}

void go(byte channel, String direction) {
  digitalWrite(cs[channel],LOW);
  digitalWrite(inc[channel],HIGH);
  if(direction == "up") {
    digitalWrite(ud[channel],HIGH);
  } else {
    digitalWrite(ud[channel],LOW);
  }
  delay(delta);
  digitalWrite(inc[channel],LOW);
  delay(delta);
  printer(" " + direction + " ");
}

void setWantedPosition(byte channel, byte pos) {
  wantedPosition[channel] = pos;
  changed[channel] = true;
}

void setup(void){
  for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
    pinMode(cs[i], OUTPUT);
    pinMode(ud[i], OUTPUT);
    pinMode(inc[i], OUTPUT);
    pinMode(relays[i], OUTPUT);
    digitalWrite(relays[i], LOW);
  }
  pinMode(LED, OUTPUT);
  Serial.begin(19200);
  printer("Initial pot positions: " + String(potPos[0]) + ", " + String(potPos[1]) + ", " + String(potPos[2]));
}

void loop(void){
  while (Serial.available()>0){
    serIn = Serial.read();
    printer(String(serIn) + "\n Pot last pos " + String(potPos[0]) + ", " + String(potPos[1]) + ", " + String(potPos[2]));
    switch (char(serIn)) {
    case '0':
      for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
        setWantedPosition(i, 100);  
      }     
      break;
    case 's':
      for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
        setWantedPosition(i, 100);  
        closeRelay(i);
      }        
      break;
    case 'd':
      debug = !debug;
      printer(String(debug));
      break;
    case 'o':
      openRelay(0);
      break;
    case 'p':
      closeRelay(0);
      break;
     case 'k':
      openRelay(1);
      break;
    case 'l':
      closeRelay(1);
      break;
    case 'r':
      resetP();
      break;
    case '$':      
      byte channel = 0;
      int tmpVal = Serial.parseInt();
      int intValue = 0;
      for (byte i = 0; i < NUMBER_OF_CHANNELS; i++) {
        if (tmpVal >= channelPrefix[i]) {
           channel = i;
           intValue = tmpVal - channelPrefix[i];
         }
      }            
      printer("intValue: " + String(intValue));      
      int newValue = intValue;
      printer("newValue: " + String(newValue));
      if (newValue > 0 && newValue <= 100) {        
        setWantedPosition(channel, newValue);
      }      
      break;      
    }
  }
  for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
    if(potPos[i] < wantedPosition[i]) {
      go(i, "up");
      potPos[i]++;
    } else if(potPos[i] > wantedPosition[i]) {
      go(i, "down");
      potPos[i]--;
    } else if(potPos[i] == wantedPosition[i] && changed[i]) {
      changed[i] = false;    
    } else if(potPos[i] == wantedPosition[i] && !changed[i]) {
      long start = millis();
    }
  }
}



