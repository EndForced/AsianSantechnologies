/*----------------------MOTORS-------------------------*/
#define ma1 38
#define ma2 40

#define mb1 4
#define mb2 5

#define mc1 41
#define mc2 42

#define md1 1
#define md2 2

#define PWM_FREQ 8000
#define PWM_RES 10

#define PWM_MAX ((1 << PWM_RES) - 1)

void motors_init() {
  // Serial.println(PWM_MAX);
  /*------------PWM_PINS-------------*/
  ledcAttach(ma1, PWM_FREQ, PWM_RES);
  ledcAttach(ma2, PWM_FREQ, PWM_RES);
  ledcAttach(mb1, PWM_FREQ, PWM_RES);
  ledcAttach(mb2, PWM_FREQ, PWM_RES);
  ledcAttach(mc1, PWM_FREQ, PWM_RES);
  ledcAttach(mc2, PWM_FREQ, PWM_RES);
  ledcAttach(md1, PWM_FREQ, PWM_RES);
  ledcAttach(md2, PWM_FREQ, PWM_RES);

  // turn off all
  for (int i = 0; i < 8; i++)
    ledcWriteChannel(i, PWM_MAX);

  /*-------INTERRUPTS---------*/
  attachInterrupt(digitalPinToInterrupt(47), encl, RISING);
  attachInterrupt(digitalPinToInterrupt(36), encr, RISING);
}


void drive(float spa, float spb, float spc, float spd) {
  // sets speed to all four motors

  // constrain all speeds
  spa = constrain(spa * 1, -PWM_MAX, PWM_MAX);
  spb = constrain(spb * 1, -PWM_MAX, PWM_MAX);
  spc = constrain(spc * 1, -PWM_MAX, PWM_MAX);
  spd = constrain(spd * 1, -PWM_MAX, PWM_MAX);


  ledcWrite(ma1, spa > 0 ? spa : 0);
  ledcWrite(ma2, spa < 0 ? -spa : 0);

  ledcWrite(mb1, spb > 0 ? spb : 0);
  ledcWrite(mb2, spb < 0 ? -spb : 0);

  ledcWrite(mc1, spc > 0 ? spc : 0);
  ledcWrite(mc2, spc < 0 ? -spc : 0);

  ledcWrite(md1, spd > 0 ? spd : 0);
  ledcWrite(md2, spd < 0 ? -spd : 0);
}

void drive(int speed) {
  drive(speed, speed, speed, speed);
}

void stop() {
  // forcefully stops all motors
  for (int i = 0; i < 8; i++)
    ledcWriteChannel(i, PWM_MAX);
}


void encl() {
  countl++;
}
void encr() {
  countr++;
}
