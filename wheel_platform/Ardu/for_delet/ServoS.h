/*	Пользовательская библиотека управления сервоприводами	*/

#ifndef ServoS	// Если библиотека еще не была подключена

#define ServoS	// Подключить ее

#include "Arduino.h"	// Используем стандартную библиотеку Arduino

#include "Servo.h"	// Используем стандартную библиотеку управления сервоприводами

class ServoClass

{

	public:

	Servo serv;	// Собственно сам сервопривод, управляемый стандартной

				// библиотекой servo

	int servPosition;	  // Текущая позиция сервопривода, градусов

	int posMax;	// Максимально допустимый предел перемещения сервопривода, градусов

	int posMin;	// Минимальный допустимый предел перемещения сервопривода, градусов

	int posInit;	// Исходная позиция сервопривода, градусов

	// Переменные, которые отвечают за перемещение

	boolean move;	   // Должен ли двигатся ли сервопривод в настоящий момент 

	int movePosition;	// Позиция, которую должен принять сервопривод, градусы

	float moveSpeed;	// Скорость, с которой сервопривод должен двигаться, об/мин

	int moveIncrement;	  // изменение положения за один интервал времени, градусов

	int moveInterval;	// Интервал между движениями для обеспечения  скорости, миллисекунды

	unsigned long lastTimeCheck;	// Время последнего движения сервопривода, в мс от начала работы программы

	ServoClass();		// Конструктор класса

	void AttachServo (int pin);		//Инициализация сервопривода с указанием только номеры выхода для подключения

	void AttachServo (int pin, int minpos, int maxpos, int initpos);	//Инициализация сервопривода с указанием минимальной, максимальной и исходной позиции

	int PositionCheck(int movepos);	// Проверка, попадает  ли позиция в заданный интервал

	void MoveTo (int movepos);		// Подать команду на перемещение сервопривода	

	void MoveTo (int movepos, float movespeed) ;	// Подать команду на перемещение сервопривода с указанием скорости

	void Update ();		//Обработка перемещений

};

#endif 


