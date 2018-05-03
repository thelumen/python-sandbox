#!coding:utf-8

import math
import os
import time
import matplotlib.pyplot as plt
import numpy as np

from scipy import signal
from getpredata import get_pre_and_step_data, data2plt, compared, get_dir_names, get_file_names
from pearson import pearson, euc_dist

index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']


def get_file_name(path):
    return os.path.split(os.path.splitext(path)[0])[1]


def get_parent_path(path):
    return os.path.split(path)[0]


def get_file(path):
    return os.path.split(path)[1]


def get_foot_type(path, l):
    return os.path.split(path)[1].split('.')[0][-l:]


def equ_list(list_1, list_2):
    if len(list_1) != len(list_2):
        return False
    for i in list_1:
        if i not in list_2:
            return False
    for i in list_2:
        if i not in list_1:
            return False
    return True


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
        x_down = math.floor(x)
        if x_up == x_down:
            data_scale.append(data[x_down])
            continue
        a = np.mat([[x_up, 1], [x_down, 1]])
        b = np.mat([data[x_up], data[x_down]]).T
        r = np.linalg.solve(a, b)
        y = r[0] * x + r[1]
        data_scale.append(float(y))
    return data_scale


def sorted_position(data, point_limit):
    data_size = len(data)
    data_sort_matrix = np.zeros((data_size, point_limit))
    for j in range(point_limit):
        data_sort_p = np.argsort(np.array([data[i][j] for i in range(data_size)]))
        for i in range(data_size):
            data_sort_matrix[data_sort_p[i]][j] = i
    return np.argsort(np.array([sum(i) for i in data_sort_matrix]))


def process_data(foot_data, step, limit, offset):
    foot_data_process = [[scale_line(butter(a_data[step[0]:step[1]]), limit) for a_data in foot_data]]
    for i in range(1, offset):
        foot_data_process.append([scale_line(butter(a_data[step[0] + i:step[1] + i]), limit) for a_data in foot_data])
        foot_data_process.append([scale_line(butter(a_data[step[0] - i:step[1] - i]), limit) for a_data in foot_data])
    return foot_data_process


def alignment_re(data_ob, data_pa, step_ob, step_pa, switch, limit, point_limit, offset=2):
    result = []
    ob_offset = process_data(data_ob, step_ob, limit, offset)
    pa_offset = process_data(data_pa, step_pa, limit, offset)
    for ob in ob_offset:
        for pa in pa_offset:
            if equ_list(ob, pa):
                continue
            cmp_group = []
            for i in range(point_limit):
                if switch[3] == 0:
                    cmp_group.append(pearson(ob[i], pa[i]))
                else:
                    cmp_group.append(euc_dist(ob[i], pa[i]))
            result.append(cmp_group)
    data_sort = sorted_position(result, point_limit)
    if switch[3] == 0:
        return result[data_sort[len(result) - 1]]
    else:
        return result[data_sort[0]]


def similarity_re(ob_data, ob_step, pa_data, pa_step, switch, limit, point_limit, data_del):
    similarity_list = []
    cmp_zero = np.zeros(point_limit).tolist()
    cmp_one = np.ones(point_limit).tolist()
    for ob in range(len(ob_data)):
        for pa in range(len(pa_data)):
            for step_ob in ob_step[ob]:
                for step_pa in pa_step[pa]:
                    re_a = alignment_re(ob_data[ob], pa_data[pa], step_ob, step_pa, switch, limit, point_limit)
                    if switch[3] == 0:
                        if re_a == cmp_one:
                            continue
                        else:
                            similarity_list.append(re_a)
                    else:
                        if re_a == cmp_zero:
                            continue
                        else:
                            similarity_list.append(re_a)
    if data_del != 0:
        result_list = np.zeros(point_limit)
        if switch[3] == 0:
            sort_list = sorted_position(similarity_list, point_limit)[data_del:]
        else:
            sort_list = sorted_position(similarity_list, point_limit)[:-data_del]
        for i in sort_list:
            result_list += similarity_list[i]
        return result_list / (len(similarity_list) - data_del)
    return [sum([j[i] for j in similarity_list]) / len(similarity_list) for i in range(point_limit)]


def observer_stability(path, switch, point_limit):
    data_del = 0
    size_limit = 50
    group = {}
    patients = sorted(get_dir_names(path))
    file_n = 0
    for patient in patients:
        if file_n != 0:
            file_n += 1
            continue
        patient_data = path + '/' + patient
        pa_f_d, pa_i_d, pa_p_d = get_pre_and_step_data(patient_data, 0)
        group_type = {}
        if switch[0] == 0:
            pa_l_f_d = []
            pa_l_i_d = []
            pa_r_f_d = []
            pa_r_i_d = []
            for i in range(len(pa_p_d)):
                if get_foot_type(pa_p_d[i], 4) == 'left':
                    pa_l_f_d.append(pa_f_d[i])
                    pa_l_i_d.append(pa_i_d[i])
                else:
                    pa_r_f_d.append(pa_f_d[i])
                    pa_r_i_d.append(pa_i_d[i])
            left = False
            right = False
            if switch[4] == 0:
                for i in range(len(pa_p_d)):
                    if not left:
                        if get_foot_type(pa_p_d[i], 4) == 'left':
                            group_type['left'] = similarity_re(pa_l_f_d, pa_l_i_d, pa_l_f_d, pa_l_i_d,
                                                               switch, size_limit, point_limit, int(data_del / 2))
                            left = True
                    if not right:
                        if get_foot_type(pa_p_d[i], 5) == 'right':
                            group_type['right'] = similarity_re(pa_r_f_d, pa_r_i_d, pa_r_f_d, pa_r_i_d,
                                                                switch, size_limit, point_limit, int(data_del / 2))
                            right = True
                group[patient] = group_type
            else:
                group[patient] = similarity_re(pa_l_f_d, pa_l_i_d, pa_r_f_d, pa_r_i_d, switch, size_limit, point_limit,
                                               data_del)
        else:
            group[patient] = similarity_re(pa_f_d, pa_i_d, pa_f_d, pa_i_d, switch, size_limit, point_limit, data_del)
        file_n += 1
    return group


if __name__ == "__main__":
    begin = time.time()
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
    # 是否使用剔除
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
            print('----------------', condition)
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
    print(switch_list, '耗时：' + str((time.time() - begin) / 60))
