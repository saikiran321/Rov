#define portOfPin(P)\
  (((P)>=0&&(P)<8)?&PORTD:(((P)>7&&(P)<14)?&PORTB:&PORTC))
#define ddrOfPin(P)\
  (((P)>=0&&(P)<8)?&DDRD:(((P)>7&&(P)<14)?&DDRB:&DDRC))
#define pinOfPin(P)\
  (((P)>=0&&(P)<8)?&PIND:(((P)>7&&(P)<14)?&PINB:&PINC))
#define pinIndex(P)((uint8_t)(P>13?P-14:P&7))
#define pinMask(P)((uint8_t)(1<<pinIndex(P)))

#define pinAsInput(P) *(ddrOfPin(P))&=~pinMask(P)
#define pinAsInputPullUp(P) *(ddrOfPin(P))&=~pinMask(P);digitalHigh(P)
#define pinAsOutput(P) *(ddrOfPin(P))|=pinMask(P)
#define digitalLow(P) *(portOfPin(P))&=~pinMask(P)
#define digitalHigh(P) *(portOfPin(P))|=pinMask(P)
#define isHigh(P)((*(pinOfPin(P))& pinMask(P))>0)
#define isLow(P)((*(pinOfPin(P))& pinMask(P))==0)
#define digitalState(P)((uint8_t)isHigh(P))

#include <Encoder.h>
#include <Wire.h>
#include "MS5837.h"

MS5837 sensor;

Encoder EnR(2, 5);
Encoder EnL(3, 11);  

int M1BRK = 7;
int M1Dir = 8;
int M1PWM = 9;

int M2BRK = 4;
int M2Dir = 13;
int M2PWM = 6;

int TAILPWM=10;
int TAILBRK=12;
int TAILDIR=A7;

int inptail=0;  //input speed of tail from serial read
int inpen=0;   //target value for encoder received from serial read - assuming both encoders are same angles

int inp;
int count = 0;
int CsValue=0;         //Current sensor
float AcsValue = 0.0;  //Average current sensor value
int analogInput = A1;  //Voltage sensor
int VsValue = 0;       //Voltage sensor value
float AvsValue = 0.0;  //Average voltage value
int pres=0,temp=0;
float Apres=0,Atemp=0;
long output;           //Cs and Vs values sent to python PC
int AnalogInPin=A0;  //Current sensor

void setup() { 

  Serial.begin(38400);
  
  pinMode(analogInput, INPUT);
  pinMode(AnalogInPin,INPUT);

  Serial.println("Starting");
  Wire.begin();
  sensor.init();
  sensor.setFluidDensity(997); // kg/m^3 (freshwater, 1029 for seawater)

  pinMode(M1BRK,OUTPUT);
  pinMode(M1Dir,OUTPUT);
  pinMode(M1PWM,OUTPUT);
  
  pinMode(M2BRK,OUTPUT);
  pinMode(M2Dir,OUTPUT);
  pinMode(M2PWM,OUTPUT);
  
  pinMode(TAILBRK,OUTPUT);
  pinMode(TAILDIR,OUTPUT);
  pinMode(TAILPWM,OUTPUT);
  
  analogWrite(M1PWM,0);
  analogWrite(M2PWM,0);
} 

void loop(){

  long EnR_Pos = EnR.read();
  long EnL_Pos = EnL.read();
  
  //VOLTAGE SENSOR    
  // read the value at analog input
  VsValue = analogRead(analogInput);

  
  //CURRENT SENSOR
  //Read current sensor values   
  CsValue = analogRead(AnalogInPin);  
  AcsValue = AcsValue + CsValue;
  AvsValue = AvsValue + VsValue;

  //DEPTH SENSOR
  sensor.read();
 
   
  pres=sensor.pressure();
  Apres=Apres+pres;
   
  temp=sensor.temperature(); 
  Atemp=Atemp+temp;
  
  //SERIAL INPUT
  if (Serial.available())  
  {
       inp = Serial.read();   // first digit for tail motor
       inp = inp - '0' ;      // next three digits for en
       inptail=inp/1000;
       inp=inp%1000;
       inpen=inp;
   

  //TAIL MOTOR
  inptail = inptail * 28; //28*9  = 252  -- change factor if required
  if (inptail>0)
  {
    digitalHigh(TAILDIR);
    digitalLow(TAILBRK);
    analogWrite(TAILPWM,inptail);
  }

//ENCODER MOTOR LEFT
  while(abs(EnR_Pos) - abs(inpen))
  {
      analogWrite(M1PWM,100);
      

    if (EnR_Pos < inpen )
    {
      digitalLow(M1BRK);
      digitalHigh(M1Dir);  //change according to direction
    }
    else if (EnR_Pos > inpen)
    {
      digitalLow(M1BRK);
      digitalLow(M1Dir);  //change according to direction
    }
    long EnR_Pos = EnR.read();
   }
   digitalHigh(M1BRK);

  
//ENCODER MOTOR RIGHT
//digitalWrite(A2, HIGH);       // turn on pullup resistor

  while(abs(EnL_Pos) - abs(inpen))
  { 
    analogWrite(M2PWM,100);
    if (EnL_Pos < inpen )
    {
      digitalLow(M2BRK);
      digitalLow(M2Dir);   //Change direction - opp to M1
    }
    else if (EnL_Pos > inpen)
    {
      digitalLow(M2BRK);
      digitalHigh(M2Dir);   //Change direction - opp to M2
    }
    
    long EnL_Pos = EnL.read();
   }
   digitalHigh(M2BRK);
  } 
   // send serial data to PC - current sensor and voltage sensor
  count = count + 1;
  if (count == 100)
  {
    count = 0;
    AcsValue = AcsValue/100;
    AvsValue = AvsValue/100;
    Apres=Apres/100;
    Atemp=Atemp/100;
    
    Serial.print(AcsValue);
    Serial.print("\t");
    Serial.print(AvsValue);
    Serial.print("\t");
    Serial.print(Apres);
    Serial.print("\t");
    Serial.println(Atemp);
        
    AcsValue = 0;
    AvsValue = 0;
    Atemp=0;
    Apres=0; 
   }
  }   
  

