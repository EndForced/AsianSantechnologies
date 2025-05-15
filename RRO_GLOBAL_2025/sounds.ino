/*-----------------------------BUZZERS-----------------------------*/
#define BZ1_PIN 10
#define BZ2_PIN 35
// у меня не сделаны асинхронные бипы
// скорее всего сделаю через микрос
void beep(int freq, int dur) {
  myTone(1.0 / float(freq), dur);
}

void myTone(float per, int dur) {
  uint32_t tim = millis();
  while (millis() < tim + dur) {
    digitalWrite(BZ1_PIN, 1);
    delayMicroseconds(per * 1e+5 * 5);
    digitalWrite(BZ1_PIN, 0);
    delayMicroseconds(per * 1e+5 * 5);
  }
}


#define D4 293
#define D5 587
#define A4 440
#define GH4 415
#define G4 391
#define F4 350
#define C4 261
#define C5 523


void do_megalovania() {

  delay(150);
  beep(D4, 75);
  delay(75);

  beep(D4, 75);
  delay(75);

  beep(D5, 75);
  delay(75 + 125);


  beep(A4, 75);
  delay(75 + 250);

  beep(GH4, 75);
  delay(75 + 125);


  beep(G4, 75);
  delay(75 + 125);

  beep(F4, 125);
  delay(125);

  beep(D4, 75);
  delay(75);

  beep(F4, 75);
  delay(75);

  beep(G4, 75);
  delay(75);

  // beep(C4,75);
  // delay(75);

  // beep(C4,75);
  // delay(75);

  // beep(D5,75);
  // delay(75+125);

  // beep(A4,75);
  // delay(75+250);


  // beep(GH4,75);
  // delay(75+125);


  // beep(G4,75);
  // delay(75+125);

  // beep(F4,125);
  // delay(125);
}