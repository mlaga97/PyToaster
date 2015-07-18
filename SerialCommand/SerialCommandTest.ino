#include <MAX6675.h>

int CS = 53;             // CS pin on MAX6675
int SO = 50;              // SO pin of MAX6675
int units = 1;            // Units to readout temp (0 = raw, 1 = ˚C, 2 = ˚F)
float temperature = 0.0;  // Temperature output variable
float mintemp = 1000.0;
float maxtemp = -1000.0;

// Initialize the MAX6675 Library for our chip
MAX6675 temp(CS,SO,SCK,units);

float getTemp() {
  temperature = temp.read_temp();
  if( temperature > maxtemp ) {
    maxtemp = temperature;
  }
  if( temperature < mintemp ) {
    mintemp = temperature;
  }
  
  Serial.print("Current Temperature: ");
  Serial.print( temperature );
  Serial.print("; Minimum Temperature: ");
  Serial.print( mintemp );
  Serial.print("; Maximum Temperature: ");
  Serial.println( maxtemp );
  
  delay( 250 );
  return temperature;
}





void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(100);
  Serial.println("TOAST!");
  //pinMode(13,OUTPUT);
}

void WaitForSerial( int bytes ) {
  while( Serial.available() < bytes ) {}
}

byte c;
int p1,p2;

void loop() {  
  WaitForSerial(1);
  c = Serial.read();
  
  switch(c) {
    case 0: // For flushing
      break;
    case 109: // 'm': Mode
      WaitForSerial(2);
      p1 = Serial.read();
      p2 = Serial.read();
      pinMode( p1, p2 );
      break;
    case 116: // 't': Temperature
      Serial.println(temp.read_temp());
      break;
    case 119: // 'w': Write
      WaitForSerial(2);
      p1 = Serial.read();
      p2 = Serial.read();
      digitalWrite( p1, p2 );
      break;
    default:
      Serial.print("Unknown opcode: ");
      Serial.println(c);
  }
}

