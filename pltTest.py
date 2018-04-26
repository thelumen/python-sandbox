#!coding:utf-8
import math
import os
import matplotlib.pyplot as plt
import numpy as np

from scipy import signal
from getpredata import get_pre_data, data2plt, compared, get_dir_names, get_file_names
from pearson import pearson, euc_dist

index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']


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


def save_image(foot_data, path_data):
    for json in range(len(foot_data)):
        for step in range(len(foot_data[json])):
            for i in range(8):
                plt.plot(foot_data[json][step][i], color=index_c[i])
            plt.ylim(0, 180)
            file_name = get_file_name(path_data[json])
            patient_name = os.path.split(file_name[0])
            p_condition = os.path.split(patient_name[0])
            if p_condition == '术前':
                p_condition = 'before'
            else:
                p_condition = 'after'
            title = p_condition[0] + '/img/' + p_condition[1] + '/' + patient_name[1] + '/' + file_name[1] + '_' + str(
                step) + '.png'
            plt.title(title)
            plt.savefig(title)
            plt.close()


def get_file_name(path):
    return os.path.split(os.path.splitext(path)[0])[1]


def get_parent_path(path):
    return os.path.split(path)[0]


def get_file(path):
    return os.path.split(path)[1]


def get_foot_type(path, l):
    return os.path.split(path)[1].split('.')[0][-l:]


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
    for i in range(limit):
        x = i * (data_size - 1) / (limit - 1)
        x_up = math.ceil(x)
        x_down = int(x)
        if x_up == x_down:
            data_scale.append(data[x_down])
            continue
        a = np.mat([[x_up, 1], [x_down, 1]])
        b = np.mat([data[x_up], data[x_down]]).T
        r = np.linalg.solve(a, b)
        y = r[0] * x + r[1]
        data_scale.append(float(y))
    return data_scale


def alignment_euc(data_1, data_2, step_a=3):
    """根据欧氏距离对齐"""
    r_euc = []
    l_euc = []
    for i in range(step_a):
        r_euc.append(euc_dist(data_1[i:], data_2[:(len(data_1) - i)]))
        l_euc.append(euc_dist(data_1[:(len(data_1) - i)], data_2[i:]))
    if min(r_euc) < min(l_euc):
        min_p = np.argmin(r_euc)
        return data_1[min_p:], data_2[:(len(data_1) - min_p)], 1, min_p
    else:
        min_p = np.argmin(l_euc)
        return data_1[:(len(data_1) - min_p)], data_2[min_p:], -1, min_p


def mov_dist(data_1, data_2, dire, distances, point_limit):
    r_p = np.where(np.array(dire) > 0)
    l_p = np.where(np.array(dire) < 0)
    r_n = len(r_p[0])
    l_n = len(l_p[0])
    if l_n > 3:
        panning = int(np.average(np.array(distances)[l_p]))
        for i in range(point_limit):
            data_1[i] = data_1[i][:(len(data_1[i]) - panning)]
            data_2[i] = data_2[i][panning:]
    elif r_n > 4:
        panning = int(np.average(np.array(distances)[r_p]))
        for i in range(point_limit):
            data_1[i] = data_1[i][panning:]
            data_2[i] = data_2[i][:(len(data_2[i]) - panning)]
    return data_1, data_2


def alignment(data_1, data_2, point_limit, comp=False):
    direction = []
    distance = []
    for i in range(point_limit):
        a_d_1, a_d_2, dirc, dist = alignment_euc(data_1[i], data_2[i])
        direction.append(dirc)
        distance.append(dist)
        if comp:
            compared(data_1[i], data_2[i], i)
            compared(a_d_1, a_d_2, i)
    return mov_dist(data_1, data_2, direction, distance, point_limit)


def similarity(ob_foot_data, pa_foot_data, switch, p=6):
    x_limit = 50
    point_limit = p
    weighted = [[0.2, 0.4, 1.6, 1.9, 1.7, 1.6, 0.4, 0.2],
                [0.2, 0.4, 1.6, 1.9, 1.7, 1.6, 0.4, 0.2],
                [0.6, 0.6, 0.7, 1.3, 1.4, 1.4, 1.3, 0.7],
                [0.6, 0.6, 0.7, 1.3, 1.4, 1.4, 1.3, 0.7],
                [0.6, 0.6, 0.7, 1.3, 1.4, 1.4, 1.3, 0.7],
                [0.7, 0.7, 0.7, 0.9, 0.9, 0.7, 0.7, 0.7],
                [0.7, 0.7, 0.7, 0.9, 0.9, 0.7, 0.7, 0.7],
                [0.8, 0.8, 0.8, 0.8, 1, 1.6, 1.4, 0.8]]
    comp_group = []
    comp_zero = np.zeros(point_limit).tolist()
    for ob in range(len(ob_foot_data)):
        for o_f_step in ob_foot_data[ob]:
            for pa in range(len(pa_foot_data)):
                for p_f_step in pa_foot_data[pa]:
                    o_foot_step = o_f_step
                    p_step_data = p_f_step
                    similarity_step = []
                    data_normal = [scale_line(butter(o_foot_step[i]), x_limit) for i in range(point_limit)]
                    data_patient = [scale_line(butter(p_step_data[i]), x_limit) for i in range(point_limit)]
                    # 对齐方法开关
                    if switch[1] == 0:
                        d_n, d_p = data_normal, data_patient
                    else:
                        d_n, d_p = alignment(data_normal, data_patient, point_limit)
                    # 分段方法开关
                    if switch[2] == 0:
                        for i in range(point_limit):
                            # pearson or euc
                            if switch[3] == 0:
                                similarity_step.append(pearson(d_n[i], d_p[i]))
                            else:
                                similarity_step.append(euc_dist(d_n[i], d_p[i]))
                    else:
                        step = 3
                        unit = 10
                        section = int(len(d_n[0]) / unit) - step + 1
                        if section != 8:
                            re_w = [scale_line(weighted[i], section) for i in range(8)]
                        else:
                            re_w = weighted
                        for i in range(point_limit):
                            # compared(d_n[i], d_p[i], i)
                            unit_pearson = []
                            for j in range(section):
                                begin = j * unit
                                end = (j + step) * unit
                                # pearson or euc
                                if switch[3] == 0:
                                    unit_pearson.append(
                                        (pearson(d_n[i][begin:end], d_p[i][begin:end])) * re_w[i][j] / section)
                                else:
                                    unit_pearson.append(
                                        (euc_dist(d_n[i][begin:end], d_p[i][begin:end])) * re_w[i][j] / section)
                            similarity_step.append(sum(unit_pearson))
                    if comp_zero == similarity_step:
                        continue
                    else:
                        comp_group.append(similarity_step)
    group_size = len(comp_group)
    group_del = int(group_size / 10)
    final_size = group_size - group_del
    group_variance = []
    for i in range(group_size):
        group_variance.append([np.var(comp_group[i]), comp_group[i]])
    group_v = sorted(group_variance, key=lambda x: x[0])[:final_size]
    result = np.zeros(point_limit)
    for i in range(final_size):
        result += group_v[i][1]
    return result / final_size


def observer_stability(path, switch, point_limit):
    group = {}
    patients = sorted(get_dir_names(path))
    for patient in patients:
        # if file_n != 2:
        #     file_n += 1
        #     continue
        patient_data = path + '/' + patient
        pa_f_d, pa_p_d = get_pre_data(patient_data, 0)
        group_type = {}
        if switch[0] == 0:
            pa_l_f_d = []
            pa_r_f_d = []
            for i in range(len(pa_p_d)):
                if get_foot_type(pa_p_d[i], 4) == 'left':
                    pa_l_f_d.append(pa_f_d[i])
                else:
                    pa_r_f_d.append(pa_f_d[i])
            left = False
            right = False
            if switch[4] == 0:
                for i in range(len(pa_p_d)):
                    if not left:
                        if get_foot_type(pa_p_d[i], 4) == 'left':
                            group_type['left'] = similarity(pa_l_f_d, pa_l_f_d, switch, point_limit)
                            left = True
                    if not right:
                        if get_foot_type(pa_p_d[i], 5) == 'right':
                            group_type['right'] = similarity(pa_r_f_d, pa_r_f_d, switch, point_limit)
                            right = True
                            group[patient] = group_type
            else:
                group[patient] = similarity(pa_f_d, pa_f_d, switch, point_limit)
        else:
            group[patient] = similarity(pa_f_d, pa_f_d, switch, point_limit)
    return group


if __name__ == "__main__":
    observer_normal_path = '/home/ri/Data/Observer/no'
    patient_path = '/home/ri/Data/patient/足根'
    # 正常人 压力线绘制
    # pa_f_d, pa_p_d = get_pre_data(observer_normal_path, 0)
    # for json in range(len(pa_f_d)):
    #     for step in range(len(pa_f_d[json])):
    #         for i in range(8):
    #             plt.plot(pa_f_d[json][step][i], color=index_c[i])
    #         plt.ylim(0, 180)
    #         img = get_file_name(pa_p_d[json])
    #         info = get_parent_path(get_parent_path(pa_p_d[json])) + '/img/' + str(img) + '_' + str(step) + '.png'
    #         plt.title(info)
    #         plt.savefig(info)
    #         plt.close()

    # 点数限制
    p_l = 2
    # 单侧 or 双侧
    switching = 0
    # 是否使用对齐
    switching_1 = 0
    # 是否使用分段
    switching_2 = 0
    # pearson or euc
    switching_3 = 0
    # 相同 or 不同
    switching_4 = 0
    # 开关序列
    switch_list = [switching, switching_1, switching_2, switching_3, switching_4]

    sq_group = observer_stability(patient_path + '/术前', switch_list, p_l)
    sh_group = observer_stability(patient_path + '/术后', switch_list, p_l)
    if switching == 0 and switching_4 == 0:
        for key in sq_group.keys():
            turn = 0
            print(key)
            print('术前: L-> ', [round(i, 4) for i in sq_group[key]['left']])
            print('术后: L-> ', [round(i, 4) for i in sh_group[key]['left']])
            condition = []
            for i in range(p_l):
                if sq_group[key]['left'][i] < sh_group[key]['left'][i]:
                    if switching_3 == 0:
                        condition.append('好')
                        turn += 1
                    else:
                        condition.append('坏')
                else:
                    if switching_3 == 0:
                        condition.append('坏')
                    else:
                        turn += 1
                        condition.append('好')
            print('----------------', condition)
            print('术前: R-> ', [round(i, 4) for i in sq_group[key]['right']])
            print('术后: R-> ', [round(i, 4) for i in sh_group[key]['right']])
            condition = []
            for i in range(p_l):
                if sq_group[key]['right'][i] < sh_group[key]['right'][i]:
                    if switching_3 == 0:
                        turn += 1
                        condition.append('好')
                    else:
                        condition.append('坏')
                else:
                    if switching_3 == 0:
                        condition.append('坏')
                    else:
                        turn += 1
                        condition.append('好')
            print('----------------', condition, '^__')
            print('----------------------------------', turn)
    else:
        for key in sq_group.keys():
            turn = 0
            print(key)
            print('术前: ', [round(i, 4) for i in sq_group[key]])
            print('术后: ', [round(i, 4) for i in sh_group[key]])
            condition = []
            for i in range(p_l):
                if sq_group[key][i] < sh_group[key][i]:
                    if switching_3 == 0:
                        condition.append('好')
                        turn += 1
                    else:
                        condition.append('坏')
                else:
                    if switching_3 == 0:
                        condition.append('坏')
                    else:
                        turn += 1
                        condition.append('好')
            print('----------------', condition)
            print('----------------------------------', turn)
    print(switch_list)
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
