
volatile int countl = 0;
volatile int countr = 0;

int inverse = 0;
float e_old = 0;
int err_i = 0;
float sum = 0;
float errors[10] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
float dat1, dat2;

void setup() {
  Serial.begin(115200);
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, 16, 17);
  Serial.println("Started!");


  motors_init();

  buzzer_init();
  beep(900, 300);

  delay(1200);
  servos_init();

  all_forward();
  // delay(2100);
  // all_diagonal();
  beep(1200, 200);
  delay(10);
  beep(600, 90);
  delay(10);
  beep(400, 90);
  delay(10);
  beep(900, 150);
}

void loop() {
  buttonWait(0);
  send_rgb(100, 100, 0);
  delay(10);
  open_claws();

  buttonWait(0);
  send_rgb(100, 0, 100);
  delay(10);
  close_claws();
}


uint32_t tim = 0;
void buttonWait(int flag) {
  while (1) {
    // Serial.println(digitalRead(BTN_PIN));
    if (button() == 0)
      break;
    else if (millis() - tim > 200) {
      tim = millis();
      switch (flag) {
        case (1):
          Serial.print(raw(1));
          Serial.print('\t');
          Serial.print(raw(2));
          Serial.print('\t');
          Serial.print(raw(3));
          Serial.print('\t');
          Serial.print(raw(4));
          Serial.print("\t\t");
          Serial.print(sensor(1));
          Serial.print('\t');
          Serial.print(sensor(2));
          Serial.print('\t');
          Serial.print(sensor(3));
          Serial.print('\t');
          Serial.print(sensor(4));
          Serial.print("\t\t");
          Serial.print(countl);
          Serial.print('\t');
          Serial.print(countr);
          Serial.println('\n');
          break;
        case (2):
          Serial.print(raw(5));
          Serial.print('\t');
          Serial.print(raw(6));
          Serial.print('\t');
          Serial.print(raw(7));
          Serial.print('\t');
          Serial.print(raw(8));
          Serial.print("\t\t");
          Serial.print(sensor_x(1));
          Serial.print('\t');
          Serial.print(sensor_x(2));
          Serial.print('\t');
          Serial.print(sensor_x(3));
          Serial.print('\t');
          Serial.print(sensor_x(4));
          Serial.print("\t\t");
          Serial.print(1234);
          Serial.print('\t');
          Serial.print(5678);
          Serial.println('\n');
          break;
        default:
          break;
      }
    }
  }
  beep(500, 100);
  delay(50);
}
