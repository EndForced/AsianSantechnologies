#define PWM_RES 10
#define PWM_MAX ((1 << PWM_RES) - 1)


void go_up(int way) {
  if (abs(way) == 1) {
    pidX(0.7, 0.03, 0.6, way * PWM_MAX, 400, 0);
    MoveSync(way * PWM_MAX, way * PWM_MAX, 50, 0);
  }
  inverse = 1;
  pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 2000 - (abs(way) == 1) * 400, 0);
  drive(way * 700);
}


#define PWM_MAX 1023 // Замените на фактическое максимальное значение PWM

void align(int speed, float kp, float ki, float kd, int max_error) {
  // Настройка параметров регулятора
  float error_left = 0;
  float error_right = 0;
  float integral_left = 0;
  float integral_right = 0;
  float derivative_left = 0;
  float derivative_right = 0;
  float last_error_left = 0;
  float last_error_right = 0;
  float output_left = 0;
  float output_right = 0;
  all_diagonal();
  delay(200);

  while (abs(error_left) > 10 || abs(error_right) > 10) { // Условие выхода: ошибка достаточно мала

    // Чтение значений датчиков
    int d1 = sensor(1);
    int d2 = sensor(2);
    int d3 = sensor(3);
    int d4 = sensor(4);

    // Расчет ошибок для каждой стороны
    error_left = d2 - d1; // Разница между левыми датчиками
    error_right = d4 - d3; // Разница между правыми датчиками

    // Ограничение ошибок
    error_left = constrain(error_left, -max_error, max_error);
    error_right = constrain(error_right, -max_error, max_error);

    // ПИД-регуляторы для каждой стороны
    // Левая сторона
    integral_left += error_left;
    integral_left = constrain(integral_left, -100, 100); // Антивинд ап
    derivative_left = error_left - last_error_left;
    output_left = kp * error_left + ki * integral_left + kd * derivative_left;
    last_error_left = error_left;

    // Правая сторона
    integral_right += error_right;
    integral_right = constrain(integral_right, -100, 100); // Антивинд ап
    derivative_right = error_right - last_error_right;
    output_right = kp * error_right + ki * integral_right + kd * derivative_right;
    last_error_right = error_right;

    // Применение регулировки к моторам
    int left_speed = speed + output_left; // Увеличиваем скорость, если ошибка отрицательная
    int right_speed = speed + output_right; // Увеличиваем скорость, если ошибка отрицательная

    // Ограничение скорости
    left_speed = constrain(left_speed, -PWM_MAX, PWM_MAX);
    right_speed = constrain(right_speed, -PWM_MAX, PWM_MAX);

    // Движение с коррекцией
    drive(left_speed, left_speed, right_speed, right_speed);

  }

  // Задержка для стабилизации (можно настроить)
  delay(50);

  // Остановка после выравнивания
  stop();
}



void grab_from_ramp(int way) {
  if (abs(way) == 1) {
    pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 400, 0);
    MoveSync(way * PWM_MAX, way * PWM_MAX, 50, 0);
  }
  inverse = 1;
  pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 2800 - (abs(way) == 1) * 400, 0);
}

void grab_from_ramp_up() {

  pidX(0.7, 0.03, 0.6, 900, 400, 1);
  //  arm(0);
  //  buttonWait(0);
  //  pidX(0.7, 0.03, 0.6, PWM_MAX*0.8, 400, 1);
  inverse = 1;
  //  buttonWait(0);
  pidEnc(0.7, 0.03, 0.6, PWM_MAX, 1650, 1);
  open_claws();
  delay(250);
  arm_deg(106);
  delay(200);
  //  buttonWait(0);
  pidX(0.7, 0.03, 0.6, PWM_MAX * 0.72, 50, 1);
  arm(2);
  delay(100);
  close_claws();
  delay(250);

  lay();
  delay(100);
  //  buttonWait(0);
  go_down(-1);
  inverse = 0;
  pidX(0.7, 0.03, 0.6, -PWM_MAX * 0.75, 0, 0);
  pidEnc(0.7, 0.03, 0.6, -PWM_MAX * 0.70, 585, 1);



}


void go_down(int way) {
  int deg = 0;
  if (abs(way) > 1) {
    way /= 2;
    deg = 1400;
    beep(200, 200);
    pidEnc(0.7, 0.03, 0.6, way * PWM_MAX * 0.85, 400, 0);
  }

  pidEnc(0.7, 0.03, 0.6, way * 680, 1000, 0);
  pidEnc(0.7, 0.03, 0.6, way * 400, 1650 - deg, 1);
  inverse = 0;
}


void turn_to_line(int speed, int side_of_turn, int way_to_drive, int number) {

  all_diagonal();
  delay(200);

  int dat1 = 0;

  if (side_of_turn == 1) {
    if (way_to_drive == 1)
      dat1 = 3;
    else
      dat1 = 1;
  } else if (side_of_turn == -1) {
    if (way_to_drive == 1)
      dat1 = 2;
    else
      dat1 = 4;
  }
  for (int i = 0; i < number; i++) {

    if (inverse) {

      while (sensor(dat1) > 400)
        drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);

      while (sensor(dat1) < 880)
        drive(side_of_turn * speed * 0.8, side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8);

      while (sensor(dat1) > 220)
        drive(side_of_turn * speed * 0.6, side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6);
    } else {

      while (sensor(dat1) < 640)
        drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);

      while (sensor(dat1) > 220)
        drive(side_of_turn * speed * 0.8, side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8);

      while (sensor(dat1) < 880)
        drive(side_of_turn * speed * 0.6, side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6);
    }
  }


  stop();
  all_forward();
  delay(200);
}




void MoveSync(float sped1, float sped2, uint32_t dist, int stopp) {
  float e = 0;
  float eold = 0;
  float sped11 = sped1;
  float sped22 = sped2;
  countr = 0;
  countl = 0;
  int timer = millis();
  float deg = 0;
  while (deg < dist) {

    if (sped1 != 0 and sped2 != 0) {
      if (abs(sped1) > abs(sped2)) {
        deg = countl;
        e = countl - countr * abs(sped1) / abs(sped2);
      } else {
        deg = countr;
        e = countl * abs(sped2) / abs(sped1) - countr;
      }

      sped1 = sped11;
      sped2 = sped22;

      float u = e * 4 + (e - eold) * 8;
      float mot1 = sped1 - u * sped1 / abs(sped1);
      float mot2 = sped2 + u * sped2 / abs(sped2);
      if (sped1 > 0)
        mot1 = constrain(mot1, 0, PWM_MAX);
      else
        mot1 = constrain(mot1, -PWM_MAX, 0);

      if (sped2 > 0)
        mot2 = constrain(mot2, 0, PWM_MAX);
      else
        mot2 = constrain(mot2, -PWM_MAX, 0);

      drive(mot1, mot1, mot2, mot2);
      e_old = e;
    } else {
      drive(sped1, sped1, sped2, sped2);
      if (sped1 != 0) deg = countl;
      if (sped2 != 0) deg = countr;
    }
  }
  if (stopp > 0) {  //резко тормоз
    drive(-255 * sped1 / abs(sped1), -255 * sped1 / abs(sped1), -255 * sped2 / abs(sped2), -255 * sped2 / abs(sped2));
    delay(((abs(sped1) + abs(sped2)) / 2) / 255 * 30);
    stop();
    delay(50);
  }
}
