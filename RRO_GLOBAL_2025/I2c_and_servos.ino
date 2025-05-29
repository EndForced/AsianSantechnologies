#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#define I2C_ADDRESS 0x0A  // Change this if needed
#define RGB_PIN 48
#define NUMPIXELS 3

Adafruit_NeoPixel pixels(NUMPIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);

/*------------------------------A---B---CL1-ARM-CL2-CAM-C---D-*/
const int base_positions[8] = { 93, 87, 90, 10, 90, 90, 86, 88 };

#define ASF 140
#define BSF 40
#define CSF 135
#define DSF 45

void servos_init() {
  Wire.begin();  // Join I2C bus as master
  Wire.setClock(1000000);

  send_rgb(0, 0, 0);
  delay(10);
  send_servo(3, 80);
  delay(10);
  // open_claws();
  all_forward();
  delay(900);
}

const byte arm_num = 3;
const byte arm_positions[] = { 100, 90, 50, 30, 10 };  // from stand to last tube

byte last_arm_pos = 10;
void arm(byte num_of_pos) {
  byte distance = abs(arm_position[num_of_pos] - last_arm_pos);
  for (int i = last_arm_pos; i != arm_position[num_of_pos]; arm_position[num_of_pos] > last_arm_pos ? i++ : i--) {
    send_servo(arm_num, i);
    delay((i < distance * 0.3 or i > distance * 0.7) ? 3 : 6);
  }
  last_arm_pos = arm_position[num_of_pos];
}

void grab() {
  open_claws();
  arm(0);
  pidEnc(1.5, 0.1, 1, 800, 700, 1);
  arm(1);
  close_claws();
  delay(100);
  pidEnc(1.5, 0.1, 1, -800, 700, 1);
}

const byte claw_nums[] = { 2, 4 };
const byte claw_open[] = { 130, 51 };
const byte claw_closed[] = { 50, 131 };

void open_claws() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  char cmd[] = { 'S', 'E', 'R', 'V' };
  send_command(cmd, claw_nums[0], claw_open[0]);
  send_command(cmd, claw_nums[1], claw_open[1]);
  Wire.endTransmission();
}

void close_claws() {
  Wire.beginTransmission(I2C_ADDRESS);  // Slave address
  char cmd[] = { 'S', 'E', 'R', 'V' };
  for (int i = 0; i < 2; i++) {
    send_command(cmd, claw_nums[i], claw_closed[i]);
  }
  Wire.endTransmission();
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