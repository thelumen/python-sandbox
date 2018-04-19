#!coding:utf-8


import matplotlib.pyplot as plt
import numpy as np
import os.path

# plt.plot(data_all[6::8])#1 5,7
# plt.plot(data_all[7::8])#2 10,7
# plt.plot(data_all[0::8])#3 9,18
# plt.plot(data_all[1::8])#4 4,18
# plt.plot(data_all[3::8])#5 3,28
# plt.plot(data_all[4::8])#6 7,29
# plt.plot(data_all[5::8])#7 11,31
# plt.plot(data_all[2::8])#8 10,39

# plt.plot(data_all[1::8])#1 5,7
# plt.plot(data_all[0::8])#2 10,7
# plt.plot(data_all[6::8])#3 9,18
# plt.plot(data_all[7::8])#4 4,18
# plt.plot(data_all[5::8])#5 3,28
# plt.plot(data_all[2::8])#6 7,29
# plt.plot(data_all[3::8])#7 11,31
# plt.plot(data_all[4::8])#8 10,39

index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]
index_r_r_d = [2, 3, 7, 4, 5, 6, 0, 1]
index_l_d_r = [1, 0, 6, 7, 5, 2, 3, 4]
index_l_r_d = [1, 0, 5, 6, 7, 4, 2, 3]
index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']

all_x_r = [9, 4, 10, 3, 7, 11, 5, 10]
all_y_r = [18, 18, 39, 28, 29, 31, 7, 7]
all_x_l = [10, 5, 7, 11, 10, 3, 9, 4]
all_y_l = [7, 7, 29, 31, 39, 28, 18, 18]

home_path = '/home/ri/Data/T4/'
prs_path = home_path + 'prs/'
img_path = home_path + 'img'
prs_filefullnames = []
prs_filenames = []
for parent, dirnames, filenames in os.walk(prs_path):
    for filename in filenames:
        prs_filefullnames.append(prs_path + filename)
        prs_filenames.append(filename[:-4])


def slope(data, point):
    """斜率"""
    l_amount = data[point] - data[point - 1]
    r_amount = data[point + 1] - data[point]
    if l_amount < 0 and r_amount < 0:
        return False
    return True


def maximum(data):
    """极大值"""
    d0 = np.array(data[:-1])
    d1 = np.array(data[1:])
    d2 = d1 - d0
    maximums = []
    for i in range(len(d2) - 1):
        count = i
        i += 1
        if d2[i] <= 0 and d2[count] > 0:
            maximums.append(i)
    return maximums


def triangle(data, t_num=2, dividing_line=40, ttype='max'):
    """
    三角形拟合
    t_num:三角形个数
    dividing_line:分割线横坐标
    ttype:拟合类型
        max:最大值模式,返回两个交点与其之间的最大值构成的三角形一个
        maximum：极值模式,返回两个交点与其之间的极值构成的三角形（默认两个，可设置为一个或更多）
    """
    mark_num = []
    count = 1
    # 查找割线交点
    for d in range(len(data) - 1):
        if count % 2 == 1:
            if data[d] <= dividing_line <= data[d + 1]:
                mark_num.append(d + 1)
                count += 1
        else:
            if data[d] >= dividing_line >= data[d + 1]:
                mark_num.append(d)
                count += 1
    mark_size = len(mark_num)
    # 判断切点数量
    if mark_size < 2:
        return False
    if mark_size % 2 == 1:
        mark_num = mark_num[:-1]
        length_p = np.array(mark_num).reshape(len(mark_num) // 2, 2)
    else:
        length_p = np.array(mark_num).reshape(mark_size // 2, 2)
    maxs_t = []
    triangles = []
    # 判断拟合类型
    if ttype == 'maximum':
        maxs_t = sorted(maximum(data))
    elif ttype == 'max':
        for lp in length_p:
            data_t = data[lp[0] + 1:lp[1]]
            # 剔除无效点
            if len(data_t) < 2:
                continue
            height_p = np.where(data_t == data_t.max())[0][0] + lp[0] + 1
            triangles.append([lp, height_p, data[height_p], dividing_line])
        return triangles
    maxs = []
    # 过滤极值点
    for max in range(len(maxs_t)):
        if data[maxs_t[max]] > dividing_line:
            maxs.append(maxs_t[max])
    triangles = []
    # 判断极值点在交点范围内
    for m in range(len(maxs)):
        for lp in length_p:
            if lp[0] < maxs[m] < lp[1]:
                triangles.append([lp, maxs[m], data[maxs[m]], dividing_line])
    return triangles[:t_num]


def imageprocessing(imagpath, begin, end, type):
    data_all = np.array(np.fromfile(imagpath, 'u1'), dtype='f4')
    imageprocess = []
    for i in range(8):
        di = data_all[type[i]::8][begin:end]
        plt.plot(di, color=index_c[i])
        d_l = 40
        t = triangle(di, dividing_line=d_l)
        while not t and d_l < 180:
            d_l += 10
            t = triangle(di, dividing_line=d_l)
        print(t)
        imageprocess.append(t)
    plt.title(imagpath)
    plt.show()
    return imageprocess


def imageprocess(imagpath_0, begin_0, end_0, type_0, imagpath_1, begin_1, end_1, type_1):
    data_all_0 = np.array(np.fromfile(imagpath_0, 'u1'), dtype='f4')
    data_all_1 = np.array(np.fromfile(imagpath_1, 'u1'), dtype='f4')
    imageprocess_0 = []
    imageprocess_1 = []
    for i in range(8):
        d_l = 40
        di_0 = data_all_0[type_0[i]::8][begin_0:end_0]
        di_1 = data_all_1[type_1[i]::8][begin_1:end_1]
        # plt.plot(di_0, color=index_c[i])
        # plt.plot(di_1, color=index_c[i])
        t_0 = triangle(di_0, dividing_line=d_l)
        t_1 = triangle(di_1, dividing_line=d_l)
        while (not t_0 or not t_1) and d_l < 180:
            d_l += 10
            t_0 = triangle(di_0, dividing_line=d_l)
            t_1 = triangle(di_1, dividing_line=d_l)
        if t_0 and t_1:
            t_0[0].append(end_0 - begin_0)
            t_1[0].append(end_1 - begin_1)
        print('0: ', t_0)
        print('1: ', t_1)
        imageprocess_0.append(t_0)
        imageprocess_1.append(t_1)
    # plt.title(imagpath_0)
    # plt.title(imagpath_1)
    # plt.show()
    return imageprocess_0, imageprocess_1


def conclusion(data_0, data_1):
    max_pressure_change_0 = (data_1[0][0][2] - data_0[0][0][2] + data_1[1][0][2] - data_0[1][0][2]) / 2
    max_pressure_rate_0 = max_pressure_change_0 / abs(data_1[1][0][2] - data_0[1][0][2])
    width_r_0 = (data_0[0][0][0][1] - data_0[0][0][1] + data_0[1][0][0][1] - data_0[1][0][1]) / data_0[0][0][4]
    width_r_change_0 = ((data_1[0][0][0][1] - data_1[0][0][1] + data_1[1][0][0][1] - data_1[1][0][1]) / data_1[0][0][
        4] - width_r_0) * 25
    width_r_rate_0 = width_r_change_0 / abs(width_r_0) / 25
    width_l_0 = (data_0[0][0][1] - data_0[0][0][0][0] + data_0[1][0][1] - data_0[1][0][0][0]) / data_0[0][0][4]
    width_l_change_0 = ((data_1[0][0][1] - data_1[0][0][0][0] + data_1[1][0][1] - data_1[1][0][0][0]) / data_1[0][0][
        4] - width_l_0) * 25
    width_l_rate_0 = width_l_change_0 / abs(width_l_0) / 25
    print('足跟')
    print('最大压力差值  :%.2f' % max_pressure_change_0)
    print('最大压力变化率 :%.2f' % max_pressure_rate_0)
    print('右侧跨度      :%.2f' % width_r_change_0)
    print('跨度变化率    :%.2f' % width_r_rate_0)
    print('左侧跨度      :%.2f' % width_l_change_0)
    print('跨度变化率    :%.2f' % width_l_rate_0)
    print('-------------')
    max_pressure_change_2 = (data_1[2][0][2] - data_0[2][0][2]) / 2
    max_pressure_rate_2 = max_pressure_change_2 / data_0[2][0][2]
    width_r_2 = (data_0[2][0][0][1] - data_0[2][0][1]) / data_0[2][0][4]
    width_r_change_2 = ((data_1[2][0][0][1] - data_1[2][0][1]) / data_1[2][0][4] - width_r_2) * 25
    width_r_rate_2 = width_r_change_2 / abs(width_r_2) / 25
    width_l_2 = (data_0[2][0][1] - data_0[2][0][0][0]) / data_0[2][0][4]
    width_l_change_2 = ((data_1[2][0][1] - data_1[2][0][0][0]) / data_1[2][0][4] - width_l_2) * 25
    width_l_rate_2 = width_l_change_2 / abs(width_l_2) / 25
    print('max_pressure_change_2:%.2f' % max_pressure_change_2)
    print('max_pressure_rate_2  :%.2f' % max_pressure_rate_2)
    print('width_r_change_2     :%.2f' % width_r_change_2)
    print('width_r_rate_2       :%.2f' % width_r_rate_2)
    print('width_l_change_2     :%.2f' % width_l_change_2)
    print('width_l_rate_2       :%.2f' % width_l_rate_2)
    print('-------------')


# a = imageprocessing(prs_path + '1522129506_left.prs', 350, 400, index_l_d_r)
# b = imageprocessing(prs_path + '1522131815_left.prs', 700, 760, index_l_d_r)
# imageprocessing('/home/ri/out.prs', 350, 400, index_r_d_r)
a, b = imageprocess(prs_path + '1522129506_left.prs', 350, 400, index_l_d_r,
                    prs_path + '1522131815_left.prs', 700, 760, index_l_d_r)
conclusion(a, b)
