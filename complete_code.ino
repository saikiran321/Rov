/* read a rotary encoder with interrupts
   Encoder hooked up with common to GROUND,
   encoder0PinA to pin 2, encoder0PinB to pin 4 (or pin 3 see below)
   it doesn't matter which encoder pin you use for A or B  

   uses Arduino pullups on A & B channel outputs
   turning on the pullups saves having to hook up resistors 
   to the A & B channel outputs 

*/ 
#include <Servo.h>
#define encoder0PinA  2
#define encoder0PinB  A2
#define encoder1PinA  3
#define encoder1PinB  A6

volatile unsigned int encoder0PosL = 0;
volatile unsigned int encoder0PosR = 0;

int setPos = 720;
int M1BRK = 7;
int M1Dir = 8;
int M1PWM = 9;

int M2BRK = 4;
int M2Dir = 13;
int M2PWM = 6;

int TAILPWM=10;
int TAILBRK=12;
int TAILDIR=A7;

int inptail=0;
int inpenr=0;
int inpenl=0;
int inptr=0;
int inptl=0;

byte servoPin = 3;
Servo servo;
int inp;
int signal = 0;
int signal_p = 0;
int count = 0;
float AcsValue=0.0,Samples=0.0,AvgAcs=0.0,AcsValueF=0.0;

int analogInput = A1;
float vout = 0.0;
float vin = 0.0;
//float R1 = 30000.0; //
//float R2 = 7500.0; //
int value = 0;

int AnalogInPin=A0;

void setup() { 

  Serial.begin(9600);
  
  pinMode(analogInput, INPUT);
  //Serial.print("DC VOLTMETER");

  pinMode(AnalogInPin,INPUT);

  pinMode(M1BRK,OUTPUT);
  pinMode(M1Dir,OUTPUT);
  pinMode(M1PWM,OUTPUT);
  
  pinMode(M2BRK,OUTPUT);
  pinMode(M2Dir,OUTPUT);
  pinMode(M2PWM,OUTPUT);
  
  pinMode(TAILBRK,OUTPUT);
  pinMode(TAILDIR,OUTPUT);
  pinMode(TAILPWM,OUTPUT);
  
  pinMode(encoder0PinA, INPUT); 
  digitalWrite(encoder0PinA, HIGH);       // turn on pullup resistor
  pinMode(encoder0PinB, INPUT); 
  digitalWrite(encoder0PinB, HIGH);       // turn on pullup resistor

  attachInterrupt(0, doEncoderL, CHANGE);  // encoder pin on interrupt 0 - pin 2
  attachInterrupt(1, doEncoderR, CHANGE);  // encoder pin on interrupt 0 - pin 2

 
  Serial.println("start");                // a personal quirk
  servo.attach(servoPin);
  servo.writeMicroseconds(1500); // send "stop" signal to ESC.
  delay(1000); // delay to allow the ESC to recognize the stopped signal

} 

void loop(){
  //VOLTAGE SENSOR    
  // read the value at analog input
  float offsetV=0.0;
  value = analogRead(analogInput);
  vout = (value * 5.0) / 1023.0; // see text
  vout=vout-offsetV;
  vin = vout * 5;

  Serial.print("INPUT V= ");
  Serial.println(vout, 2);

  delay(500);


  //CURRENT SENSOR
  unsigned int x=0;

count = count + 1;

  AcsValue = analogRead(AnalogInPin);     //Read current sensor values   
  Samples = Samples + AcsValue;  //Add samples together
  
  if  (count == 150){ //Get 150 samples
  count =0;
  AvgAcs=Samples/150.0;//Taking Average of Sample
  //AcsValueF = ((AvgAcs * (5.0 / 1024.0)) - 2.5 )/0.185;
  AcsValueF = 0.0264*(AvgAcs - 512);
  
  Serial.println(AcsValueF,2);//Print the read current on Serial monitor
  Serial.println(AvgAcs,2);//Print the read current on Serial monitor
  delay (3); // let ADC settle before next sample 3ms
  Samples=0;
}

//((AvgAcs * (5.0 / 1024.0)) is converitng the read voltage in 0-5 volts
//2.5 is offset(I assumed that arduino is working on 5v so the viout at no current comes
//out to be 2.5 which is out offset. If your arduino is working on different voltage than 
//you must change the offset according to the input voltage)
//0.100v(100mV) is rise in output voltage when 1A current flows at input
delay(50);

//SERIAL INPUT
  if (Serial.available())  
  {
       inp = Serial.read();
       inp = inp - '0' ;
        //signal = map(int((inp.charAt(1)-'0')*100+(inp.charAt(2)-'0')*10+(inp.charAt(3))-'0'),0,255,1500,1900);
           //Serial.write(signal);
        //signal=int(signal/100)*100;
        int inptail=inp/10000;
        inp=inp%10000;
        int inper=inp/1000;
        inp=inp%1000;
        int inpel=inp/100;
        inp=inp%100;
        int inptr=inp/10;
        int inptl=inp%10;
        inptail=map(inptail,0,9,0,255);
   }

   //TAIL MOTOR
  if (inptail>0)
  {
    digitalWrite(TAILDIR,HIGH);
    digitalWrite(TAILBRK,LOW);
    analogWrite(TAILPWM,inptail);
  }
  else
  {
    digitalWrite(TAILBRK,HIGH);
  }

//ENCODER MOTOR LEFT
//digitalWrite(A2, HIGH);       // turn on pullup resistor
  while(inpenl)
  {
    if (encoder0PosL < setPos )
    {
      digitalWrite(M1BRK,LOW);
      digitalWrite(M1Dir,HIGH);
      analogWrite(M1PWM,100);
    //include speed of motor here
      //encode0posL++;
    }
    else
    {
      digitalWrite(M1BRK,HIGH);
      break;
      encoder0PosL = 0;
    }
  }

  
//ENCODER MOTOR RIGHT
//digitalWrite(A2, HIGH);       // turn on pullup resistor
  while(inpenr)
  {
    if (encoder0PosR < setPos )
    {
      digitalWrite(M2BRK,LOW);
      digitalWrite(M2Dir,HIGH);
      analogWrite(M2PWM,100);
    //include speed of motor here
      //encoder0PosR++;
    }
    else
    {
      digitalWrite(M1BRK,HIGH);
      break;
      encoder0PosR = 0;
    }
  }
  // do some stuff here - the joy of interrupts is that they take care of themselves

  //THRUSTER RIGHT

        signal = map(inptr,0,4,1500,1900);
        if (signal != signal_p)
        {
        servo.writeMicroseconds(signal); // Send signal to ESC.
        }
        signal_p = signal;
        Serial.print(signal);  

  //THRUSTER LEFT

        signal = map(inptl,0,4,1500,1900);
        if (signal != signal_p)
        {
        servo.writeMicroseconds(signal); // Send signal to ESC.
        }
        signal_p = signal;
        Serial.print(signal);  

}

void doEncoderL() {
//  /* If pinA and pinB are both high or both low, it is spinning
//   * forward. If they're different, it's going backward.
//   *
//   * For more information on speeding up this process, see
//   * [Reference/PortManipulation], specifically the PIND register.
//   */
if (digitalRead(encoder0PinA) == digitalRead(encoder0PinB)) 
    {
    encoder0PosL++;
    } 
  else 
    {
    encoder0PosL--;
    } 
}

void doEncoderR() {
//  /* If pinA and pinB are both high or both low, it is spinning
//   * forward. If they're different, it's going backward.
//   *
//   * For more information on speeding up this process, see
//   * [Reference/PortManipulation], specifically the PIND register.
//   */
if (digitalRead(encoder1PinA) == digitalRead(encoder1PinB)) 
    {
    encoder0PosR++;
    } 
  else 
    {
    encoder0PosR--;
    } 

//  //Serial.println (encoder0Pos, DEC);
}

/*  to read the other two transitions - just use another attachInterrupt()
in the setup and duplicate the doEncoder function into say, 
doEncoderA and doEncoderB. 
You also need to move the other encoder wire over to pin 3 (interrupt 1). 
*/ 


