/*	Пользовательская библиотека управления сервоприводами	*/

#include "ServoS.h"		// Подключаем заголовочный файл

ServoClass::ServoClass()	// Конструктор класса

{

	posMin=0;

	posMax=180;

	posInit=0;

	servPosition=0;

	lastTimeCheck=millis();	

}

void ServoClass::AttachServo (int pin)	////Инициализация сервопривода с указанием только номеры выхода для подключения

{

	serv.attach(pin);	// Подключаем сервопривод к указанному пину

	posMin= 0;		// Устанавливаем минимальную позицию 

	posMax= 180; 	  // Устанавливаем максимальную позицию 

	posInit= 0;		// Устанавливаем исходную позицию

	servPosition= posInit;	// Позиция сервопривода должна сответствовать исходному положению	

	serv.write(servPosition);	// Даем команду изменить положение

}

void ServoClass::AttachServo (int pin, int minpos, int maxpos, int initpos)	//Инициализация сервопривода с указанием минимальной, максимальной и исходной позиции

{

	serv.attach(pin);	// Подключаем сервопривод к указанному пину

	posMin= minpos;		// Устанавливаем минимальную позицию 

	posMax= maxpos; 	  // Устанавливаем максимальную позицию 

	posInit= initpos;		// Устанавливаем исходную позицию

	servPosition= posInit;	// Позиция сервопривода должна сответствовать исходному положению	

  movePosition=posInit;

	serv.write(servPosition);	// Даем команду изменить положение

}

int ServoClass::PositionCheck(int movepos)	// Проверка, попадает  ли позиция в заданный интервал

{

	int CheckedPos;

	if (movepos<=posMin)	// Если указано большее значение, чем максимальный

					// предел перемещения

	CheckedPos =posMin;	// Будем двигаться тоько до этого предела

	else

	if (movepos>=posMax)	// Если указано меньшее значение, чем минимальный 

					//предел перемещения

	CheckedPos =posMax;	// Будем двигаться тоько до этого предела

	else			// В любых других случаях - мы в допустимых для перемещения пределах

	CheckedPos =movepos;	// Просто устанавливаем позицию, в которую должен

	return CheckedPos;

}

void ServoClass::MoveTo (int movepos)  // Если скорость не указана - просто даем команду на перемещение сервопривода

{

		

		movePosition = PositionCheck(movepos); // Проверяем, не выходим ли мы за допустимые пределы премещения

		serv.write(servPosition);	// Даем команду изменить положение

}

void ServoClass::MoveTo (int movepos, float movespeed)  // Если скорость  указана - организуем плавное перемещение

{

	movePosition = PositionCheck(movepos); // Проверяем, не выходим ли мы за допустимые пределы премещения

	moveSpeed=movespeed;	// Устанавливаем скорость, с которой должен перемещаться сервопривод

	int Angle=abs(movePosition-servPosition);	  // На сколько должен переместиться сервопривод 

					// вне зависимости от направления

	if (movePosition >= servPosition)	// Определяем, в какую сторону от текущего положения нам нужно двигаться

		moveIncrement=1;	// Если вперед - будем добавлять один градус за один интервал времени

	else

		moveIncrement=-1; //  Если назад - то отнимать

	float RotationSpeed=moveSpeed*360/60;  // Перводим скорость из оборотов в минуту в градусы за секунду

	moveInterval=(int)1000/RotationSpeed;  // Вычисляем интервал между перемещениями на один градус

	move=true;  // Даем комнду начать плавное перемещение

} 

void ServoClass::Update ()	////Обработка перемещений

{

	if (move)  //Если дана команда на перемещение

	{

		if ((millis() - lastTimeCheck)>= moveInterval)	// проверяем, сколько прошло времени с последнего 

									//действия и сравниваем с нужным нам интервалом. 

									//Если времени прошло больше – совершаем следующее действие

		{

			servPosition+=moveIncrement;			// Изменяем угол на вычисленное ранее значение

			serv.write(servPosition);		// Посылаем сервоприводу команду с новым углом поворота

			lastTimeCheck= millis();	// Обновляем счетчик времени, для того чтобы следующий отсчет времени начался с этого момента

			if (servPosition==movePosition)	// Если мы достигли нужной позиции-

				move=false;			// остановить движение

		}

	}

}
