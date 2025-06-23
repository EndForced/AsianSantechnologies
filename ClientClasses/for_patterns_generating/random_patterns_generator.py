import random
import math
import time

from Future_engeneers_path_creation import wave_ini, neighbour_ini, print_colored, replace_ints_in_matrix
from Future_engeneers_path_creation_old import create_path
import copy
from exel_stuff import write, write_to_existing, replace_ints_in_matrix_rev


field_mat = [[70, 70 ,70, 70, 70, 70, 70, 70], #tipo fild mat, cho neponyatnogo?
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],
	         [70, 70 ,70, 70, 70, 70, 70, 70],]

patterns = [[33,10,10,10,32],
            [33,10,10,32],
            [10,10,10,32],
            [10,10,10,32],
            [10,10,32],
            [10,10,32],
            [33,32],
            [10,10],
            [10],
            [10],
            [10]
] #patterns (feel free to change)



params = [ 0, #lvl of debugging 0 - nothing, 1 - intermediate ways + fatal errors, 2 - all from 1 + info about path building
		   0, #ramp checkment. Includes ramps while path building. If ramp amount > 10 can slow program a lot
		   0, # works don't properly!1!1 if 0 - displaying the shortest path, if not 0 - longest (but return shortest in both cases) // can be useful for debugging
		   0, # funny sound after path buildment
		   0, #animation for final way
		   0, #launch type. 0 - usual launch, 1 - only map ini, 2 - wave ini
           1 # special parameter for pattern generating
]


num = 100 #num of tries before restart generating procedure
between_tubes = 5 #minimal distance between any two tubes (vector)  (don't put anything above 7 plzz) #can really slow down program if > 5
dummy_count = 0

def rotate_patterns(dir,pat):
    #dir 0 - up 1 - down 2 - right 3 - left
    if dir == 3:
        return pat

    elif dir == 2:
        return pat[::-1]

    else:
        pat = "".join([str(i) for i in pat]) #это я сам написал (честн)

        replacements = { "32": "30", "33": "31"}
        for old, new in replacements.items():
            pat = pat.replace(old, new)

        if dir == 1:
            pat_out = []
            for i in range(0, len(pat), 2):
                pat_out.append(int(pat[i:i + 2]))
            return pat_out


        elif dir == 0:
            pat_out = []
            for i in range(0, len(pat), 2):
                pat_out.append(int(pat[i:i + 2]))
            return pat_out[::-1]

        else:
            print("unknown direction while pat rotating!11!!1 dir: ", dir)

def pattern_placer(mat,patts):
    #that one was kinda hard (because im really dummy ass)
    global num

    patterns = copy.deepcopy(patts) #не люблю скрытые зависимости...
    trynum = 0 #счетчик попыток

    while patterns: # пока есть что ставить

        pattern = random.choice(patterns) #выбираем
        state = False #пока не поставили

        while state != True:
            dir = random.randint(0,3) #выбираем направление паттерна
            pat = rotate_patterns(dir,pattern) #поворачиваем его
            start_point = (random.randint(0,7),random.randint(0,7)) #рандомайзим

            if dir == 0: #распишу только одно направление
                if start_point[0] - len(pat) > -1: #если паттерн целиком влазит
                    mat_tmp = copy.deepcopy(mat) #создаем временную матрицу
                    for i in range(len(pat)):
                        if mat[start_point[0] - i][start_point[1]] == 70: #если клетка свободна - записываем
                            mat_tmp[start_point[0] - i][start_point[1]] = pat[i] #запись во временную матрицу
                        else: #если клетка в которую хотим записать - занята
                            trynum+=1
                            break #делаем реролл
                        if i == len(pat)-1: #если мы смогли записать весь паттерн
                            state = True
                            patterns.remove(pattern) #удаляем что записали
                            mat = mat_tmp #превращаем временную матрицу в постоянную

            if dir == 1:
                if start_point[0] + len(pat) < 8:
                    mat_tmp = copy.deepcopy(mat)
                    for i in range(len(pat)):
                        if mat[start_point[0] + i][start_point[1]] == 70:
                            mat_tmp[start_point[0] + i][start_point[1]] = pat[i]
                        else:
                            trynum+=1
                            break
                        if i == len(pat)-1:
                            state = True
                            patterns.remove(pattern)
                            mat = mat_tmp


            if dir == 2:
                if start_point[1] - len(pat) > -1:
                    mat_tmp = copy.deepcopy(mat)
                    for i in range(len(pat)):
                        if mat[start_point[0]][start_point[1]-i] == 70:
                            mat_tmp[start_point[0]][start_point[1]-i] = pat[i]
                        else:
                            trynum+=1
                            break
                        if i == len(pat)-1:
                            state = True
                            patterns.remove(pattern)
                            mat = mat_tmp


            if dir == 3:
                if start_point[1] + len(pat) < 8:
                    mat_tmp = copy.deepcopy(mat)
                    for i in range(len(pat)):
                        if mat[start_point[0]][start_point[1]+i] == 70:
                            mat_tmp[start_point[0]][start_point[1]+i] = pat[i]
                        else:
                            trynum+=1
                            break
                        if i == len(pat)-1:
                            state = True
                            patterns.remove(pattern)
                            mat = mat_tmp

            if trynum > num:
                return None

    return(mat)

def tube_placement(mat,waves_all):
    global num
    global between_tubes

    cords_f = []
    cords_s = []
    first_count = 0
    second_count = 0
    trynum = 0

    while first_count != 2 or second_count != 1:
        cord = random.choice(waves_all) #роллим из всех волн


        if mat[cord[0]][cord[1]] == 70 and first_count != 2: #если нароллили первый этаж + трубы еще можно ставить
            vecs = []
            if first_count == 1: #добавляем расстояние до других труб если таковые есть
                vecs.append(math.dist(cord,cords_f[0])) #ну вы поняли

            if second_count == 1: #так же и со вторым этажом
                vecs.append(math.dist(cord,cords_s[0]))

            if vecs:
                if min(vecs) < between_tubes: #если какая-то из труб ближе чем нужно, то выходим из функции (надо бы чуть оптимизировать это по идее...)
                    return None

            mat[cord[0]][cord[1]] = int("704"+str(random.randint(0,1))) #если все таки зароллили несто подходящее, то записываем его, да еще и с рандомной ориентацией!1
            cords_f.append(cord)
            first_count += 1


        if mat[cord[0]][cord[1]] == 10 and second_count != 1: #тут +- то же, только для второго этажа
            #вы не представляете, в каких обстоятельствах я пишу эти комментарии (в смешных) (и очень маловероятных)
            vecs = []
            if first_count:
                for u in range(first_count):
                    vecs.append(math.dist(cord, cords_f[u]))

            if vecs:
                if min(vecs) < between_tubes:
                    return None


            mat[cord[0]][cord[1]] = 1041
            second_count += 1
            cords_s.append(cord)


        if mat[cord[0]][cord[1]] == 11 and second_count != 1:

            vecs = []
            if first_count:
                for u in range(first_count):
                    vecs.append(math.dist(cord, cords_f[u]))

            if vecs:
                if min(vecs) < between_tubes:
                    return None


            mat[cord[0]][cord[1]] = 1140
            second_count += 1
            cords_s.append(cord)

        trynum += 1


        if trynum > num:
            return None


    return(mat)

def unload_point_place(mat,waves_all):
    global num

    num_count = 0
    state = False
    while not state:
        dir = random.randint(0, 3)

        if dir == 0:
            cord_to_start = (7,random.randint(0,5))
            for i in range(3):
                if mat[7][cord_to_start[1]+i] == 70 and mat[6][cord_to_start[1]+i] == 70 and (6,cord_to_start[1]+i) in waves_all:
                    pass

                else:
                    num_count += 1
                    break

                if i == 2:
                    for j in range(3):
                        mat[7][cord_to_start[1] + j] = 61
                    state = True



        if dir == 1:
            cord_to_start = (0, random.randint(2, 7))
            for i in range(3):
                if mat[0][cord_to_start[1] - i] == 70 and mat[1][cord_to_start[1] - i] == 70 and (1,cord_to_start[1] - i) in waves_all :
                    pass

                else:
                    num_count += 1
                    break

                if i == 2:
                    for j in range(3):
                        mat[0][cord_to_start[1] - j] = 60
                    state = True



        if dir == 2:
            cord_to_start = (7,random.randint(0, 5))
            for i in range(3):
                if mat[cord_to_start[1]+i][0] == 70 and mat[cord_to_start[1]+i][1] == 70 and (cord_to_start[1]+i,1) in waves_all:
                    pass

                else:
                    num_count += 1
                    break

                if i == 2:
                    for j in range(3):
                        mat[cord_to_start[1] + j][0] = 62
                    state = True



        if dir == 3:
            cord_to_start = (7,random.randint(2, 7))
            for i in range(3):
                if mat[cord_to_start[1]-i][7] == 70 and mat[cord_to_start[1]-i][6] == 70 and (cord_to_start[1]-i,6) in waves_all:
                    pass

                else:
                    num_count += 1
                    break

                if i == 2:
                    for j in range(3):
                        mat[cord_to_start[1] - j][7] = 63
                    state = True

        num_count += 1

        if num_count > num:
            return None



    return(mat)

def my_pos(mat):

    while 1:
        pos = (random.randint(0,7),random.randint(0,7))

        if mat[pos[0]][pos[1]] == 70:
            # mat[pos[0]][pos[1]] = 7050
            return pos

def generate_some(pat_num):

    if pat_num > 100:
        generated = 0
        for i in range(0,round(pat_num/100)):
            while generated < 100:
                mat_out = copy.deepcopy(field_mat)
                mat_out = pattern_placer(copy.deepcopy(mat_out), patterns)

                if mat_out:
                    my_pos_huh = my_pos(mat_out)
                    cells = neighbour_ini(mat_out)
                    waves = wave_ini(my_pos_huh, cells)
                    waves_all = []

                    for i in waves:
                        for k in i:
                            waves_all.append(k)

                    mat_out[my_pos_huh[0]][my_pos_huh[1]] = 7050
                    mat_out = tube_placement(mat_out, waves_all)

                    if mat_out:
                        mat_out = unload_point_place(mat_out, waves_all)
                        if mat_out:
                            mat_out = replace_ints_in_matrix_rev(mat_out)
                            path = create_path(mat_out, params)
                            if path:
                                to_write = [mat_out]
                                write(to_write)
                                generated += 1
                                print("+1!")

        write_to_existing()
        print("cycle passed")

    else:
        gen = 0
        while gen < pat_num:
            mat_out = copy.deepcopy(field_mat)
            mat_out = pattern_placer(copy.deepcopy(mat_out), patterns)

            if mat_out:
                my_pos_huh = my_pos(mat_out)
                cells = neighbour_ini(mat_out)
                waves = wave_ini(my_pos_huh, cells)
                waves_all = []

                for i in waves:
                    for k in i:
                        waves_all.append(k)

                mat_out[my_pos_huh[0]][my_pos_huh[1]] = 7050
                mat_out = tube_placement(mat_out, waves_all)

                if mat_out:
                    mat_out = unload_point_place(mat_out, waves_all)
                    if mat_out:
                        path = create_path(mat_out, params)
                        if path:
                            to_write = [replace_ints_in_matrix_rev(mat_out)]
                            write(to_write)
                            gen += 1
                            print("+1!")

    write_to_existing()
    print_colored("cycle passed","green")

#generates patterns. If u opened project from archive and gonna generate some pats, just run this file and wait.
#ps, I already created smth like 1000 patterns with between tubes parametr = 5, seems like we don't need more.
#all pats are in pats_all.xlsx
while 1:
    generate_some(10)
    time.sleep(3)


