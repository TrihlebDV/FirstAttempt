//#include "function.cpp"

#include <Servo.h>

Servo srv1;
Servo srv2;

int pins[8] = {8, 3, 2, 4, 8, 5, 6 , 7};
int servos[6] = {10, 11, 90, 90};

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
            digitalWrite(pins[6], LOW);
            digitalWrite(pins[7], HIGH);
            break;
        case 2:  //backward
            digitalWrite(pins[2], LOW);
            digitalWrite(pins[3], HIGH);
            digitalWrite(pins[6], HIGH);
            digitalWrite(pins[7], LOW);
            break;
        case 3:  //right
            digitalWrite(pins[2], HIGH);
            digitalWrite(pins[3], LOW);
            digitalWrite(pins[6], HIGH);
            digitalWrite(pins[7], LOW);
            break;
        case 4:  //left
            digitalWrite(pins[2], LOW);
            digitalWrite(pins[3], HIGH);
            digitalWrite(pins[6], LOW);
            digitalWrite(pins[7], HIGH);
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
void servo(int flag){
  if(flag == 11){
    if(servos[2] < 120) servos[2] += 3;
    srv1.write(servos[2]);
  }
  if(flag == 10){
    if(servos[2] > 20) servos[2] -= 3;
    srv1.write(servos[2]);
  }
  if(flag == 21){
    if(servos[3] < 120) servos[3] += 3;
    srv2.write(servos[3]);
  }
  if(flag == 20){
    if(servos[3] > 20) servos[3] -= 3;
    srv2.write(servos[3]);
  }
}

void setup() {
  for(int i = 0; i< 8; i++){
    pinMode(pins[i], OUTPUT);  
  }
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);  

  srv1.attach(11);
  srv2.attach(9);
  srv1.write(90);
  srv2.write(90);
  
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
      case 70:
      {
      servo(11);
      break;
      }
      case 71:
      {
        servo(10);
        break;
      }
      case 72:
      {
      servo(21);
      break;
      }
      case 73:
      {
        servo(20);
        break;
      }
    }
    }
  delay(10);
}
