/*----------------------SENSORS-------------------------*/
#define sa 11
#define sb 7
#define sc 13
#define sd 16

#define xsa 12
#define xsb 6
#define xsc 14
#define xsd 15

int raw(int dat) {
  int data = 0;
  switch (dat) {
    case 1: data = analogRead(sa); break;
    case 2: data = analogRead(sb); break;
    case 3: data = analogRead(sc); break;
    case 4: data = analogRead(sd); break;
    case 5: data = analogRead(xsa); break;
    case 6: data = analogRead(xsb); break;
    case 7: data = analogRead(xsc); break;
    case 8: data = analogRead(xsd); break;
    default: data = 37707; break;
  }

  return data;
}

float sensor(int dat) {
  float data = 0;

  uint16_t datamin = 1300;
  uint16_t datbmin = 1220;
  uint16_t datcmin = 1430;
  uint16_t datdmin = 1290;

  uint16_t datamax = 3990;
  uint16_t datbmax = 4025;
  uint16_t datcmax = 4050;
  uint16_t datdmax = 4020;

  switch (dat) {
    case 1:
      data = float(analogRead(sa) - datamin) / (datamax - datamin);
      break;
    case 2:
      data = float(analogRead(sb) - datbmin) / (datbmax - datbmin);
      break;
    case 3:
      data = float(analogRead(sc) - datcmin) / (datcmax - datcmin);
      break;
    case 4:
      data = float(analogRead(sd) - datdmin) / (datdmax - datdmin);
      break;
  }

  return constrain(data * 1023.0, 0, (1<<10)-1);
}

float sensor_x(int dat) {
  float data = 0;

  uint16_t datamin = 1460;
  uint16_t datbmin = 1080;
  uint16_t datcmin = 1380;
  uint16_t datdmin = 1350;

  uint16_t datamax = 4000;
  uint16_t datbmax = 3830;
  uint16_t datcmax = 4060;
  uint16_t datdmax = 4040;

  switch (dat) {
    case 1:
      data = float(analogRead(xsa) - datamin) / (datamax - datamin);
      break;
    case 2:
      data = float(analogRead(xsb) - datbmin) / (datbmax - datbmin);
      break;
    case 3:
      data = float(analogRead(xsc) - datcmin) / (datcmax - datcmin);
      break;
    case 4:
      data = float(analogRead(xsd) - datdmin) / (datdmax - datdmin);
      break;
  }

  return constrain(data * 1023.0, 0, (1<<10)-1);
}
