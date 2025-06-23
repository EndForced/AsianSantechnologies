from copy import deepcopy
from os import system, name

import cv2 #что бы окошки выводить
# from playsound3 import playsound #что бы звуки включать
import time #что бы время считать

# import ctypes #что бы иконку окна менять
import itertools #что бы проще составлять все возможные комбинации
import copy # что бы list = list1 работало нормально
from itertools import groupby #et hz zachem
import re
import os
import numpy as np
#
# def icon_change():
#     icon_path = "random_funny_stuff/cute_icon.ico"  # Я не знаю как оно работает, если честно, я украл этот код
#
#     icon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x00000010)
#     hwnd = ctypes.windll.user32.FindWindowW(None, "map")
#
#     if hwnd:
#         ctypes.windll.user32.SendMessageW(hwnd, 128, 0, icon)
def replace_ints_in_matrix(matrix):

    replacements = {
        10: 70,
        20: 10,
        32: 33,
        33: 30,
        34: 32,
        41: 7040,
        42: 7041,
        51: 1140,
        52: 1141,
        61: 60,
        62: 63,
        63: 61,
        64: 62,
        71: 7050,
        72: 7052,
        73: 7051,
        74: 7053
    }

    new_matrix = []
    for row in matrix:
        new_row = []
        for element in row:
            if element in replacements:
                new_row.append(replacements[element])
            else:
                new_row.append(element)
        new_matrix.append(new_row)

    return new_matrix

def ini(img, mat): #вывод объектов на экран
    if mat is not None:
        for i in range(len(mat)): # перебираем каждый элемент матрицы и выводим его
            for j in range(len(mat[i])):
                show_smth(mat[i][j], (i, j), img)
        cv2.imshow("map", cv2.resize(img, (600, 600)))
        cv2.waitKey(1)
    else:
        print("Field mat can't be non type object! \n   Programmer u are dummy ass")

def show_smth(code, cords, object):
    if code == 1041:
        code = 1141

    img_path = f"field_pics/{code}.png"

    # Fast existence check and image loading
    if os.path.exists(img_path):
        pic = cv2.imread(img_path)
        if pic is not None and pic.shape[0] == 100 and pic.shape[1] == 100:
            # Direct assignment if all conditions are met
            y_start, y_end = 100 * cords[0], 100 * cords[0] + 100
            x_start, x_end = 100 * cords[1], 100 * cords[1] + 100
            object[y_start:y_end, x_start:x_end] = pic
            cv2.waitKey(1)
            return

    # Fallback path (only executed if above conditions fail)
    pic = np.zeros((100, 100, 3), dtype=np.uint8)
    pic[:] = (0, 0, 255)  # Red placeholder
    y_start, y_end = 100 * cords[0], 100 * cords[0] + 100
    x_start, x_end = 100 * cords[1], 100 * cords[1] + 100

    # Boundary checks to prevent out-of-bounds errors
    height, width = object.shape[:2]
    y_start = max(0, min(y_start, height - 100))
    y_end = y_start + 100
    x_start = max(0, min(x_start, width - 100))
    x_end = x_start + 100

    object[y_start:y_end, x_start:x_end] = pic
    cv2.waitKey(1)

def neighbour_ini(mat):          #определение клеток в которые можно пройти
    #если хочешь что-то менять - помни про инвертированные координаты, i это у, а j это х
    #еще в словаре хранятся координаты вида (y,x) просто так удобнее
    #функция работает с любым размером матрицы который больше 1х1
    #если ты реально собрался что-то менять - good luck)

    neighbour_dict = {}
    for i in range(len(mat)): #для каждого ряда
        for j in range(len(mat[i])): # для каждого элемента каждого ряда
            neighbour_dict[(i, j)] = [] #создание пустого списка клеток в которые можно пройти из конкретной клетки
            if mat[i][j] == 70: #если клетка из которой идем - первый этаж

                if i + 1 < 8 and ((mat[i + 1][j] == 70) or (mat[i + 1][j] == 30)): #если при попытке пройти в + по у мы не выйдем за пределы поля и клетка в которую идем - элемент первого этажа или рампа направленная в нужную сторону то записываем ее в список
                    # print("success")
                    neighbour_dict[(i, j)].append((i + 1, j)) #добавляем в список возможных клеток исходную с измененной координатой

                if i - 1 > -1 and (mat[i - 1][j] == 70 or mat[i - 1][j] == 31):
                    # действуем по аналогии с первым случаем, только рампа в этом случае будет другая тк идем в другую сторону
                    neighbour_dict[(i, j)].append((i - 1, j))

                if j - 1 > -1 and (mat[i][j - 1] == 70 or mat[i][j - 1] == 32):
                    # то же самое
                    neighbour_dict[(i, j)].append((i, j - 1))

                if j + 1 < 8 and (mat[i][j + 1] == 70 or mat[i][j + 1] == 33):
                    # то же самое
                    neighbour_dict[(i, j)].append((i, j + 1))


            #todo uncomment to move freely on sec floor

            elif int(str(mat[i][j])[0]) == 1: # если клетка из которой мы ищем возможные проходы - второй этаж
                if i + 1 < 8 and ((mat[i + 1][j] == 11 or mat[i + 1][j] == 10) or (mat[i + 1][j] == 31)): #не выходим за матрицу и клетка в которую хотим пройти - элемент второго этажа или рампа на съезд
                    # добавляем клетку с измененной координатой
                    neighbour_dict[(i, j)].append((i + 1, j))

                if i - 1 > -1 and ((mat[i - 1][j] == 11 or mat[i - 1][j] == 10) or mat[i - 1][j] == 30):
                    # делаем все тоже
                    neighbour_dict[(i, j)].append((i - 1, j))

                if j - 1 > -1 and ((mat[i][j - 1] == 10 or mat[i][j - 1] == 11) or mat[i][j - 1] == 33):
                    # и тут
                    neighbour_dict[(i, j)].append((i, j - 1))

                if j + 1 < 8 and ((mat[i][j + 1] == 11 or mat[i][j + 1] == 10) or mat[i][j + 1] == 32):
                    # этот код достаточно однообразный
                    neighbour_dict[(i, j)].append((i, j + 1))


            #todo comment this piece if u gonna move freely on sec floor
            #todo start

            # elif int(str(mat[i][j])) == 10: # если клетка из которой мы ищем возможные проходы - второй этаж
            #
            #     if j - 1 > -1 and ((mat[i][j - 1] == 10) or mat[i][j - 1] == 33):
            #         # и тут
            #         neighbour_dict[(i, j)].append((i, j - 1))
            #
            #     if j + 1 < 8 and ((mat[i][j + 1] == 10) or mat[i][j + 1] == 32):
            #         # этот код достаточно однообразный
            #         neighbour_dict[(i, j)].append((i, j + 1))
            #
            #
            # elif int(str(mat[i][j])) == 11: # если клетка из которой мы ищем возможные проходы - второй этаж
            #
            #     if i + 1 < 8 and ((mat[i + 1][j] == 11) or (mat[i + 1][j] == 31)): #не выходим за матрицу и клетка в которую хотим пройти - элемент второго этажа или рампа на съезд
            #         # добавляем клетку с измененной координатой
            #         neighbour_dict[(i, j)].append((i + 1, j))
            #
            #     if i - 1 > -1 and ((mat[i - 1][j] == 11) or mat[i - 1][j] == 30):
            #         # делаем все тоже
            #         neighbour_dict[(i, j)].append((i - 1, j))


            #todo end


            elif int(str(mat[i][j])[0]) == 3: #если рампа
                # я не придумал ничего лучше рассматривания частных случаев, где можно проехать либо на второй этаж либо на другую рампу
                if mat[i][j] == 30:
                    if i+1 < len(mat) and (mat[i + 1][j] == 10 or mat[i + 1][j] == 11 or mat[i + 1][j] == 31):
                        neighbour_dict[(i, j)].append((i + 1, j))

                    if i - 1 > -1 and (mat[i - 1][j] == 70 or mat[i - 1][j] == 31):
                        neighbour_dict[(i, j)].append((i - 1, j))


                elif mat[i][j] == 31: # я реально рассматриваю все 4 рампы
                    if i + 1 < len(mat) and (mat[i + 1][j] == 70 or mat[i + 1][j] == 30):
                        neighbour_dict[(i, j)].append((i + 1, j))

                    if i - 1 > -1 and (mat[i - 1][j] == 10 or mat[i - 1][j] == 11 or mat[i - 1][j] == 30):
                        neighbour_dict[(i, j)].append((i - 1, j))

                elif mat[i][j] == 32: #это немного неэффективно
                    if j + 1 < len(mat) and (mat[i][j + 1] == 70 or mat[i][j + 1] == 33):
                        neighbour_dict[(i, j)].append((i, j + 1))

                    if j - 1 > -1 and (mat[i][j - 1] == 10 or mat[i][j - 1] == 11 or mat[i][j - 1] == 11 or mat[i][j - 1] == 33):
                        neighbour_dict[(i, j)].append((i, j - 1))

                elif mat[i][j] == 33: #но в принципе пофиг
                    if j - 1 > -1 and (mat[i][j - 1] == 70 or mat[i][j - 1] == 32):
                        neighbour_dict[(i, j)].append((i, j - 1))

                    if j + 1 < len(mat) and (mat[i][j + 1] == 10 or mat[i][j + 1] == 11 or mat[i][j + 1] == 11 or mat[i][j + 1] == 32):
                        neighbour_dict[(i, j)].append((i, j + 1))





    return (neighbour_dict)

def interpolate_color(t):
    if (t < 1 or t == 1) and (t > 0 or t ==0):
        #переводит значение от нуля до единицы в цвет от красного до синего, думаю мне не нужно это объяснять
        light_blue = (75, 120, 230)
        bright_red = (255, 0, 0)
        t = t - 0.05
        red = int(light_blue[0] + (bright_red[0] - light_blue[0]) * t)
        green = 0
        blue = int(light_blue[2] + (bright_red[2] - light_blue[2]) * t)

        return red, green, blue
    else:
        print("Fail during colour interpolation! arg can't be > 1 or < 0 !  \n arg:", t)
        return None

def wave_frame_displaying(cords, w_num, max_w_num, object, toggle_ramk = 1, toggle_mycolor = None, custom_num = 0,line_smth = (3,0.8)):
    #эта штука выводит один квадрат сетки волн + цифру
    add = 20
    if not toggle_mycolor:
        w_to_map = max_w_num - w_num #тк 1 - синий, а 0 - красный нам нужно инвертировать номер волны
        w_mapped = scale_value(w_to_map, 0, max_w_num, 0, 1) #маппинг номера волны от 0 до одного
        add = 20 #добавления отступа для двухзначных чисел
        if len(str(w_num)) == 2:
            add = 5

    if toggle_ramk:
        if not toggle_mycolor:
            cv2.rectangle(object, (cords[1] * 100, cords[0] * 100), (cords[1] * 100 + 100, cords[0] * 100 + 100),
                          interpolate_color(w_mapped), line_smth[0]) #рисуем прямоугольник
        if toggle_mycolor:
            cv2.rectangle(object, (cords[1] * 100, cords[0] * 100), (cords[1] * 100 + 100, cords[0] * 100 + 100),
                          toggle_mycolor, line_smth[0])  # рисуем прямоугольник

    if not toggle_mycolor:
        cv2.putText(object, str(w_num), ((cords[1] - 1) * 100 + 160 + add, cords[0] * 100 + 90), cv2.FONT_HERSHEY_SIMPLEX, line_smth[1],
                    interpolate_color(w_mapped), 2) #рисуем текст (числа после плюса подобраны вручную хд)

    else:
        cv2.putText(object, str(custom_num), ((cords[1] - 1) * 100 + 90 + add, cords[0] * 100 + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(0,250,0),2) #рисуем текст (числа после плюса подобраны вручную хд)

def scale_value(value, from_min, from_max, to_min, to_max):
    normalized_value = (value - from_min) / (from_max - from_min)  # map() из ардуино но в питоне

    scaled_value = to_min + normalized_value * (to_max - to_min)

    return scaled_value

def wave_ini(p_start, connections_dict):
    # построение волны
    waves = [[p_start]]

    while len(waves[-1]) != 0: #пока длина последней построенной волны не равна 0
        waves.append([]) #добавляем к списку с волнами пустой список

        for i in range(len(waves[-2])): # перебираем все точки из предыдущей волны
            all_waves = []

            for k in waves: # создание списка всех точек всех волн, что бы избежать повторения
                for q in k:
                    all_waves.append(q)

            # print(connections_dict[waves[-2][i]])
            for j in range(len(connections_dict[waves[-2][i]])): #для всех точек, в которые можно пройти из выбранной точки предыдущей волны

                if connections_dict[waves[-2][i]][j] not in all_waves: #если точка в которую можно пройти из выбранной точки прошлой волны еще не использована - добавляем ее в текущую волну
                   # ps -2 - индекс прошлой волны, i - индекс конкретного элемента этой волны. Это ключ к элементу словаря,который содержит все клетки в которые можно пройти. j - индекс конкретной клетки в которую можно пройти
                    waves[-1].append(connections_dict[waves[-2][i]][j])
                    # на следующем повторении цикла текущая волна станет прошлой и так пока есть куда идти

    return waves

def wave_visual(wave_list, object):
    for i in range(len(wave_list)): # перебираем все элементы списка с волнами, что бы визуализировать его на картинке
        for j in range(len(wave_list[i])):
            wave_frame_displaying(wave_list[i][j], i, len(wave_list) - 1, object)

def tuples_to_lists(tuples_list):
  return [list(tup) for tup in tuples_list] #thats dummy...

def wave_back_way(waves, p1, p2, dict, lenght_debugging,object,field_mat, max_lenght = None,):
    # global smth_for_ramps
    smth_for_ramps = True
    print("creating path", p1, p2)

    way = [p2]  # построение обратного маршрута
    all_waves = []
    final_app = 0

    for i in waves: #список всех элементов всех волн
        for j in i:
            all_waves.append(j)


    if p1 == p2:
        if lenght_debugging:
            print("Start and finish points can't be same! \n Points:", p1, p2)
        return None

    if p1 != waves[0][0]:
        if lenght_debugging:
            print("Error! start point of wave and start point of path are not same!", "\n", "start point of wave: ", waves[0][0], " start point of path: " , p1)
        return None

    if p2 not in all_waves:
        if lenght_debugging:
            print("cant find path", "pt 1:", p1, "pt 2:", p2)
        return None

    while 1:
        pre_app = ()
        possible_moves = dict[way[-1]] # берем последний элемент построенного пути и смотрим куда из него можно пройти
        min_num = 1000 #очень надеюсь что будет меньше 1000 волн...

        for i in range(len(possible_moves)): #для каждой возможной клетки
            for j in waves:
                if possible_moves[i] in j: # если клетка в которую можно пройти находится в одной из волн то
                    if waves.index(j) < min_num: # если индекс волны меньше минимального
                        min_num = waves.index(j) #перезаписываем минимальный индекс
                        pre_app = possible_moves[i] #перезаписываем клетку в которую хотим ходить



        if str(field_mat[pre_app[0]][pre_app[1]])[0] == "3": #"реальная" длина (с длиной рамп)
            final_app+=2

        # по итогам цикла получаем клетку с наименьшим номером волны, ее и записываем
        way.append(pre_app)

        if max_lenght: #аргумент из штук с рампами что бы не строить маршрут если он уже длиннее минимального
            if len(way)+final_app >= max_lenght:
                return None

        if way[-1] == p1: #если пришли в исходную точку (маршрут построен)
            imposters = [] #рампы

            if final_app != 0 and smth_for_ramps == False: #никакой рекурсии!)

                if lenght_debugging == 2:
                    print("Seems like theres ramps on our way... \n Lets try to reconstruct it!")
                    print("current lenght:", len(way)+final_app)

                smth_for_ramps = True
                way_with_ramps = ramp_security_control(imposters,lenght_debugging,len(way)+final_app,dict,object,p1,p2,field_mat) #вызываем функцию ре-маршрутизации

                if way_with_ramps: #если она что-то вернула
                    if lenght_debugging == 2:
                        print("Path recreated successfully p1:", p1, " ", "p2: ", p2, "\n          ", "lenght: ",
                              way_with_ramps[1])
                    return way_with_ramps

            if lenght_debugging == 2:
                print("Path created successfully p1:", p1, " ", "p2: ", p2, "\n          ", "lenght: ", str(len(way)+final_app))

            if way:
                way = way[::-1] #инвертирование пути тк строим от обратного
                return [way, len(way)+final_app]

            else:
                return None #по идее такого случая не может быть, но мало ли

def ramp_security_control(ramps,debugging,current_len,dict,object,p1,p2,field_mat):
        #этот прикол надо бы оптимизировать
        #если в рампу нельзя проехать, ее стоит не учитывать
        #если рампы стоят рядом друг с другом - аля спуск-подъем тогда берем их за один элемент
        #надо добавить рекурсию промежуточных маршрутов - если есть рампы которых нет в списке перебираемых - запускаем эту же функцию, но с новыми рампами а то есть варианты когда эта штука может не сработать но шанс этого просто мегамаленький
        #еще нужна макс длина маршрута в качестве аргумента, что бы по достижении ее wave_back_way переставал считать дальше
        ramps = []
        max_lenght = 1000
        #print(current_len)

        # while 1:
        #     print("hehe")

        for i in range(8):
            for j in range(8):
                if list(str(field_mat[i][j]))[0] == "3":
                    ramps.append((i,j))

        global smth_for_ramps

        dict_to_change = copy.deepcopy(dict) #очень странная штука, copy.copy не работало а deepcopy работает (i have no clue why)
        all_path_dict = {}
        all_len_list = []


        ramps_combinations = all_combinations(ramps) #все комбинации из рамп маршрута, вообще можно было бы сделать комбинацию из всех рамп на поле, но питон не вывозит
        for i in range(len(ramps_combinations)): #для всех комбинаций рамп
            for j in range(len(ramps_combinations[i])): #для всех рамп в комбинации
                for k in range(8): #для всей
                    for m in range(8): #матрицы
                        for n in range(len(dict_to_change[(k,m)])): #для всех клеток в которые можно пройти из конкретной клетки матрицы
                            if ramps_combinations[i][j] in dict_to_change[(k,m)]: #если в рампу из комбинации можно пройти то
                                dict_to_change[(k,m)].remove(ramps_combinations[i][j]) #теперь в нее нельзя пройти хехе

            wave_list = wave_ini(p1,dict_to_change)

            way = wave_back_way(wave_list,p1,p2,dict_to_change,0,object,field_mat, max_lenght) #ищем путь, но с забанеными рампами
            dict_to_change = copy.deepcopy(dict) #возвращаем словарь с клетками куда можно пройти к нормальному виду

            if way: #если путь существует

                if way[1] < max_lenght:
                    max_lenght = way[1]

                final_app = 0 #считаем "настоящую длину" (с учетом рамп)

                for z in range(len(way)):
                    if list(str(field_mat[way[0][z][0]][way[0][z][1]]))[0] == "3": #эти индексы...
                        #print("appended")
                        final_app += 2

                all_path_dict[way[1]+final_app] = way[0] #добавляем путь в словарь всех путей (пофигу что пути с одинаковой длиной будут перезаписываться)
                all_len_list.append(way[1]+final_app)

        smth_for_ramps = False #перед ретерном возвращаем "предохранитель" от бесконечной рекурсии

        if len(all_len_list) > 0 and min(all_len_list) < current_len: #если новый маршрут короче старого: а то мало ли что там создалось
            if debugging:
                ini(object,field_mat) #рисуем крутой маршрут
                whats_that = wave_ini(p1,dict)
                wave_visual(whats_that,object)
            return all_path_dict[min(all_len_list)], min(all_len_list) #return маршрута (инвертированного) + длины (его же)

        else:
            ini(object, field_mat) #если нет, возвращаем ничего и функция вейв бек все поймет и отрисует начальный маршрут
            whats_that = wave_ini(p1, dict)
            wave_visual(whats_that, object)
            return None

def way_visualisation(object, way, funny_sound, anim, color = (0,255,0), thickness = 10,delta = 0,field_mat = []):
    if way:
        for i in range(len(way)-1):
            cv2.line(object,(way[i][1]*100 + 30 + delta*10, way[i][0]*100 + 30+delta*10 ),(way[i+1][1]*100 + 30+delta*10 , way[i+1][0]*100 + 30+ delta*10),color,thickness)
            cv2.imshow("map", cv2.resize(object, (600, 600)))
            cv2.waitKey(1)

        if anim:
            dir = 0
            for j in range(len(way) - 1):

                if way[j][1] == way[j + 1][1] + 1:
                    dir = 3

                elif way[j][1] == way[j + 1][1] - 1:
                    dir = 2

                elif way[j][0] == way[j + 1][0] + 1:
                    dir = 0

                elif way[j][0] == way[j + 1][0] - 1:
                    dir = 1

                if j > 0:
                    show_smth(field_mat[way[j-1][0]][way[j-1][1]],way[j-1],object)

                show_smth("705"+str(dir),way[j],object)
                cv2.imshow("map", cv2.resize(object, (600, 600)))
                cv2.waitKey(1)


                time.sleep(0.2)

            show_smth(field_mat[way[-2][0]][way[-2][1]], way[-2], object)
            show_smth("705" + str(dir), way[-1], object)
            cv2.imshow("map", cv2.resize(object, (600, 600)))
            cv2.waitKey(1)


    if funny_sound:
        pass

    else:
        return None

def all_combinations(elements):
    combinations = []

    for r in range(1, len(elements) + 1):
        combinations.extend(itertools.combinations(elements, r))

    return combinations

def all_permutations(elements):
  # Генерация всех перестановок
  permutations = list(itertools.permutations(elements))
  return permutations

def get_colors(option):
  if option == 1: #что бы финальный маршрут был нагляднее
    return 0, 0, 255
  elif option == 2:
    return  0, 255, 255
  elif option == 3:
    return 192, 192, 0
  else:
    return 255, 0, 0

def print_colored(text, color='white'):
  # ANSI escape codes for text coloring
  #если честно, я не знаю как это работает
  colors = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m', # Reset to default color
  }
  color_code = colors.get(color, colors['white'])
  print(f"{color_code}{text}{colors['reset']}")

def remove_duplicates(input_list):
  seen = set()
  result = []
  for item in input_list:
    if item not in seen:
      seen.add(item)
      result.append(item)
  return result

def clear():
    # for windows the name is 'nt'
    if name == 'nt':
        _ = system('cls')

    # and for mac and linux, the os.name is 'posix'
    else:
        _ = system('clear')

def final_roadmap(obj,field_mat,ramp_checkment = False, debugging = 0):
    #min_max - if != 0 displaying longest way (for fun and debugging)
    global smth_for_ramps
    smth_for_ramps = not ramp_checkment
    skip_all_cv = not False


    print_colored("          Let the procedure begin...","magenta")


    cells_to_tubes_dict = {} #dict like [tube cord] = list of cells from which we can pick up it
    unload_cells_dict = {}
    real_all_paths_no_joke = {} #all possible tubes picking ways, storing like [path lenght] = [ways of path list]

    tubes = [] #tubes cords list
    cell_to_tube = [] # cells we can pick up tubes from
    way_lenghts = [] #war to store all ways lenght (keys to real_all_paths_no_joke)
    waves_all = [] #all waves to prevent adding unreachable cells to cells_to_tubes_dict
    unload_cords = []
    unload_cells= []
    my_pos = []

    # print("slpng")
    # print_matrix(field_mat)
    # time.sleep(2)

    #---------------pos detecting ------------------#
    for i in range(len(field_mat)):
        for j in range(len(field_mat)):

            if str(field_mat[i][j])[-2] == "5":

                if str(field_mat[i][j])[0] == "7":
                    my_pos = (i,j)
                    field_mat[i][j] = 70

                else:
                    if debugging:
                        print_colored("Dont ready for robot on second floor!1", "red")
                    print_colored("\n\n         FAILED", "red")
                    return None

    #-------------------waves building--------------------#

    dictionary = neighbour_ini(field_mat)
    p1_tmp = copy.deepcopy(my_pos) #variable for my pos storing (can be replaced with way[0][-1] but i don't care
    waves = wave_ini(my_pos,dictionary) #creating waves

    for k in waves:  # создание списка всех точек всех волн, что бы избежать повторения
        for q in k:
            waves_all.append(q)


    #--------------tubes pick up points finding------------------#

    for i in range(len(field_mat)): #поиск клеток из которых можно забрать трубы (записывается в словарь вида труба - список клеток)
        for j in range(len(field_mat)):
            #PS str(field_mat[i][j])[0] == str(field_mat[i][j-1])[0] - проверка на этажность. Если есть идеи как сделать проще то было бы славно

            if list(str(field_mat[i][j]))[-2] == "4":

                cells_to_tubes_dict[(i,j)] = []
                tubes.append((i,j))

                if list(str(field_mat[i][j]))[-1] == "1": #смотрим куда повернута труба

                    # if i+1 < 8:
                    #     print(str(field_mat[i+1][j])[0])
                    #     if str(field_mat[i+1][j])[0] == "3":
                    #         print(i,j)


                    if j+1 < len(field_mat) and str(field_mat[i][j])[0] == str(field_mat[i][j+1])[0] and (i,j+1) in waves_all :
                        cell_to_tube.append((i,j+1))

                    if j - 1 > -1 and str(field_mat[i][j])[0] == str(field_mat[i][j-1])[0] and (i,j-1) in waves_all: #если на том же этаже и есть в волнах, то считаем что с этой клетки можно забрать
                        cell_to_tube.append((i, j-1))


                    #---------------picking up from ramps-----------------#
                    if j - 1 > -1 and str(field_mat[i][j-1]) == "33" and (i,j-1) in waves_all:
                        cell_to_tube.append((i, j-1))

                    if j + 1 < len(field_mat) and str(field_mat[i][j+1]) == "32" and (i,j+1) in waves_all:
                        cell_to_tube.append((i, j+1))



                elif list(str(field_mat[i][j]))[-1] == "0":

                    if i-1 > -1 and str(field_mat[i][j])[0] == str(field_mat[i-1][j])[0] and (i-1,j) in waves_all:

                        cell_to_tube.append((i-1, j))

                    if i + 1 < len(field_mat) and str(field_mat[i][j])[0] == str(field_mat[i+1][j])[0] and (i+1,j) in waves_all:
                        cell_to_tube.append((i+1, j))

                    # ---------------picking up from ramps-----------------#
                    if i + 1 < len(field_mat) and str(field_mat[i+1][j]) == "30" and (i+1,j) in waves_all:
                        cell_to_tube.append((i+1, j))

                    if i - 1 > -1 and str(field_mat[i-1][j]) == "31" and (i-1,j) in waves_all:
                        cell_to_tube.append((i-1, j))



            if cell_to_tube:

                cells_to_tubes_dict[(i,j)].append(cell_to_tube)
                cell_to_tube = []

    # print(cells_to_tubes_dict)

    # --------------tubes unload up points finding------------------#

    for z in range(len(field_mat)):
        for ov in range(len(field_mat)): #клетки из которых можно разгрузить трубы
            if str(field_mat[z][ov])[0] == "6": #если нашли точку разгрузки

                unload_cords.append((z,ov))
                unload_cells_dict[unload_cords[-1]] = []

                if str(field_mat[z][ov])[-1] == "0" or str(field_mat[z][ov])[-1] == "1":

                    if z+1 < len(field_mat) and str(field_mat[z+1][ov]) == "70": #разгружать можно только с первого этажа
                        unload_cells_dict[unload_cords[-1]].append((z+1,ov))
                        unload_cells.append((z+1,ov))

                    if z-1 > -1 and str(field_mat[z-1][ov]) == "70":
                        unload_cells_dict[unload_cords[-1]].append((z-1,ov))
                        unload_cells.append((z-1,ov))

                if str(field_mat[z][ov])[-1] == "2" or str(field_mat[z][ov])[-1] == "3":

                    if ov+1 < len(field_mat) and field_mat[z][ov+1] == 70:
                        unload_cells_dict[unload_cords[-1]].append((z,ov+1))
                        unload_cells.append((z,ov+1))

                    if ov-1 > -1 and field_mat[z][ov-1] == 70:
                        unload_cells_dict[unload_cords[-1]].append((z,ov-1))
                        unload_cells.append((z,ov-1))

    print(unload_cells_dict)

    if not unload_cords:

        if debugging:
            print("Cant build path, no unload points!1!")
        print_colored("\n\n         FAILED", "red")
        return None

    for i in range(len(tubes)): #Проверка того, что в каждую трубу можно доехать, иначе маршрут нельзя построить
        if cells_to_tubes_dict[tubes[i]] == []:
            if debugging:
                wave_frame_displaying(tubes[i],0,0,obj,1,(0,0,255),"ERR",(6,0.8))
                print("Cant create path! Unreachable tube found:", tubes[i])
            print_colored("\n\n\n\n         FAILED", "red")
            return None


    tubes = all_permutations(tubes) #все варианты сбора труб
    tubes = tuples_to_lists(tubes) #all_permutations возвращает картежи, а не списки, что несомненно грустно

    cells_to_tubes_dict[unload_cords[0]] = [unload_cells] #добавление поинтов разгрузки труб


    for m in range(len(tubes)): #добавляем точку выгрузки к каждому маршруту
        tubes[m].append(unload_cords[0])

    #print(cells_to_tubes_dict)

    for i in range(len(tubes)): #для всех вариантов сбора

        path_to_all = []
        way_lenght = 0
        p1_tmp = deepcopy(my_pos)

        for j in range(len(tubes[i])): #для всех труб в вариантах сбора

            ways_to_tube_dict = {}
            ways_to_tube = []

            for q in range(len(cells_to_tubes_dict[tubes[i][j]][0])): #для всех клеток с которых можно забрать конкретную трубу

                #16.11.24 в 20:25 я пофиксил тупейший баг, но об этом никто не узнает

                waves = wave_ini(p1_tmp,dictionary) #строим волну со старта
                if debugging:
                    wave_visual(waves,obj)

                way = wave_back_way(waves,p1_tmp,cells_to_tubes_dict[(tubes[i][j])][0][q],dictionary,debugging,obj,field_mat) #маршрут к одной из клеток из которой можно забрать трубу

                if way: #если путь есть, то записываем его в словарь с путями
                    if debugging == 1 or debugging == 0:
                        progress_bar(round(( (1/len(tubes))*i + ((1/len(tubes))/len(tubes[i])*(j+1) ) )*100)) #nvm
                    #print(round(( (1/len(tubes))*(i+1) + ((1/len(tubes))/len(tubes[i])*j ) )*100))

                    ways_to_tube_dict[way[1]] = way[0] #way[0] - way cords list, way[1] - way lenght with ramps
                    ways_to_tube.append(way[1])
                else:
                    if debugging:
                        print("Failed while creating one of final ways. \n Seems like field was scanned incorrectly", "\n p1:", p1_tmp, "p2:", cells_to_tubes_dict[(tubes[i][j])][0][q])

            if not ways_to_tube: #если к одной из труб совсем никак нельзя проехать
                if debugging:
                    wave_frame_displaying(tubes[i][j], 0, 0, obj, 1, (0, 0, 255), "ERR", (6, 0.8))
                    print("One of tubes is completely unreachable!")
                    print(ways_to_tube_dict)
                print_colored("\n\n         FAILED", "red")
                return None

            path_to_all.append(ways_to_tube_dict[min(ways_to_tube)]) #список путей для одного из возможных маршрутов

            way_lenght += min(ways_to_tube)
            p1_tmp = ways_to_tube_dict[min(ways_to_tube)][-1]

        real_all_paths_no_joke[way_lenght] = path_to_all #как только закончился цикл - записываем получившийся маршрут
        way_lenghts.append(way_lenght) #и его длину (я не умею работать с ключами словаря(()

        if debugging:
            ini(obj,field_mat)
        waves = wave_ini(p1_tmp, dictionary)

        if debugging:
            wave_visual(waves, obj)

        if debugging:
            for help_me in range(len(real_all_paths_no_joke[min(way_lenghts)])): #рисуем один из возможных маршрутов
                way_visualisation(obj, path_to_all[help_me], 0, 0, get_colors(help_me + 1))
                cv2.imshow("map", cv2.resize(obj, (600, 600)))
                cv2.waitKey(1)
            #time.sleep(0.1)

    if skip_all_cv:
        #как только все маршруты построены
        ini(obj,field_mat)
        waves = wave_ini(p1_tmp, dictionary)
        wave_visual(waves, obj)

        if not min_max:
            for g in range(len(real_all_paths_no_joke[min(way_lenghts)])):

                funny_sound_heh = 0

                # print(my_pos)


                if g == len(real_all_paths_no_joke[min(way_lenghts)])-1:
                    funny_sound_heh = funny_sound

                way_visualisation(obj, real_all_paths_no_joke[min(way_lenghts)][g], funny_sound_heh, anim, get_colors(g),10,g,field_mat)
                wave_frame_displaying(real_all_paths_no_joke[min(way_lenghts)][g][-1],0,0,obj,0,1,g+1) #рисуем номер в клетке с которой забираем трубу
                cv2.imshow("map", cv2.resize(obj, (600, 600)))
                # show_smth(7050,my_pos,obj)
                cv2.waitKey(1)
                time.sleep(0.5)

        else: #рисование самого длинного маршрута (пару раз пригодилось)
            print_colored("\n\nShowing longest way BUT returning shortest, dont panic XD","magenta")
            for g in range(len(real_all_paths_no_joke[max(way_lenghts)])):
                funny_sound_heh = 0

                if g == len(real_all_paths_no_joke[max(way_lenghts)]):
                    funny_sound_heh = funny_sound

                way_visualisation(obj, real_all_paths_no_joke[max(way_lenghts)][g], funny_sound_heh, anim, get_colors(g),10,g)
                wave_frame_displaying(real_all_paths_no_joke[max(way_lenghts)][g][-1], 0, 0, obj, 0, 1, g + 1) #рисуем номер в клетке с которой забираем трубу
                cv2.imshow("map", cv2.resize(obj, (600, 600)))
                cv2.waitKey(1)
                time.sleep(0.8)

        way_lenghts = remove_duplicates(way_lenghts) #для красивого вывода

        if debugging:
            print_colored("\n\n\npossible paths lenghts:" + "  " + str([i for i in way_lenghts]), "blue")
            print_colored("our choice:" + "  " + str(min(way_lenghts)), "blue")


        print_colored("\n\n\n\n\n\n\n\n      WAY DONE", "green")

    return real_all_paths_no_joke[min(way_lenghts)]

def progress_bar(value):
  """Displays a simple text-based progress bar."""
  clear()
  if 0 <= value <= 100:


    bar_length = 20
    filled_length = int(bar_length * value / 100)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    print(f"Progress: [{bar}] {value:.0f}%")
  else:
    pass

def way_to_commands(path,field_mat):
    # someone fix this shit plz
    #fixed
    print_colored("\n\n     way: \n", "green")
    print_colored(path, "green")
    # print(path)
    final_str = ""
    dir_list = []
    dir = 0

    for i in range(len(path)):

        for j in range(len(path[i]) - 1):

            if int(str(field_mat[path[i][j][0]][path[i][j][1]])[0]) == 3: #дядяяяяяяяяяяяяяяяя

                if int(str(field_mat[path[i][j + 1][0]][path[i][j + 1][1]])[0]) == 7:
                    dir_list.append("sd") #means ramp down

                else:
                    dir_list.append("su")  # means ramp up

                continue

            if path[i][j][1] == path[i][j + 1][1] + 1:
                dir = "L"
            elif path[i][j][1] == path[i][j + 1][1] - 1:
                dir = "R"
            elif path[i][j][0] == path[i][j + 1][0] + 1:
                dir = "U"
            elif path[i][j][0] == path[i][j + 1][0] - 1:
                dir = "D"
            dir_list.append(dir)

        # print(str(field_mat[path[i][-1][0]][path[i][-1][1]]))
        if path[i][-1][1] + 1 < 8 and len(
                str(field_mat[path[i][-1][0]][path[i][-1][1] + 1])) == 4:  # проверка на трубу (глупенькая)

            if str(field_mat[path[i][-1][0]][path[i][-1][1]])[0] == "3":
                dir_list.append("TR")
            else:
                dir_list.append("tR")


        if path[i][-1][1] - 1 > -1 and len(str(field_mat[path[i][-1][0]][path[i][-1][1] - 1])) == 4:
            if str(field_mat[path[i][-1][0]][path[i][-1][1]])[0] == "3":
                dir_list.append("TL")
            else:
                dir_list.append("tL")

        if path[i][-1][0] + 1 < 8 and len(str(field_mat[path[i][-1][0] + 1][path[i][-1][1]])) == 4:
            if str(field_mat[path[i][-1][0]][path[i][-1][1]])[0] == "3":
                dir_list.append("TD")
            else:
                dir_list.append("tD")

        if path[i][-1][0] - 1 > -1 and len(str(
                field_mat[path[i][-1][0] - 1][path[i][-1][1]])) == 4:  # Fixed this line:  -1 > -1 should be > -1

            if str(field_mat[path[i][-1][0]][path[i][-1][1]])[0] == "3":
                dir_list.append("TU")
            else:
                dir_list.append("tU")

    dir_str = ""
    for i in dir_list:
        dir_str += str(i)

    result = []
    m = 0
    while m < len(dir_str):
        if dir_str[m] == 't' or dir_str[m] == 's' or dir_str[m] == 'T':
            if m + 1 < len(dir_str):
                result.append(dir_str[m:m + 2])
                m += 2  # Skip the next number as well
        else:
            digit, group = next(groupby(dir_str[m:]))
            count = len(list(group))
            result.append(f"{digit}{count}")
            m += count

    dir_str =  "*".join(result)
    dir_list =  split_string_into_pairs(dir_str)

    print_colored("\n\n     absolute command path:", "blue")
    print_colored(dir_list, "blue")

    res_real = []
    to_add = 0
    my_dir = "U"

    for i in range(len(dir_list)):
        if i == 0:
            if my_dir != str(dir_list[i])[0]:
                if get_rotation_direction(my_dir, str(dir_list[i])[0]) != "skip":
                    res_real.append(get_rotation_direction(my_dir,str(dir_list[i])[0]))
            # print("dir:", get_rotation_direction(my_dir,str(dir_list[i])[0]), str(dir_list[i])[0])

            # print("1:", str(dir_list[i])[-1])
            res_real.append("X"+str(int(str(dir_list[i])[-1])+to_add))
            to_add = 0
            # print("num:", str(dir_list[i])[-1])
            my_dir = str(dir_list[i])[0]

        if i != 0:

            if str(dir_list[i])[0] != "t" and str(dir_list[i])[0] != "T" and str(dir_list[i])[0] != "s":
                if my_dir != str(dir_list[i])[0]:

                    if get_rotation_direction(my_dir, str(dir_list[i])[0]) != "skip":

                        # print(get_rotation_direction(my_dir, str(dir_list[i])[0]))
                        res_real.append(get_rotation_direction(my_dir, str(dir_list[i])[0]))

                # print("2:", get_rotation_direction(my_dir, str(dir_list[i])[0]))
                res_real.append("X"+str(int(str(dir_list[i])[-1])+to_add))
                to_add = 0
                my_dir = str(dir_list[i])[0]

            else:
                if str(dir_list[i])[0] == "t":
                    if my_dir != str(dir_list[i])[0]:

                        # print(get_rotation_direction(my_dir, str(dir_list[i])[0]))
                        if get_rotation_direction(my_dir, str(dir_list[i])[-1]) != "skip":
                            res_real.append(get_rotation_direction(my_dir, str(dir_list[i])[-1]))

                    my_dir = str(dir_list[i])[-1]
                    res_real.append("G0")

                if str(dir_list[i]) == "su":
                    if res_real[-1] == "X1":
                        res_real = res_real[:-1]

                    else:
                        num = int(res_real[-1][-1])
                        res_real = res_real[:-1]
                        res_real.append("X"+str(num-1))

                        # to_add = 1

                    res_real.append("F1") #up
                    res_real.append("X1")

                if str(dir_list[i]) == "sd":

                    if res_real[-1] == "X1":
                        res_real = res_real[:-1]
                    else:
                        num = int(res_real[-1][-1])
                        res_real = res_real[:-1]
                        res_real.append("X"+str(num-1))


                    # to_add = 1

                    res_real.append("F0") #down
                    res_real.append("X1")



    num = int(res_real[-1][-1])
    res_real = res_real[:-1]
    res_real.append("X" + str(num - 1))

    print_colored("\n\n\n\n\n    relative command path::", "cyan")
    print_colored(res_real, "cyan")

    print_colored("\n\n     DONE", "green")

    return res_real, dir_list

def create_path(mat,params=[2,0]):
    unload_dict = {"l":["P1","R1","X1","L1","P1","R1","X1","L1","P1"],"r":["P1","L1","X1","R1","P1","L1","X1","R1","P1"], "c":["L1","X1","R1","P1","R1","X1","L1","P1","R1","X1","L1","P1"]}
    mat_to_change = copy.deepcopy(mat)
    command_str = []
    mat_to_change = replace_ints_in_matrix(mat)

    # print(mat_to_change)
    # time.sleep(2)

    start_time = time.time()

    obj = cv2.imread("white_picture.jpg")  # картинка для фона
    smth_for_ramps = True  # анти рекурсия при рамп чекменте

    if params[-1] == 1:
        full_way = final_roadmap(obj, mat_to_change, params[1], params[0])
        commands = way_to_commands(full_way,mat_to_change)
        type_u = detect_unload_type(full_way[-1][-1],mat_to_change, params[0], commands[1])
        print(type_u)
        if type_u[1] != "skip":
            commands[0].append(str(type_u[1] + "1"))
        return commands + unload_dict[type_u[0]]


    ini(obj, mat_to_change)
    # cv2.imshow("map", cv2.resize(obj, (600, 600)))
    # cv2.waitKey(1)


    if params[-2] == 0:
        full_way = final_roadmap(obj,mat_to_change,params[1], params[0])
        if full_way:
            command_str = way_to_commands(full_way,mat_to_change)
            type_u = detect_unload_type(full_way[-1][-1], mat_to_change, params[0],command_str[1])

            print(type_u)


            if type_u[1] != "skip":
                command_str[0].append(str(type_u[1])+"1")
            return  command_str[0] + unload_dict[type_u[0]]

        else:
            return None
        # print(neighbour_ini(mat))

    elif params[-1] == 1:
        ini(obj,mat)
        cv2.imshow("map", cv2.resize(obj, (600, 600)))
        cv2.waitKey(1)
        # icon_change()
        return None

    elif params[-1] == 2:
        my_pos = []

        for i in range(len(mat)):

            for j in range(len(mat)):

                if str(mat[i][j])[-2] == "5":
                    print("idktbh")


                    if str(mat[i][j])[0] == "7":
                        my_pos = (i, j)
                        mat_to_change[i][j] = 70

        ini(obj,mat)
        waves = wave_ini(my_pos,neighbour_ini(mat_to_change))
        wave_visual(waves,obj)
        cv2.imshow("map", cv2.resize(obj, (600, 600)))
        cv2.waitKey(1)
        # icon_change()
        return None



    cv2.imshow("map", cv2.resize(obj, (600, 600)))

    # ---------------------trash---------------------#

    # icon_change()
    end_time = time.time()
    execution_time = end_time - start_time
    print_colored(f"\nTaken time to find path\n    {execution_time:.6f} sec", "cyan")
    cv2.waitKey(1)

    return command_str

def ini_for_nerds(mat):
    obj = cv2.imread("white_picture.jpg")  # картинка для фона
    ini(obj, mat)
    cv2.imshow("map", cv2.resize(obj, (600, 600)))
    cv2.waitKey(0)

def tg_ini(mat):
    obj = cv2.imread("white_picture.jpg")  # картинка для фона
    if mat:
        for i in range(len(mat)):  # перебираем каждый элемент матрицы и выводим его
            for j in range(len(mat[i])):
                show_smth(mat[i][j], (i, j), obj)
    else:
        print("Field mat can't be non type object! \n   Programmer u are dummy ass")
    return obj

def split_string_into_pairs(input_string):
  """
  Splits a string into a list of two-character substrings.

  Args:
    input_string: The string to split.

  Returns:
    A list of two-character substrings, or an empty list if the input
    string is empty or has an odd number of characters.
  """
  if not input_string:
    return []

  pattern = r"[a-zA-Z0-9]{2}"  # Matches two alphanumeric characters

  matches = re.findall(pattern, input_string)

  return matches

def get_rotation_direction(current_direction, target_direction):

    directions = ["U", "R", "D", "L"]
    current_direction = current_direction.upper() # normalize the input
    target_direction = target_direction.upper()  # normalize the input

    if current_direction not in directions or target_direction not in directions:
        # print("fail")
        return None  # Invalid direction input



    current_index = directions.index(current_direction)
    target_index = directions.index(target_direction)

    # Calculate the difference in indices
    diff = (target_index - current_index) % 4  # Use modulo to handle wrap-around

    if diff == 0:
        return "skip"
    elif diff == 1:
        return "R1"  # Rotate right
    elif diff == 2:
        return "R2"  # Rotate back 180 degrees
    elif diff == 3:
        return "L1"  # Rotate left
    else:
        # print("fail")
        return None  # Should not happen, but handle it anyway

def detect_unload_type(pos,mat,debugging = 0, dir_list = None):
    print(pos)

    robot_dir = str(dir_list[-1])[0]
    dir = ""
    tube_dir = ""
    # mat = replace_ints_in_matrix(mat)

    if pos[0] != 7 and mat[pos[0]+1][pos[1]]//10 == 6:
        if debugging:
            print("down")
            tube_dir = "D"

        if pos[0] != 7 and mat[pos[0] + 1][pos[1] - 1] // 10 != 6:
            dir = "r"

        elif pos[0] != 7 and pos[1] != 7 and mat[pos[0] + 1][pos[1] + 1] // 10 != 6:
            dir = "l"

        else:
            dir = "c"

    if pos[1] != 7 and mat[pos[0]][pos[1]+1]//10 == 6:
        if debugging:
            print("right")
            tube_dir = "R"

        if pos[0] != 7 and pos[1] != 7 and mat[pos[0]+1][pos[1]+1]//10 != 6:
            dir = "r"

        elif pos[1] != 7 and mat[pos[0]-1][pos[1]+1]//10 != 6:
            dir = "l"

        else:
            dir = "c"


    if mat[pos[0]-1][pos[1]]//10 == 6:
        if debugging:
            tube_dir = "U"

        if pos[0] != 7 and pos[1] != 7 and mat[pos[0] + 1][pos[1] + 1] // 10 != 6:
            dir = "r"

        elif pos[0] != 7 and mat[pos[0] + 1][pos[1] - 1] // 10 != 6:
            dir = "l"

        else:
            dir = "c"



    if mat[pos[0]][pos[1]-1]//10 == 6:
        if debugging:
            tube_dir = "L"

        if mat[pos[0]-1][pos[1]-1]//10 != 6:
            dir = "r"

        elif pos[0]!= 7 and mat[pos[0]+1][pos[1]-1]//10 != 6:
            dir = "l"

        else:
            dir = "c"

    # print(dir)
    return dir,get_rotation_direction(robot_dir,tube_dir)

def way_to_commands_single(path,mat,my_dir):
    print("path:", path)
    dir_list = []
    for i in range(len(path)-1):

        if str(mat[path[i][0]][path[i][1]])[0] == "3":
            if mat[path[i + 1][0]][path[i + 1][1]] == 10:
                dir_list.append("sd")  # means ramp down

            else:
                dir_list.append("su")  # means ramp up

            continue


        if path[i][1] == path[i + 1][1] + 1:
            dir = "L"
        elif path[i][1] == path[i + 1][1] - 1:
            dir = "R"
        elif path[i][0] == path[i + 1][0] + 1:
            dir = "U"
        elif path[i][0] == path[i + 1][0] - 1:
            dir = "D"
        dir_list.append(dir)

    res = []
    print("dir list:",dir_list)
    print("facing:", my_dir)
    for i in dir_list:
        #обработка рамп
        if i == "su" or i == "sd":
            res.append("X1")
            res.append(["F1" if i == "su" else "F0"])
            res.append("X1")

        if i == my_dir:
            res.append("X1")

        else:
            print(my_dir,i)
            res.append(get_rotation_direction(my_dir,i))
            res.append("X1")
            my_dir = i

    return res


#bugs: 2 tubes with same pickup point (breaks everything)
#fix: check if next pickup point = previous => add empty point list => break current cycle => profit
#we need to create unload path thing. because our def returns only path to closest unload thing. So we still have some things to do

# print(get_rotation_direction("L","R"))

#24.02.25 1:45 everything almost done. All I have left is an unload type detection. But it is really easy. Transforming way to commands was harder than I expected tbh