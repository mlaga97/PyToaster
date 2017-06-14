#include "max6675.h"

int thermoDO = 4;
int thermoCS = 5;
int thermoCLK = 6;

MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);

float temperature = 0.0;  // Temperature output variable
float mintemp = 1000.0;
float maxtemp = -1000.0;

float getTemp() {
  temperature = thermocouple.readCelsius();
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
  Serial.begin(115200);
  pinMode(12, OUTPUT);
  delay(500);
  Serial.println("TOAST!");
}

void WaitForSerial( int bytes ) {
  while( Serial.available() < bytes ) {}
}

byte c;
int p1,p2;

void loop() {
  getTemp();

  if(temperature > 50) {
    Serial.println("OFF!");
    digitalWrite(12, LOW);
  } else if(temperature < 50) {
    Serial.println("ON!");
    digitalWrite(12, HIGH);
  }
}

