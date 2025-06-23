void pidXN(float sped, int n) {
  if (n > 1)
    for (int i = 1; i < n; i++) {
      pidX(0.5, 0.01, 0.4, sped, 150, 0);
    }
  int overdrive = 575;
  pidX(0.5, 0.02, 0.5, sped, 0, 0);
  pidEnc(0.5, 0.02, 0.5, sped * 0.8, overdrive, 1);
}

void pidX(float kp, float ki, float kd, float sped, int overdrive, int stopp) {
  all_forward();
  int minx = 200;
  if (inverse == 1) {
    minx = 730;
  }

  uint8_t datx1 = 0;
  uint8_t datx2 = 0;
  if (sped > 0) {
    datx1 = 2;  // B
    datx2 = 3;  // C
  } else {
    datx1 = 1;  // A
    datx2 = 4;  // D
  }

  err_i = 0;
  sum = 0;
  for (int i : errors)
    i = 0;
  e_old = 0;

  int counter = 0;
  while (counter < 10) {
    pid_regulator(kp, ki, kd, sped);

    if (!inverse) {
      if (sensor_x(datx1) < minx and sensor_x(datx2) < minx)
        counter++;
      else
        counter = 0;
    } else {
      if (sensor_x(datx1) > minx and sensor_x(datx2) > minx)
        counter++;
      else
        counter = 0;
    }
  }
  // AllForward();
  if (overdrive > 0)
    pidEnc(kp, ki, kd, sped, overdrive, stopp);
  else if (stopp == 1) {  //резко тормоз
    stop_after_pid(sped);
    delay(50);
  }
}

void pidEnc(float kp, float ki, float kd, float sped, int enc, int stopp) {
  // 5000 enc - > 725 mm
  // 100 enc - > 14.5 mm
  all_forward();

  countl = 0;
  countr = 0;
  err_i = 0;
  sum = 0;
  for (int i : errors)
    i = 0;
  e_old = 0;

  while ((countl + countr) < enc) {
    pid_regulator(kp, ki, kd, sped);
  }

  if (stopp == 1) {  //резко тормоз
    stop_after_pid(sped);
  }
}

uint32_t timer = 0;
void pid_regulator(float kp, float ki, float kd, float sped) {

  float speed = abs(sped);
  int way = sped / abs(sped);

  // sensors choosing
  if (sped > 0) {
    dat1 = sensor(2);  // B
    dat2 = sensor(3);  // C
  } else {
    dat1 = sensor(1);  // A
    dat2 = sensor(4);  // D
  }
  // error calculation
  float e = (dat2 - dat1);
  if (inverse) e = -e;
  if (abs(e) < 20)
    e = 0;
  // integral part
  errors[err_i] = e;
  err_i = (err_i + 1) % 10;
  sum = sum + e - errors[err_i];

  float Up = e * kp;                    // Proportional
  float Ui = sum * ki;                  // Integral
  float Ud = (e - errors[err_i]) * kd;  // Differential

  float U = Up + Ui + Ud;  // result

  float mot1 = speed - U;
  float mot2 = speed + U;
  mot1 = constrain(mot1, 0, 1.3 * speed);
  mot2 = constrain(mot2, 0, 1.3 * speed);

  mot1 = mot1 * way;
  mot2 = mot2 * way;
  if (millis() - timer > 15) {
    timer = millis();
    // servo jiggle
    if (abs(U) > 20) {
      int deg = constrain(U * 0.006, -2, 2);
      int serv[4] = { 0, 1, 6, 7 };
      int degs[4] = { ASF + deg, BSF - deg, CSF - deg, DSF + deg };
      Wire.beginTransmission(I2C_ADDRESS);  // Slave address
      for (int i = 0; i < 4; i++)
        send_servo(serv[i], degs[i]);
      Wire.endTransmission();
    } else if (abs(U) < 5)
      all_forward();
  }
  drive(mot1, mot1, mot2, mot2);
}

void stop_after_pid(float sped) {
  int way = sped / abs(sped);
  int tormoz_speed = -way * (1023);
  drive(tormoz_speed, tormoz_speed, tormoz_speed, tormoz_speed);
  delay(10);
  all_forward();
  delay((abs(sped) / 1023.0 * 25) - 10);
  stop();
}