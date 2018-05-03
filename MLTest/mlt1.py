#!coding:utf-8

import glob
import json
import math
import os

import numpy as np
from sklearn.model_selection import train_test_split


def scale_line(data_list, limit):
    """线性缩放"""
    data_size = len(data_list)
    data_scale = []
    if data_size == limit:
        return data_list
    for i in range(limit):
        x = i * (data_size - 1) / (limit - 1)
        x_up = math.ceil(x)
        x_down = math.floor(x)
        if x_up == x_down:
            data_scale.append(data_list[x_down])
            continue
        a = np.mat([[x_up, 1], [x_down, 1]])
        b = np.mat([data_list[x_up], data_list[x_down]]).T
        r = np.linalg.solve(a, b)
        y = r[0] * x + r[1]
        data_scale.append(float(y))
    return data_scale


def extract_pressure(file_path):
    index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]
    index_l_d_r = [1, 0, 6, 7, 5, 2, 3, 4]
    file_data = np.fromfile(file_path, dtype='u1')
    num = len(file_data) // 508
    audio = np.empty((num, 40), dtype='u1')
    end = 444
    i = 0
    while i < num:
        np.copyto(audio[i], file_data[end - 40: end])
        end += 508
        i += 1
    audio = audio.reshape(-1)
    file_foot_type = os.path.split(file_path)[1].split('.')[0][-4:]
    type_foot = index_r_d_r
    if file_foot_type == 'left':
        type_foot = index_l_d_r
    data_t = []
    for i in range(8):
        data_t.append(audio[type_foot[i]::8])
    return data_t


def get_json(path):
    return glob.glob(path + '/*.json')


def pressure_2_data(path, deep, x_limit, point_limit):
    re_path = path
    for i in range(deep):
        re_path += '/*'
    json_file_path = glob.glob(re_path + '/*.json')
    json_file_path.extend(glob.glob(path + '/*/*/*.json'))
    data_set = []
    for json_file in json_file_path:
        data_file_path = json_file.replace('.json', '.dat')
        pre_data = extract_pressure(data_file_path)[point_limit[0]:point_limit[1]]
        with open(json_file, 'r') as load_file:
            load_json = json.load(load_file)
            interception = load_json['footstep']
            for i in range(len(interception)):
                obs = 0
                if 'observer' in json_file:
                    obs = 1
                print(obs)
                step = interception[i]
                data_step = [scale_line(a_data[step[0]:step[1]], x_limit) for a_data in pre_data]
                data_reshape = np.array(data_step).flatten().tolist()
                data_reshape.append(obs)
                data_set.append(data_reshape)
    return np.array(data_set)


if __name__ == '__main__':
    de = 4
    x_l = 30
    p_l = [0, 2]
    test_path = '/home/ri/Data'
    data = pressure_2_data(test_path, de, x_l, p_l)
    x, y = np.split(data, [(x_l * (p_l[1] - p_l[0])), ], axis=1)
    x = x[:, :2]
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, train_size=0.6)
