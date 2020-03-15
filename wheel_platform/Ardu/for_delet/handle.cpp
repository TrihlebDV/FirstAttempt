
#include </home/daniil/Desktop/arduino/for_delet/handle.h> 
#include <Arduino.h>

Handler::Handler(){
  change = 150;
}

bool Handler::checkSys(){ return 0;}

void Handler::configServo()
{
  servoH.AttachServo(12, 30, 150, 90);
  servoV.AttachServo(11, 30, 150, 90);
}

void Handler::camCtrl(int pitch, int yaw){
  if(pitch != 0) 
  {
    int arg;
    if(pitch == 1) arg = 1;
    else arg = -1;
    int angPitch = servoH.movePosition + 10*arg;
    servoH.MoveTo(angPitch, 5.0);
  }
  if(yaw != 0)
  {
    int arg;
    if(yaw == 1) arg = 1;
    else arg = -1;
    int angYaw = servoV.movePosition + 10*arg;
    servoV.MoveTo(angYaw, 5.0);
  }
}

void Handler::boardCtrl(int direct, int spd){
  //motors.set(direct, spd);
  if(direct == 1) //ahead
  {
    boardL.MoveTo(true, spd, change);
    boardR.MoveTo(true, spd, change);
  }
  
  else if(direct == 2) //backward
  {
    boardL.MoveTo(false, spd, change);
    boardR.MoveTo(false, spd, change);
  }
  
  else if(direct == 3) //left
  {
    boardL.MoveTo(false, spd/2, change);
    boardR.MoveTo(true, spd/2, change);
  }

  else if(direct == 4) //right
  {
    boardL.MoveTo(true, spd/2, change);
    boardR.MoveTo(false, spd/2, change);
  }
}
void Handler::classificer(int* arr){
  if(arr[0] == 0)      camCtrl(arr[1], arr[2]);
  else if(arr[0] == 1) boardCtrl(arr[1], arr[2]);
}
void Handler::upDate(){
  boardL.Update();
  boardR.Update();  
  servoH.Update();
  servoV.Update();
}
