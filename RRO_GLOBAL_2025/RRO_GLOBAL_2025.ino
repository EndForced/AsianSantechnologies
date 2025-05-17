
#include <string.h>

volatile int countl = 0;
volatile int countr = 0;

int inverse = 0;
float e_old = 0;
int err_i = 0;
float sum = 0;
float errors[10] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
float dat1, dat2;
int count = 0;

#define D4 293
#define D5 587
#define A4 440
#define GH4 415
#define G4 391
#define F4 350
#define C4 261
#define C5 523


String data = "MEGA_PID 228 1336 -993";
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, 16, 17);
  Serial.println("Started!");
}

void loop() {
  //   put your main code here, to run repeatedly:
//  String parameters[10];
  //  splitIntoParameters(data, parameters);

  //   while (parameters[count] != "end") {
  //    Serial.println(parameters[count]);
  //    count++;
  uartProcessing();
  delay(50);
//Serial1.println("123");
//delay(10000000);
}
