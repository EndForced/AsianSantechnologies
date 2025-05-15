void pidXN(float sped, int n) {
  if (n > 1)
    for (int i = 1; i < n; i++) {
      pidX(1.5, 0.02, 0.8, sped, 100, 0);
    }
  int overdrive = 555;
  pidX(2.5, 0.01, 0.8, sped * 0.7, overdrive, 1);
}

void pidX(float kp, float ki, float kd, float sped, int overdrive, int stopp) {

  int minx = 60;
  if (inverse == 1) {
    minx = 230;
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
  while (counter < 20) {
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
  } else delay(50);
}

void pidEnc(float kp, float ki, float kd, float sped, int enc, int stopp) {
  // 800 enc - > 125 mm
  // 100 enc - > 15.625 mm
  // ^ to update
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
  delay(50);
}


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
  if (abs(e) < 4)
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

  // servo jiggle
  // int deg = constrain(U * 0.025, -3, 3);
  // bserv.write(BSF - deg);
  // cserv.write(CSF - deg);
  // dserv.write(DSF + deg);
  // aserv.write(ASF + deg);

  drive(mot1, mot1, mot2, mot2);
}

void stop_after_pid(float sped) {
  int way = sped / abs(sped);
  int tormoz_speed = -way * 255;
  drive(tormoz_speed, tormoz_speed, tormoz_speed, tormoz_speed);
  delay(abs(sped) / 255.0 * 30);
  stop();
}