/*----------------------SENSORS-------------------------*/
#define sa 13
#define sb 11
#define sc 16
#define sd 7

#define xsa 14
#define xsb 12
#define xsc 15
#define xsd 6

float sensor(int dat) {
  float data = 0;

  uint16_t datamin = 10;
  uint16_t datbmin = 10;
  uint16_t datcmin = 10;
  uint16_t datdmin = 10;

  uint16_t datamax = 3800;
  uint16_t datbmax = 3800;
  uint16_t datcmax = 3800;
  uint16_t datdmax = 3800;

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

  return constrain(data * 256.0, 0, 256);
}

float sensor_x(int dat) {
  float data = 0;

  uint16_t datamin = 10;
  uint16_t datbmin = 10;
  uint16_t datcmin = 10;
  uint16_t datdmin = 10;

  uint16_t datamax = 3800;
  uint16_t datbmax = 3800;
  uint16_t datcmax = 3800;
  uint16_t datdmax = 3800;

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

  return constrain(data * 256.0, 0, 256);
}


