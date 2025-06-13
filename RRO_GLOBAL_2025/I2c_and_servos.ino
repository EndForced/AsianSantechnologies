#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#define I2C_ADDRESS 0x0A  // Change this if needed
#define RGB_PIN 48
#define NUMPIXELS 3

Adafruit_NeoPixel pixels(NUMPIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);

/*------------------------------A---B---CL1-ARM-CL2-CAM-C---D-*/
const int base_positions[8] = { 93, 87, 90, 10, 90, 150, 86, 88 };

#define ASF 140
#define BSF 40
#define CSF 135
#define DSF 45

void servos_init() {
  Wire.begin();  // Join I2C bus as master
  Wire.setClock(400000);

  send_rgb(0, 0, 0);
  delay(20);
  arm(6, 10);
  delay(150);
  close_claws();
  cam(0);

  // open_claws();
  all_forward();
  delay(300);
}

const byte arm_num = 3;
const byte arm_positions[] = { 102, 98, 93, 60, 40, 22, 5};  // from stand to last tube
const byte max_pos = sizeof(arm_positions) / sizeof(byte) - 1;

byte last_arm_pos = 10;
byte last2_arm_pos = 10;

void arm(byte num_of_pos) {
  last2_arm_pos = last_arm_pos;
  byte distance = abs(arm_positions[num_of_pos] - last_arm_pos);
  send_servo(arm_num, arm_positions[num_of_pos]);
  last_arm_pos = arm_positions[num_of_pos];
}

void arm(byte num_of_pos, int del) {
  last2_arm_pos = last_arm_pos;
  byte distance = abs(arm_positions[num_of_pos] - last_arm_pos);
  for (int i = last_arm_pos; i != arm_positions[num_of_pos]; arm_positions[num_of_pos] > last_arm_pos ? i++ : i--) {
    send_servo(arm_num, i);
    float dist = distance;
    delay(del);
  }
  // send_servo(arm_num, arm_positions[num_of_pos]);

  last_arm_pos = arm_positions[num_of_pos];
}

void arm_deg(byte deg) {
  last2_arm_pos = last_arm_pos;
  byte distance = abs(deg - last_arm_pos);
  send_servo(arm_num, deg);
  last_arm_pos = deg;
}

void arm_deg(byte deg, int del) {
  last2_arm_pos = last_arm_pos;
  byte distance = abs(deg - last_arm_pos);
  for (int i = last_arm_pos; i != deg; deg > last_arm_pos ? i++ : i--) {
    send_servo(arm_num, i);
    float dist = distance;
    delay(del);
  }
  // send_servo(arm_num, arm_positions[num_of_pos]);

  last_arm_pos = deg;
}

int time_calc(byte new_pos) {
  byte distance = abs(arm_positions[new_pos] - last2_arm_pos);
  return distance * 10 + 100;
}

void grab() {
  open_claws();
  arm(1);
  delay((time_calc(1) * 3) / 4);
  pidEnc(0.7, 0.07, 0.8, 850, 350, 0);
  pidEnc(0.7, 0.07, 0.8, 450, 200, 1);
  delay(200);
  arm(2);
  delay(time_calc(2) + 150);
  close_claws();
  delay(250);
  lay();
  pidEnc(0.5, 0.04, 0.5, -750, 580, 1);
  delay(50);
}

void lay() {
  close_claws();
  if (0 <= collected_tubes && collected_tubes < 3) {
    arm(max_pos - collected_tubes);
    // delay(time_calc(max_pos - collected_tubes));
    collected_tubes++;
  }
  // delay(50);
}

void put() {
  if (0 < collected_tubes && collected_tubes <= 3) {
    collected_tubes--;
    arm(max_pos - collected_tubes);
    delay(time_calc(max_pos - collected_tubes));
    delay(100);
  }
  close_claws();
  delay(150);
  arm(0);
  delay(time_calc(0));
  delay(200);
  open_claws(8);
  delay(100);
  arm_deg(82, 8);
  // podexatb
  pidEnc(0.4, 0.01, 0.5, 850, 1050, 0);
  pidEnc(0.4, 0.01, 0.5, 450, 220, 1);
  arm(0, 9);
  delay(200);
  // ot'exatb
  pidXN(-800, 1);
  arm(3);
}

const byte claw_nums[] = { 2, 4 };
const byte claw_open[] = { 124, 61 };
const byte claw_closed[] = { 58, 129 };

void open_claws() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  char cmd[] = { 'S', 'E', 'R', 'V' };
  send_command(cmd, claw_nums[0], claw_open[0]);
  send_command(cmd, claw_nums[1], claw_open[1]);
  Wire.endTransmission();
}

void open_claws(int delay_ms) {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  char cmd[] = { 'S', 'E', 'R', 'V' };

  // Плавное открытие
  byte start_pos1 = claw_closed[0];
  byte start_pos2 = claw_closed[1];
  byte end_pos1 = claw_open[0];
  byte end_pos2 = claw_open[1];

  for (int i = 0; i <= 66; i++) {
    byte current_pos1 = map(i, 0, 66, start_pos1, end_pos1);
    byte current_pos2 = map(i, 0, 66, start_pos2, end_pos2);

    send_command(cmd, claw_nums[0], current_pos1);
    send_command(cmd, claw_nums[1], current_pos2);
    Wire.endTransmission();
    delay(delay_ms);
    Wire.beginTransmission(I2C_ADDRESS);  // Начинаем новую передачу
  }
}

void close_claws() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  char cmd[] = { 'S', 'E', 'R', 'V' };
  for (int i = 0; i < 2; i++) {
    send_command(cmd, claw_nums[i], claw_closed[i]);
  }
  Wire.endTransmission();
}

const byte cam_pos[] = { 153, 35 };
const byte cam_num = 5;
byte last_cam = 0;

void cam(byte num_pos, int del) {
  int dist = abs(last_cam - cam_pos[num_pos]);
  for (int i = last_cam; i != cam_pos[num_pos]; cam_pos[num_pos] > last_cam ? i++ : i--) {
    send_servo(cam_num, i);
    delay(del);
  }
  last_cam = cam_pos[num_pos];
}
void cam(byte num_pos) {
  cam(num_pos, 0);
}


const byte diagonal[4] = { 91, 86, 86, 90 };
const byte forward[4] = { ASF, BSF, CSF, DSF };
const byte abcd[4] = { 0, 1, 6, 7 };

void all_forward() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  for (int i = 0; i < 4; i++)
    send_servo(abcd[i], forward[i]);
  Wire.endTransmission();
}
void all_diagonal() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  for (int i = 0; i < 4; i++)
    send_servo(abcd[i], diagonal[i]);
  Wire.endTransmission();
}



void send_servo(uint8_t servo_num, uint8_t angle) {
  char cmd[] = { 'S', 'E', 'R', 'V' };
  send_command(cmd, servo_num, angle);
}
void send_rgb(uint8_t r, uint8_t g, uint8_t b) {
  char cmd[] = { 'R', 'G', 'B', ' ' };
  send_command(cmd, r, g, b);
}


void send_command(char command[4], uint8_t arg) {
  for (int charnum = 0; charnum < 4; charnum++)
    Wire.write(command[charnum]);
  Wire.write(arg);
  Wire.write(255);
  Wire.write(255);
  Wire.endTransmission();
}
void send_command(char command[4], uint8_t arg1, uint8_t arg2) {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  for (int charnum = 0; charnum < 4; charnum++)
    Wire.write(command[charnum]);
  Wire.write(arg1);
  Wire.write(arg2);
  Wire.write(255);

  Wire.endTransmission();
}
void send_command(char command[4], uint8_t arg1, uint8_t arg2, uint8_t arg3) {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  for (int charnum = 0; charnum < 4; charnum++)
    Wire.write(command[charnum]);
  Wire.write(arg1);
  Wire.write(arg2);
  Wire.write(arg3);
  Wire.write(255);

  Wire.endTransmission();
}
