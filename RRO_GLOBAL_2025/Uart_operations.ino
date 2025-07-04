const String commands[] = { "Reset", "Beep", "Turn", "Pid", "Up", "Down", "Grab", "Put", "T", "Button_skip", "Direction", "Elevation", "Tubes", "MyFloor", "Route", "RRR" };
const int commandsCount = 14;
String parameters[10];
int paramCount = 0;

bool ramp_last = 0;

void uartProcessing() {
  if (Serial1.available()) {
    String uart_data = Serial1.readStringUntil('\n');
    uart_data.trim();

    if (uart_data.length() == 0) return;

    String command = readUntilSpace(uart_data);
    int commandIndex = findCommandIndex(command, commands, commandsCount);

    // SendData("Received: " + uart_data);

    Serial.print("Received: ");
    Serial.println(uart_data);
    Serial.print("Command: ");
    Serial.println(command);
    Serial.print("Command index: ");
    Serial.println(commandIndex);

    splitIntoParameters(uart_data, parameters, paramCount);

    if (ramp_last and commandIndex != 4 and commandIndex != 5) ramp_last = 0;
    switch (commandIndex) {
      case 0: handleResetCommand(); break;  // "Reset"
      case 1: handleBeepCommand(); break;   // "Beep"

      case 2: handleTurnCommand(); break;  // "Turn"
      case 3: handlePidCommand(); break;   // "Pid"
      case 4: handleUpCommand(); break;    // "Up"
      case 5: handleDownCommand(); break;  // "Down"
      case 6: handleGrabCommand(); break;  // "Grab"
      case 7: handlePutCommand(); break;   // "Put"

      case 8: handleServoCommand(); break;  // "Servo"

      case 9: handleButtonSkipCommand(); break;  // "Button_skip"
      case 10: handleDirCommand(); break;        // "Dir_swap"
      case 11: handleElevationCommand(); break;  // "Elevation_swap"
      case 12: handleTubesCommand(); break;      // "Tubes"

      case 13: handleMyFloorCommand(); break;    // "MyFloor"

      case 14: handleRoute();  //Route
      case 15: handleRoute();  // RRR

      default:                 // we fucking dont know whut is it
        SendData("Unknown command: " + command);
        break;
    }
  }
  delay(50);
}

// command holders

#define G4 391

void handleBeepCommand() {
  switch (paramCount) {
    case 0:
      beep(G4, 500);
      break;
    case 1:
      beep(G4, parameters[0].toInt());
      break;
    case 2:
      beep(parameters[0].toInt(), parameters[1].toInt());
      break;
    default:
      beep(G4, 500);
  }
  SendData("Beeping done");
}

void handleResetCommand() {
  SendData("Resetting...");
  Serial.println("Resetting...");
  delay(100);
  esp_restart();
}

void handleGrabCommand() {
  grab();
  SendData("Grab");
  Serial.println("Grab");
}

void handlePutCommand() {
  put();
  SendData("Put");
  Serial.println("Put");
}

void handleUpCommand() {
  go_up(dir * (ramp_last + 1));
  // stop();
  SendData("Up");
  Serial.println("Up");
}

void handleDownCommand() {
  go_down(dir * (ramp_last + 1));
  SendData("Down");
  Serial.println("Down");
}

void handleTurnCommand() {
  if (paramCount == 0) {
    SendData("Error: No direction specified");
    return;
  }

  String direction = parameters[0];
  int steps = (paramCount > 1) ? parameters[1].toInt() : 1;
  int speed = (paramCount > 2) ? parameters[2].toInt() : 850;
  int way = (direction == "Left") ? -1 : 1;

  turn_to_line(speed, way, dir, steps);

  // Andrew's Job
  SendData("Turning " + direction + " speed " + String(speed));
}

void handlePidCommand() {
  if (paramCount == 0) {
    SendData("Error: No direction specified");
    return;
  }

  String direction = parameters[0];
  int steps = (paramCount > 1) ? parameters[1].toInt() : 1;
  int speed = (paramCount > 2) ? parameters[2].toInt() : 950;

  int way = (direction == "Forward") ? 1 : -1;

  pidXN(speed * way, steps);

  // Andrew's Job
  SendData("Moving " + direction + " with speed " + String(speed));
}

void handleServoCommand() {
  // Andrew's Job
  SendData("allign ");
}

void handleMyFloorCommand() {
  int datvals = 0;
  for (int i = 1; i < 5; i++) {
    datvals += sensor_x(i);
  }
  if (datvals / 4 < 500) {
    SendData("2");
    inverse = 1;
  } else {
    SendData("1");
    inverse = 0;
  }
}

// String identifier = parameters[0];
// if (isdigit(identifier[0])){}
// int steps = (paramCount > 1) ? parameters[1].toInt() : 1;
// int way = (direction == "Forward") ? 1 : -1;

// pidXN(speed * way, steps);

// Andrew's Job
// SendData("Moving " + direction + " with speed " + String(speed));


void handleButtonSkipCommand() {
  if (paramCount > 0) {
    SendData("Warning: Button_skip doesn't accept parameters");
  }
  //btn flag change
  SendData("Button activated");
}

void handleDirCommand() {
  if (paramCount == 0) {
    SendData("Error: No mode specified");
    return;
  }

  int new_dir = parameters[0].toInt();
  if (new_dir == 1 or new_dir == -1)
    dir = new_dir;
  else {
    SendData("Error: direction non-existant (dir must be a 1 or -1)");
    return;
  }

  SendData("Direction swiched to " + String(dir));
}

void handleElevationCommand() {
  if (paramCount == 0) {
    SendData("Error: No level specified");
    return;
  }

  int new_level = parameters[0].toInt();
  if (new_level == 1 or new_level == 2)
    inverse = new_level - 1;
  else {
    SendData("Error: level non-existant (level must be a 1 or 2)");
    return;
  }

  SendData("Level swiched to " + String(inverse + 1));
}

void handleTubesCommand() {
  if (paramCount == 0) {
    SendData("Error: No tubes count specified");
    return;
  }

  int new_tubes = parameters[0].toInt();
  if (new_tubes >= 0 and new_tubes <= 3)
    collected_tubes = new_tubes;
  else {
    SendData("Error: tubes number non-existant (must be between 0 or 3)");
    return;
  }

  SendData("Tubes swiched to " + collected_tubes);
}


void handleRoute() {

}


















// dont touch bro!!
String readUntilSpace(const String& input) {
  int spaceIndex = input.indexOf(' ');
  return (spaceIndex == -1) ? input : input.substring(0, spaceIndex);
}

int findCommandIndex(const String& command, const String commands[], int size) {
  for (int i = 0; i < size; i++) {
    if (commands[i] == command) {
      return i;
    }
  }
  return -1;
}

void splitIntoParameters(const String& data, String* parameters, int& count) {
  count = 0;
  int startPos = data.indexOf(' ');

  if (startPos == -1) {
    return;
  }

  startPos++;
  int spacePos = startPos;


  while (spacePos < data.length() && count < 10) {
    spacePos = data.indexOf(' ', startPos);

    if (spacePos == -1) {
      parameters[count++] = data.substring(startPos);
      break;
    }

    parameters[count++] = data.substring(startPos, spacePos);
    startPos = spacePos + 1;
  }

  //resetting remains of massive
  for (int i = count; i < 10; i++) {
    parameters[i] = "";
  }
}

void SendData(String message) {
  //for uarts stability
  Serial1.flush();
  Serial1.println(message);
}





void do_smth(String str)
{
  char ch = str[0];
  int num = str[1] - '0';

  switch (ch)
  {
    case 'X':
      if (num > 0)
        pidXN(1000, num % 8);
      break;
    case 'x':
      if (num > 0)
        pidXN(-1000, num % 8);
      break;
    case 'R':
      if (num > 0)
        turn_to_line(900, 1, 1, num % 4);
      break;
    case 'r':
      if (num > 0)
        turn_to_line(900, 1, -1, num % 4);
      break;
    case 'L':
      if (num > 0)
        turn_to_line(900, -1, 1, num % 4);
      break;
    case 'l':
      if (num > 0)
        turn_to_line(900, -1, -1, num % 4);
      break;

    case 'G':
      grab();
      break;

    case 'P':
      put();
      break;

    case 'U':
      go_up(1);
      break;
    case 'u':
      go_up(-1);
      break;

    case 'D':
      go_down(1);
      break;
    case 'd':
      go_down(-1);
      break;
  }
}
void read_string_and_do() {
  int index = 0;
  while (moves[index]) {
    do_smth(moves[index]);
    index++;
  }
  buttonWait(0);
}
