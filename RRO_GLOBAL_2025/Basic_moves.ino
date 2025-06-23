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
  cam(1);
  pidEnc(0.7, 0.03, 0.6, way * 680, 1000, 0);
  pidEnc(0.7, 0.03, 0.6, way * 400, 1650 - deg, 1);
  cam(0);
  inverse = 0;
}

void otrovnyat(int time) {
  float errors1[10] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  float kp = 0.8;
  float ki = 0.0;
  float kd = 0.7;
  uint32_t tim = millis();
  int counter = 0;
  // all_side();
  while (millis() - tim < time) {
    // sensors choosing
    dat1 = sensor(1);      // A
    dat2 = sensor(2);      // B
    int dat3 = sensor(3);  // C
    int dat4 = sensor(4);  // D

    // error calculation
    float e = (dat2 - dat3);
    float e1 = (dat4 - dat1);
    if (inverse) e = -e;
    if (inverse) e1 = -e1;

    // if (abs(e) > 20 or abs(e1) > 20) counter = 0;
    // else counter++;
    // if (counter > 20) break;

    errors[err_i] = e;
    errors1[err_i] = e1;
    err_i = (err_i + 1) % 10;

    float Up = e * kp;                    // Proportional
    float Ud = (e - errors[err_i]) * kd;  // Differential

    float U = Up + Ud;  // result

    float Up1 = e1 * kp;                     // Proportional
    float Ud1 = (e1 - errors1[err_i]) * kd;  // Differential

    float U1 = Up1 + Ud1;  // result

    float mot1 = -U1;
    float mot2 = U;
    float mot3 = U;
    float mot4 = -U1;
    mot1 = constrain(mot1, -900, 900);
    mot2 = constrain(mot2, -900, 900);
    mot3 = constrain(mot3, -900, 900);
    mot4 = constrain(mot4, -900, 900);

    drive(-mot1, mot2, -mot3, mot4);
  }
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
        drive(side_of_turn * 750, side_of_turn * 750, -side_of_turn * 750, -side_of_turn * 750);

      while (sensor(dat1) > 450 and not align_flag)
        drive(side_of_turn * 750, side_of_turn * 750, -side_of_turn * 750, -side_of_turn * 750);
    } else {

      while (sensor(dat1) < 640)
        drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);

      while (sensor(dat1) > 220)
        drive(side_of_turn * 750, side_of_turn * 750, -side_of_turn * 750, -side_of_turn * 750);

      while (sensor(dat1) < 550 and not align_flag)
        drive(side_of_turn * 750, side_of_turn * 750, -side_of_turn * 750, -side_of_turn * 750);
    }
  }
  if (align_flag) {
    otrovnyat(300);
  } else {
    int tormoz_speed = -side_of_turn * (1023);
    drive(tormoz_speed, tormoz_speed, -tormoz_speed, -tormoz_speed);
    delay(10);
    delay((abs(speed) / 1023.0 * 25) - 10);
  }
  otrovnyat(200);

  stop();
  delay(100);
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