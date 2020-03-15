/*	Пользовательская библиотека управления сервоприводами	*/

#include "BoardS.h"		// Подключаем заголовочный файл

BoardClass::BoardClass(int pin, int enable, int sw1, int sw2, int sMin, int sMax, char d)	// Конструктор класса

{
  board=pin;
  
	posMin=sMin;

	posMax=sMax;

	enb=enable;

  switch1=sw1;

  switch2=sw2;

	LTC=millis();	

  RTDir=true;

  motDir=true;
  
  RTSpeed=0;

  id = d;
}

int BoardClass::checkSpeed(int spd)	// Проверка, попадает  ли позиция в заданный интервал

{
   
	int RSpeed;

	if (spd<=posMin)
	{
	  RSpeed=posMin;
	}

	else
	{
	  if (spd>=posMax)
	  {
	    RSpeed=posMax;// Если указано меньшее значение, чем минимальный 
	  }

	  else			// В любых других случаях - мы в допустимых для перемещения пределах
    {
	    RSpeed =spd;	// Просто устанавливаем позицию, в которую должен
    }
	}
  
	return RSpeed;

}

void BoardClass::MoveTo (bool dir, int spd, int chSpd)  // Если скорость  указана - организуем плавное перемещение

{
  motDir = dir;
	motSpeed = checkSpeed(spd); // Проверяем, не выходим ли мы за допустимые пределы премещения
	chgSpeed=chSpd;	// Устанавливаем скорость, с которой должен перемещаться сервопривод

	TDiff=1000/chgSpeed;  // Вычисляем интервал между перемещениями на один градус
                                     // moveSpeed: grad per second

	move=true;  // Даем комнду начать плавное перемещение
} 

void BoardClass::setSpd(bool dir, int spd)
{
  digitalWrite(switch1, dir^1);//устанавливаем нужное направление движения
  digitalWrite(switch2, dir^0);

  analogWrite(board, spd);//устанавливаем необходимую скорость перемещения
}

void BoardClass::Update ()	////Обработка перемещений
{
	if (move)  //Если дана команда на перемещение
	{
		if ((millis() - LTC)>= TDiff)	// проверяем, сколько прошло времени с последнего 
		{
      if (RTDir == motDir)
      {
        if (RTSpeed == motSpeed)
        {
          setSpd(RTDir, RTSpeed);
          move=false;         
        }
        else
        {
          if (RTSpeed > motSpeed)
          {
            RTSpeed --;
            setSpd(RTDir, RTSpeed);            
          }
          else
          {
            RTSpeed ++;
            setSpd(RTDir, RTSpeed); 
          }
        }
		  }
      else
      {
        if (RTSpeed == 0) 
        {
          Serial.println(RTDir);
          RTDir = !RTDir;
          Serial.println(id);
        }
        else
        {
          RTSpeed --;
          setSpd(RTDir, RTSpeed);
        }
      }
      LTC = millis();
	  }
  }
}
