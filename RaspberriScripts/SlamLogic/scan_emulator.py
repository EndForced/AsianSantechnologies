import numpy as np
#я написал это в поезде до этого не спав сутки


class ScanEmulator:
    def __init__(self, mat):
        self.matr = np.array(mat)
        robot_cord = []

        for i in range(len(mat)):
            for j in range(len(mat)):
                if self.matr[i][j] in [71, 81]:
                    robot_cord = (i,j)
                    self.matr[i][j] = 10 if self.matr[robot_cord] == 71 else 20

        yr, xr = robot_cord
        self.cord_correction = (8-yr, 8-xr)

    def reveal(self, cord, dir):
        borders = []
        goodramp = []
        if dir == "U": goodramp = 31
        if dir == "R": goodramp = 32
        if dir == "D": goodramp = 33
        if dir == "L": goodramp = 34




        y,x = cord
        ycorr, xcorr= self.cord_correction
        realcord = (y - ycorr,x - xcorr)
        if min(realcord) <= -1  or max(realcord) >= len(self.matr) :
            print("can't handle this coords, ", cord, realcord)
            return

        y,x = realcord

        if dir not in ["U","R","D","L"]: print("Strange dir while fake revealing ",dir )

        revealcords = {
            "U": [(y-1, x+1), (y-1 , x), (y-1, x-1), (y-2, x+1), (y-2, x), (y-2, x-1)],
            "D": [(y+1, x-1), (y+1 , x), (y+1, x+1), (y+2, x-1), (y+2, x), (y+2, x+1)],
            "R": [(y+1, x+1), (y, x+1), (y-1, x+1), (y+1, x+2), (y, x+2), (y-1, x+2)],
            "L": [(y-1, x-1), (y, x-1), (y+1, x-1), (y-1,x-2), (y, x-2), (y+1, x-1)]
        }
        sec_fl = []

        res = []
        for i in range(len(revealcords[dir])):
            if max(revealcords[dir][i]) <= len(self.matr)-1 and min(revealcords[dir][i]) > -1:

                cord = revealcords[dir][i]
                res.append(int(self.matr[cord]))


            else:
                res.append("unr")
                if not borders:

                    if dir == "U":
                        if realcord[0] == 0:
                            borders.append("fc")
                        elif realcord[0] == 1 and self.matr[realcord[0]][realcord[1]] != 20:
                            borders.append("ff")

                    if dir == "D":
                        if realcord[0] == 7:
                            borders.append("fc")
                        elif realcord[0] == 6 and self.matr[realcord[0]][realcord[1]] != 20:
                            borders.append("ff")

                    if dir == "R":
                        print(realcord)
                        if realcord[1] == 7:
                            borders.append("fc")
                        elif realcord[1] == 6 and self.matr[realcord[0]][realcord[1]] != 20:
                            borders.append("ff")

                    if dir == "L":
                        print(realcord)
                        if realcord[1] == 0:
                            borders.append("fc")
                        elif realcord[0] == 1 and self.matr[realcord[0]][realcord[1]] != 20:
                            borders.append("ff")
                else:
                    if self.matr[realcord]!= 20: borders.append("ff")

            lst = [20, 52, 52, 31, 32, 33, 34]
            lst.remove(goodramp)
            if res[i] in lst :
                sec_fl.append(i)

        if 0 in sec_fl: res[3] = "unr"
        if 1 in sec_fl: res[4] = "unr"
        if 2 in sec_fl: res[5] = "unr"

        return list(res), borders

def dummy_def(commands):
    commands_dict = {"L": "Turn Left", "R": "Turn Right", "X": "Pid Forward", "x": "Pid Backwards", "F1": "Up",
                     "F0": "Down", "G0": "Grab", "P1": "Put"}
    for i in range(len(commands)):
        if len(commands[i]) == 2:
            if commands[i][0] not in ["F", "P", "G"]:
                command = commands[i][0]
                num = commands[i][1] if commands[i][1] else ""
                commands[i] = f"{commands_dict[command]} {num}"

            elif commands[i][0] in ["F", "P", "G"]:
                command = commands[i]
                commands[i] = f"{commands_dict[command]}"

    return commands

fm = [[20, 20, 34, 10, 20, 42, 10, 10],
      [10, 10, 10, 32, 34, 10, 10, 10],
      [10, 32, 20, 20, 34, 10, 10, 62],
      [10, 32, 20, 20, 20, 20, 10, 62],
      [20, 10, 20, 10, 10, 71, 10, 62],
      [20, 20, 20, 20, 34, 10, 10, 42],
      [20, 42, 20, 20, 20, 34, 10, 10],
      [33, 10, 10, 10, 10, 10, 20, 10]]
se = ScanEmulator(fm)
rev = se.reveal((8,8),"U")
print(rev)