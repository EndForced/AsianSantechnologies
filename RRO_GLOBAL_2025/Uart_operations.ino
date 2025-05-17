const String commands[] = {"Beep", "Reset", "Turn", "Button_skip"};
const int commandsCount = 4;
String parameters[10];
int paramCount = 0;
//Beep optional: millis, freq
//Reset - resetting
// Turn - Left/Right, optional - int num, int speed

void uartProcessing() {
  if (Serial1.available()) {
    String uart_data = Serial1.readStringUntil('\n');
    uart_data.trim();
    String command = readUntilSpace(uart_data);

    Serial.print("Received: ");
    Serial.print(uart_data);
    Serial.print("\nCommand: ");
    Serial.println(command);

    int num = find(command, commands, commandsCount); // индекс команды для свитчкейса
    splitIntoParameters(uart_data, parameters, paramCount);

    switch (num) {
      case 0: // "Beep"
        switch (paramCount) {

          case 0:
            beep(G4, 500);
            break;
          case 1:
            beep(G4, parameters[0].toInt());
          case 2:
            beep(parameters[0].toInt(), parameters[1].toInt());
            break;
          default :
            beep(G4, 500);
        }
        SendData("Beeping done");
        break;

      case 1: // "Reset"
        SendData("Resetting...");
        Serial.println("Resetting...");
        delay(100);
        esp_restart();
        break;

      case 2: //turn
        switch (paramCount) {
          case 0:
            SendData("No parameters in turn");
          case 1:
            SendData("Turning...");
            break;
        }


      case 3: //button skip
      //need isParams func (bool)
        switch (paramCount) {
          case 0:
            SendData("Button Activated!");
            break;
          //btn flag change
          case 1:
            SendData("Cant process parameters in Button_skip");
            break;
        }


      case -1:
        SendData("Unknown command");
        break;
    }
  }
  Serial.read();
  delay(150);
}

String readUntilSpace(const String& input) {
  int spaceIndex = input.indexOf(' ');
  if (spaceIndex == -1) {
    return input;
  }
  return input.substring(0, spaceIndex);
}

int find(const String& item, const String list[], int size) {
  for (int i = 0; i < size; i++) {
    Serial.println(list[i]); Serial.println(item);
    if (list[i] == item) {
      int num = i;
      return num;
      break;
    }
  }
  return -1;
}

void splitIntoParameters(const String &data, String* parameters, int count) {
  // вот сюда точно лучше не лезть
  int space_positions[10];
  int count_parameters = 0;

  for (int i = 0; i < data.length(); i++) {
    if (data.charAt(i) == ' ') {
      space_positions[count] = i;
      count++;
    }
  }

  if (count == 0) {
    parameters[0] = "end";
    return;
  }

  space_positions[count] = data.length();
  count++;


  for (int i = 0; i < count - 1; i++) {
    parameters[count_parameters] = data.substring(space_positions[i] + 1, space_positions[i + 1]);
    count_parameters++;
  }

  parameters[count_parameters] = "end";
}

void SendData(String message) {
  Serial1.flush();         // Ждём отправки предыдущих данных
  Serial1.println(message);
}
