//#include "function.cpp"
#include "Arduino.h"



/*this function initializes pins control drivers
 * --------------------------------
 *  1       2      3         4
 * anble   pwm   toward   reverse
 *--------------------------------
 * on the platform we have to driver therefor
 * array leght is 8 position*/


//pinMode(pins[0], OUTPUT);
/*
void init(){
  for(int i = 0; i< 8; i++){
    pinMode(pins[i], OUTPUT);
  }
  pinMode(servos[0], OUTPUT);
  pinMode(servos[1], OUTPUT);
}*//*

bool motorWriteInit(int *arr){
    for(int i = 0; i < 8; i++){
        pins[i] = arr[i];
    }
    return 0;
}*/
//the speed value varies between 1 and 255

/*
int sign(int arg1, int arg2){
    if(arg1 > arg2) return 1;
    else return -1;
}

//angle value varies between 0 to 180 degres
void camServo(int pos1, int pos2){
    for(;;){
        if(pos1 != -1){
            servos[4] += sign(pos1, servos[4]);
            srv1.write(servos[4]);
        }
        if(pos2 != -1){
            servos[5] += sign(pos1, servos[5]);
            srv1.write(servos[5]);
        }
        delay(1);
    }
}
/*this fuct initializes pins that control camera servos
 * ------------------------------------------------------------------------
 *      1           2           3         4            5             6
 * horizontal    vertical   border_1   border_2   start_pos_1   start_pos_2
 * -------------------------------------------------------------------------
bool camServoInit(int *arr){
    for(int i = 0; i < 6; i++){
        servos[i] = arr[i];
    }
    srv1.attach(servos[0]);
    srv2.attach(servos[1]);
    camServo(servos[4], servos[5]);
    return 0;
}*/
