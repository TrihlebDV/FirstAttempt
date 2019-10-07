//#include "function.cpp"

#include <Servo.h>

Servo srv1;
Servo srv2;

int pins[8] = {8, 3, 2, 4, 8, 5, 6 , 7};
int servos[6] = {10, 11, 0, 0, 0, 0};

void motorWrite(int max_speed, int _direction){
    if(max_speed == -1){
        digitalWrite(pins[0], LOW);
        digitalWrite(pins[4], LOW);
        analogWrite(pins[1], 0);
        analogWrite(pins[5], 0);
    }
    else{
        digitalWrite(pins[0], HIGH);
        digitalWrite(pins[4], HIGH);
        switch (_direction) {
        case 1:  //ahead
            digitalWrite(pins[2], HIGH);
            digitalWrite(pins[3], LOW);
            digitalWrite(pins[6], HIGH);
            digitalWrite(pins[7], LOW);
            break;
        case 2:  //backward
            digitalWrite(pins[2], LOW);
            digitalWrite(pins[3], HIGH);
            digitalWrite(pins[6], LOW);
            digitalWrite(pins[7], HIGH);
            break;
        case 3:  //right
            digitalWrite(pins[2], HIGH);
            digitalWrite(pins[3], LOW);
            digitalWrite(pins[6], LOW);
            digitalWrite(pins[7], HIGH);
            break;
        case 4:  //left
            digitalWrite(pins[2], LOW);
            digitalWrite(pins[3], HIGH);
            digitalWrite(pins[6], HIGH);
            digitalWrite(pins[7], LOW);
            break;
        default:
            break;
        }
        //gradually turn on the engines
        for(int i = 1; i <= max_speed; i++){
            analogWrite(pins[1], i);
            analogWrite(pins[5], i);
            delay(1);
        }
    }
}

void setup() {
  for(int i = 0; i< 8; i++){
    pinMode(pins[i], OUTPUT);  
  }
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);  
  Serial.begin(115200);
}

void loop() {
  if(Serial.available()){
    char count = Serial.read();
    Serial.println(count);
    switch (count) {
      case 65:
      {
        motorWrite(200, 1);
        break;
      }
      case 66:
      {
       motorWrite(200, 2);
       break;
      }
      case 67:
      {
        motorWrite(150, 3);
        break;
      }
      case 68:
      {
        motorWrite(150, 4);
        break;
      }
      case 69:
      {
        motorWrite(-1, 0);
        break;
      }
    }
    }
  delay(10);
}
