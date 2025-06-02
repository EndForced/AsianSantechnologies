const String commands[] = { "Beep", "Reset", "Turn", "Pid", "Up", "Down", "Grab", "Put", "Button_skip", "Mode_swap", "Elevation_swap", "Tubes" };
const int commandsCount = 4;
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

    Serial.print("Received: ");
    Serial.println(uart_data);
    Serial.print("Command: ");
    Serial.println(command);
    Serial.print("Command index: ");
    Serial.println(commandIndex);

    splitIntoParameters(uart_data, parameters, paramCount);
    if (ramp_last and commandIndex != 4 and commandIndex != 5) ramp_last = 0;
    switch (commandIndex) {
      case 0: handleBeepCommand(); break;   // "Beep"
      case 1: handleResetCommand(); break;  // "Reset"

      case 2: handleTurnCommand(); break;  // "Turn"
      case 3: handlePidCommand(); break;   // "Pid"
      case 4: handleUpCommand(); break;    // "Up"
      case 5: handleDownCommand(); break;  // "Down"
      case 6: handleGrabCommand(); break;  // "Grab"
      // case 7: handlePutCommand(); break;   // "Put"

      case 8: handleButtonSkipCommand(); break;  // "Button_skip"
      case 9: handleBeepCommand(); break;        // "Beep"
      case 10: handleBeepCommand(); break;       // "Beep"


      default:  // we fucking dont know whut is it
        SendData("Unknown command: " + command);
        break;
    }
  }
  delay(150);
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

void handleUpCommand() {
  go_up(dir * (ramp_last + 1));
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
  int speed = (paramCount > 1) ? parameters[1].toInt() : 1000;
  int steps = (paramCount > 2) ? parameters[2].toInt() : 1;
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
  int speed = (paramCount > 2) ? parameters[2].toInt() : 900;

  int way = (direction == "Forward") ? 1 : -1;

  pidXN(speed * way, steps);

  // Andrew's Job
  SendData("Moving " + direction + " with speed " + String(speed));
}

void handleButtonSkipCommand() {
  if (paramCount > 0) {
    SendData("Warning: Button_skip doesn't accept parameters");
  }
  //btn flag change
  SendData("Button activated");
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
