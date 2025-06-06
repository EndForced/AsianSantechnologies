#define PWM_RES 10
#define PWM_MAX ((1 << PWM_RES) - 1)


void go_up(int way) {
  if (abs(way) == 1) {
    pidX(0.7, 0.03, 0.6, way * PWM_MAX, 400, 0);
    MoveSync(way * PWM_MAX, way * PWM_MAX, 50, 0);
  }
  inverse = 1;
  pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 2000 - (abs(way) == 1) * 400, 0);
  drive(way*700);
}


void grab_from_ramp(int way) {
  if (abs(way) == 1) {
    pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 400, 0);
    MoveSync(way * PWM_MAX, way * PWM_MAX, 50, 0);
  }
  inverse = 1;
  pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 2800 - (abs(way) == 1) * 400, 0);
}


void go_down(int way) {
  int deg = 0;
  if (abs(way) > 1) {
    way /= 2;
    deg = 1400;
    beep(200, 200);
    pidEnc(0.7, 0.03, 0.6, way * PWM_MAX, 400, 0);
  }

  pidEnc(0.7, 0.03, 0.6, way * 680, 1000, 0);
  pidEnc(0.7, 0.03, 0.6, way * 400, 1650 - deg, 1);
  inverse = 0;
}


void turn_to_line(int speed, int side_of_turn, int way_to_drive, int number, bool smooth_turn = false) {
  all_diagonal();
  delay(200);

  // Калибровочные коэффициенты для разных направлений
  float left_correction = 1.4;
  float right_correction = 1.2;
  
  // Коэффициенты для разных режимов поворота
  float aggressive_factor = 1.0;    // Максимальная мощность для грубого поворота
  float smooth_factor = 0.5;        // Пониженная мощность для аккуратного поворота
  float brake_factor = smooth_turn ? 0.4 : 0.6;  // Разные коэффициенты торможения
  float align_factor = smooth_turn ? 0.3 : 0.6;  // Разные коэффициенты выравнивания

  int dat1 = 0;
  if (side_of_turn == 1) {
    if (way_to_drive == 1) dat1 = 3;
    else dat1 = 1;
  } else {
    if (way_to_drive == 1) dat1 = 2;
    else dat1 = 4;
  }

  for (int i = 0; i < number; i++) {
    float correction = (side_of_turn == 1) ? left_correction : right_correction;
    float power_factor = smooth_turn ? smooth_factor : aggressive_factor;
    
    if (inverse) {
      // Фаза 1: Основной поворот
      while (sensor(dat1) > 400) {
        drive(side_of_turn * speed * power_factor * correction, 
              side_of_turn * speed * power_factor * correction, 
              -side_of_turn * speed * power_factor * correction, 
              -side_of_turn * speed * power_factor * correction);
        delay(10);
      }
      
      // Фаза 2: Торможение
      while (sensor(dat1) < 880) {
        drive(side_of_turn * speed * brake_factor * correction, 
              side_of_turn * speed * brake_factor * correction, 
              -side_of_turn * speed * brake_factor * correction, 
              -side_of_turn * speed * brake_factor * correction);
        delay(10);
      }
      
      // Фаза 3: Выравнивание
      while (sensor(dat1) > 220) {
        drive(side_of_turn * speed * align_factor * correction, 
              side_of_turn * speed * align_factor * correction, 
              -side_of_turn * speed * align_factor * correction, 
              -side_of_turn * speed * align_factor * correction);
        delay(10);
      }
    } else {
      // Обратная логика для inverse == false
      while (sensor(dat1) < 640) {
        drive(side_of_turn * speed * power_factor * correction, 
              side_of_turn * speed * power_factor * correction, 
              -side_of_turn * speed * power_factor * correction, 
              -side_of_turn * speed * power_factor * correction);
        delay(10);
      }
      
      while (sensor(dat1) > 220) {
        drive(side_of_turn * speed * brake_factor * correction, 
              side_of_turn * speed * brake_factor * correction, 
              -side_of_turn * speed * brake_factor * correction, 
              -side_of_turn * speed * brake_factor * correction);
        delay(10);
      }
      
      while (sensor(dat1) < 880) {
        drive(side_of_turn * speed * align_factor * correction, 
              side_of_turn * speed * align_factor * correction, 
              -side_of_turn * speed * align_factor * correction, 
              -side_of_turn * speed * align_factor * correction);
        delay(10);
      }
    }
  }
  
  // Торможение и завершение маневра
  int tormoz_speed = -side_of_turn * (1023);
  drive(tormoz_speed, tormoz_speed, -tormoz_speed, -tormoz_speed);
  delay(10);
  all_diagonal();
  delay((abs(speed) / 1023.0 * 30) - 10);
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
