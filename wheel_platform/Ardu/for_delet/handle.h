#pragma once
#include <Arduino.h>
#include </home/daniil/Desktop/arduino/for_delet/ServoS.h>
#include </home/daniil/Desktop/arduino/for_delet/BoardS.h>
//#include </home/daniil/Desktop/arduino/for_delet/configHandle.h>

/*#define enb1    28
#define enb2    29
#define swch11  22
#define swch12  23
#define swch21  4
#define swch22  25
#define Pin1 1
#define Pin2 2
#define serH 8
#define serV 9
*/

 
class Handler
{
public:
  BoardClass boardL{10, 28, 24, 25, 0, 255, 'l'};
  BoardClass boardR{7, 29, 23, 22, 0, 255, 'r'};  
  ServoClass servoH;
  //serv1.AttachServo(8, 30, 150, 90);
  ServoClass servoV;
  //servoV.AttachServo(9, 30, 150, 90);
  Handler();
  int change;
  bool checkSys();
  void camCtrl(int pitch, int yaw);
  void boardCtrl(int direct, int spd);
  void classificer(int* arr);
  void upDate();
  void configServo();
}; 

  
