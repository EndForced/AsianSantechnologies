commands_dict = {"R" : "Turn Left", "L": "Turn Right", "X": "Pid Forward", "x": "Pid Backwards", "F0": "Up", "F1": "Down"}
commands = ["X2", "F1", "X2"]
for i in range(len(commands)):
    if len(commands[i]) == 2:
        if commands[i][0] != "F":
            command = commands[i][0]
            num = commands[i][1]
            commands[i] = f"{commands_dict[command]} {num}"

        elif commands[i][0] == "F":
            command = commands[i]
            commands[i] = f"{commands_dict[command]}"


print(commands)