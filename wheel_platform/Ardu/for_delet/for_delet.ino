#include </home/daniil/Desktop/arduino/for_delet/handle.h>

Handler myHandler;

int arr[3] = {0};
int counter = 0;
int sp = 0;

void setup() {
  // put your setup code here, to run once
  Serial.begin(9600);
  Serial.println(myHandler.checkSys());
  myHandler.configServo();
  
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()>0){
    if(counter > 1){
      sp += (int)((Serial.read() - 48)*(int)pow(10.0, 4-counter));
    }
    else arr[counter] = (int)(Serial.read() - 48);
    counter++;
    if(counter == 5){
      arr[2] = sp;
      sp = 0;
      myHandler.classificer(arr);
      counter = 0;
    } 
  }
  myHandler.upDate();
}
