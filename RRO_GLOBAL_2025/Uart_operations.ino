const String commands[] = {"Beep", "Reset"};
const int commandsCount = 2;
String parameters[10];


void uartProcessing() {
  //тут все +- понятно
  if (Serial1.available()) {
    String uart_data = Serial1.readStringUntil('\n');
    uart_data.trim();
    String command = readUntilSpace(uart_data);

    Serial.print("Received: ");
    Serial.print(uart_data);
    Serial.print("\nCommand: ");
    Serial.println(command);

    int num = find(command, commands, commandsCount); // индекс команды для свитчкейса (умно)
    switch (num) {
      case 0: // "Beep"
        break;
      case 1: // "Reset"
        Serial1.println("Resetting...");
        delay(100);
        esp_restart();
        break;
      case -1:
        Serial1.println("Unknown command");
        break;
    }
  }
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
    if (list[i] == item) {
      int num = i;
      break;
    }
  }
  return -1;
}

void splitIntoParameters(const String &data, String* parameters) {
  // вот сюда точно лучше не лезть
  int space_positions[10];
  int count = 0;
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
