
void FromNormalToInverse(int way) {
  if (abs(way) == 1) {
    pidEnc(2, 0, 1, way * 255, 400, 0);
    MoveSync(way * 255, way * 255, 50, 0);
  }
  inverse = 1;
  pidEnc(1.0, 0.01, 0.2, way * 255, 2800 - (abs(way) == 1) * 400, 0);
}

void FromInverseToNormal(int way) {
  int deg = 0;
  if (abs(way) > 1) {
    way /= 2;
    deg = 1400;
    beep(200, 200);
    pidEnc(1.5, 0.1, 1, way * 255, 400, 0);
  }

  pidEnc(1.5, 0.1, 1, way * 110, 900, 0);
  pidEnc(1.5, 0.1, 1, way * 80, 1650 - deg, 1);
  inverse = 0;
  // pidEnc(3, 0, 1, way * 80, 100, 1);
}


void turn_to_line(int speed, int side_of_turn, int way_to_drive, int number) {
  all_diagonal();
  delay(200);
  for (int i = 0; i < number; i++) {
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

    if (inverse) {
      drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);
      delay(50);

      while (sensor(dat1) > 400)
        drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);

      while (sensor(dat1) < 920)
        drive(side_of_turn * speed * 0.8, side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8);

      while (sensor(dat1) > 120)
        drive(side_of_turn * speed * 0.6, side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6);
    } else {
      drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);
      delay(50);
      while (sensor(dat1) < 640)
        drive(side_of_turn * speed, side_of_turn * speed, -side_of_turn * speed, -side_of_turn * speed);

      while (sensor(dat1) > 160)
        drive(side_of_turn * speed * 0.8, side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8, -side_of_turn * speed * 0.8);

      while (sensor(dat1) < 920)
        drive(side_of_turn * speed * 0.6, side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6, -side_of_turn * speed * 0.6);
    }
  }
  int tormoz_speed = -side_of_turn * (1023);
  drive(tormoz_speed, tormoz_speed, -tormoz_speed, -tormoz_speed);
  delay(10);
  all_forward();
  delay((abs(speed) / 1023.0 * 20)-10);
  stop();
  delay(100);
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
        mot1 = constrain(mot1, 0, 255);
      else
        mot1 = constrain(mot1, -255, 0);

      if (sped2 > 0)
        mot2 = constrain(mot2, 0, 255);
      else
        mot2 = constrain(mot2, -255, 0);

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