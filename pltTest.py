#!coding:utf-8
import math

import matplotlib.pyplot as plt
import numpy as np

from scipy import signal
from getpredata import get_pre_data, data2plt, compared
from pearson import pearson, euc_dist


def cogr(p, p_x, p_y):
    p_sum = sum(p)
    x = np.array(p_x)
    y = np.array(p_y)
    return [sum(x * p) / p_sum, sum(y * p) / p_sum]


def cog(p):
    p_x, p_y, p_sum = 0, 0, 0
    for i in range(len(p)):
        for j in range(len(p[i])):
            if p[i][j] > 0:
                p_x += p[i][j] * j
                p_y += p[i][j] * i
                p_sum += p[i][j]
    return [p_x / p_sum, p_y / p_sum]


def solution(equation, y):
    equation[0] = equation[0] - y
    return equation.r


def fitting(data_t, t):
    x = range(len(data_t))
    y = data_t
    z = np.polyfit(x, y, t)  # 用多项式拟合
    p = np.poly1d(z)
    # print(p1)  # 在屏幕上打印拟合多项式
    # print(p1(30))
    # root = solution(copy.deepcopy(p1), 30)
    # s = list(filter(lambda r: 0 < r < 80 and r.imag == 0, root))
    # print(s)
    # print('----------------------------')
    yvals = p(x)  # 也可以使用yvals=np.polyval(z1,x)
    plt.plot(x, y, label='original values')
    plt.plot(x, yvals, 'r', label='polyfit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.legend(loc=1)  # 指定legend的位置
    plt.show()
    return p


def butter(x, b=0.36):
    """低通滤波"""
    b, a = signal.butter(3, b)
    sf = signal.filtfilt(b, a, x)
    return sf


def scale_line(data, limit):
    """线性缩放"""
    data_size = len(data)
    data_scale = []
    if data_size == limit:
        return data
    else:
        for i in range(limit):
            x = i * (data_size - 1) / (limit - 1)
            x_up = math.ceil(x)
            x_down = int(x)
            # if i == limit - 1:
            #     data_scale.append(data[data_size - 1])
            #     continue
            if x_up == x_down:
                data_scale.append(data[x_down])
                continue
            a = np.mat([[x_up, 1], [x_down, 1]])
            b = np.mat([data[x_up], data[x_down]]).T
            r = np.linalg.solve(a, b)
            y = r[0] * x + r[1]
            data_scale.append(float(y))
    return data_scale


def alignment_max(data_1, data_2, step_a=30):
    """根据最大值对齐"""
    max_p_1 = np.argmax(data_1)
    max_p_2 = np.argmax(data_2)
    if max_p_1 == max_p_2:
        return data_1, data_2
    size = len(data_1)
    right_l = min([size - max_p_1, size - max_p_2])
    left_l = min([max_p_1, max_p_2])
    if right_l + left_l < size - step_a:
        return data_1, data_2
    data_1 = data_1[max_p_1 - left_l:max_p_1 + right_l]
    data_2 = data_2[max_p_2 - left_l:max_p_2 + right_l]
    return data_1, data_2


def alignment_euc(data_1, data_2, step_a=7):
    """根据欧氏距离对齐"""
    r_euc = []
    l_euc = []
    for i in range(step_a):
        r_euc.append(euc_dist(data_1[i:], data_2[:(len(data_1) - i)]))
        l_euc.append(euc_dist(data_1[:(len(data_1) - i)], data_2[i:]))
    if min(r_euc) < min(l_euc):
        min_p = np.argmin(r_euc)
        if min_p == step_a - 1:
            return data_1, data_2, 0, 0
        else:
            return data_1[min_p:], data_2[:(len(data_1) - min_p)], 1, min_p
    else:
        min_p = np.argmin(l_euc)
        if min_p == step_a - 1:
            return data_1, data_2, 0, 0
        else:
            return data_1[:(len(data_1) - min_p)], data_2[min_p:], -1, min_p


def mov_dist(data_1, data_2, dire, distances):
    r_p = np.where(np.array(dire) > 0)
    l_p = np.where(np.array(dire) < 0)
    r_n = len(r_p[0])
    l_n = len(l_p[0])
    if l_n > 3:
        panning = int(np.average(np.array(distances)[l_p]))
        for i in range(8):
            data_1[i] = data_1[i][:(len(data_1[i]) - panning)]
            data_2[i] = data_2[i][panning:]
    elif r_n > 4:
        panning = int(np.average(np.array(distances)[r_p]))
        for i in range(8):
            data_1[i] = data_1[i][panning:]
            data_2[i] = data_2[i][:(len(data_2[i]) - panning)]
    return data_1, data_2


def alignment(data_1, data_2, comp=False):
    direction = []
    distance = []
    for i in range(8):
        a_d_1, a_d_2, dirc, dist = alignment_euc(data_1[i], data_2[i])
        direction.append(dirc)
        distance.append(dist)
        if comp:
            compared(data_1[i], data_2[i], i)
            compared(a_d_1, a_d_2, i)
    return mov_dist(data_1, data_2, direction, distance)


if __name__ == "__main__":
    # foot_data = get_pre_data('/home/ri/user/Tem/医院数据/积水潭/2018-03-27', 0)
    x_limit = 100
    point_limit = 6
    index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]

    file_n = '/1522114734_left.json'
    observer_patient_path = '/home/ri/Data/Observer/pa' + file_n
    observer_normal_path = '/home/ri/Data/Observer/no'
    patient_path = '/home/ri/Data/patient'

    obn_foot_data = get_pre_data(observer_normal_path, 0)
    obp_foot_data = get_pre_data(observer_patient_path, -1)
    # 对照组：正常 or 患者
    switching = 0
    # 是否使用分段 pearson
    switching_0 = 0
    # 是否使用对齐 alignment
    switching_1 = 0
    # 开关列表
    switch = [switching, switching_0, switching_1]
    g_count_ob = 0
    while True:
        try:
            print('---------------')
            if switching == 0:
                data_normal, f_o = next(obn_foot_data)
                print('对照组：正常人->' + f_o)
            else:
                data_normal, f_o = next(obp_foot_data)
                print('对照组：患者->' + f_o)
            data_normal = [scale_line(butter(data_normal[i]), x_limit) for i in range(8)]
            p_foot_data = get_pre_data(patient_path, 2)
            # data2plt(data_normal, normal_path)
            p_sq = np.zeros(point_limit)
            p_sh = np.zeros(point_limit)
            p_sq_n = 0
            p_sh_n = 0
            g_count = 0
            while True:
                try:
                    data_n = data_normal
                    show = False
                    # if g_count == 1:
                    #     data_p, filename = next(p_foot_data)
                    #     g_count += 1
                    #     continue
                    data_p, filename = next(p_foot_data)
                    data_p = [scale_line(butter(data_p[i]), x_limit) for i in range(8)]
                    pearson_list = []
                    if switching_1 == 0:
                        d_n, d_p = data_n, data_p
                    else:
                        d_n, d_p = alignment(data_n, data_p, show)
                    if switching_0 == 0:
                        for i in range(point_limit):
                            # compared(d_n[i], d_p[i], i)
                            pearson_list.append(pearson(d_n[i], d_p[i]))
                    else:
                        step = 3
                        unit = 10
                        # data2plt(d_n, filename)
                        # data2plt(d_p, filename)
                        for i in range(point_limit):
                            section = int(len(d_n[i]) / unit) - step + 1
                            unit_pearson = []
                            for j in range(section):
                                begin = j * unit
                                end = (j + step) * unit
                                unit_pearson.append(pearson(d_n[i][begin:end], d_p[i][begin:end]))
                            pearson_list.append(unit_pearson)
                            pearson_list[i] = sum([pearson_list[i][j] * 1 for j in range(section)]) / section
                    if filename[25:27] == '术后':
                        p_sh += np.array(pearson_list)
                        p_sh_n += 1
                    else:
                        p_sq += np.array(pearson_list)
                        p_sq_n += 1
                    # print('编号', g_count, ',路径', filename)
                    # print(pearson_list[:3])
                    # print(pearson_list[3:])
                    # print('---------------')
                    g_count += 1
                except StopIteration as e:
                    # print('Generator 1 is over, and return value:', g_count)
                    break
            p_sh = [p_sh[i] / p_sh_n for i in range(point_limit)]
            p_sq = [p_sq[i] / p_sq_n for i in range(point_limit)]
            print('术前：', p_sq)
            print('术后：', p_sh)
            g_count_ob += 1
        except StopIteration as e:
            # print('Generator 2 is over, and return value:', g_count_ob)
            break
    print('>>>>>>')
    print(switch)
# 读取C文件* weaken_coefficient[i][j]
# lib = load_library('/home/ri/a.so', '.')
# interpolate_foot = lib.interpolate_foot
# interpolate_foot.argtypes = [ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS'),
#                              ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS')]
# interpolate_foot.restype = None
# data_solve = []
# for prs in data_reshape:
#     grid = np.empty(660, dtype='f4')
#     interpolate_foot(np.array(prs).astype('f4'), grid)
#     # plt.imshow(grid.reshape((44, 15)), interpolation='nearest', origin='lower')
#     # plt.show()
#     result = cog(np.array(grid).reshape(int(len(grid) / 15), 15))
#     data_solve.append(result)
# 压力中心线
# data_solve = [cogr(i) for i in data_reshape]
