#!coding:utf-8
import json
import numpy as np
import matplotlib.pyplot as plt
import os

index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']


def get_dir_names(home_path):
    for parent_names, dir_names, file_names in os.walk(home_path):
        return dir_names


def get_file_names(home_path):
    for parent_names, dir_names, file_names in os.walk(home_path):
        return file_names


def get_file_path_info_0(home_path):
    for file_name in get_file_names(home_path):
        if os.path.splitext(file_name)[1] == '.json':
            yield home_path + '/' + file_name


def extract_pressure(file_path):
    index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]
    index_l_d_r = [1, 0, 6, 7, 5, 2, 3, 4]
    data = np.fromfile(file_path, dtype='u1')
    num = len(data) // 508
    audio = np.empty((num, 40), dtype='u1')
    end = 444
    i = 0
    while i < num:
        np.copyto(audio[i], data[end - 40: end])
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


def data2plt(data, filename):
    for i in range(8):
        plt.plot(data[i], color=index_c[i])
    plt.ylim(0, 180)
    plt.title(filename)
    plt.show()


def compared(c_d_1, c_d_2, no):
    plt.plot(c_d_1, label='observer', color='c')
    plt.plot(c_d_2, label='patient', color=index_c[no])
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.ylim(0, 180)
    plt.title(no)
    plt.show()


def get_pre_data(root_path, deep, show_plt=False):
    fpi = 0
    if deep == 0:
        fpi = get_file_path_info_0(root_path)
    result = []
    path = []
    g_count = 0
    while True:
        try:
            if deep == -1:
                file_path_info = root_path
            else:
                file_path_info = next(fpi)
            data = extract_pressure(file_path_info.replace('.json', '.dat'))
            with open(file_path_info, 'r') as load_file:
                print(file_path_info)
                load_json = json.load(load_file)
                interception = load_json['footstep']
                data_r = []
                for i in range(len(interception)):
                    step = interception[i]
                    data_r.append([a_data[step[0]:step[1]] for a_data in data])
                    if show_plt:
                        data2plt(data_r[i], file_path_info)
            g_count += 1
            result.append(data_r)
            path.append(file_path_info)
            if deep == -1:
                break
        except StopIteration as e:
            # print('Generator 0 is over, and return value:', g_count)
            break
    return result, path


def get_pre_and_step_data(root_path, deep):
    fpi = 0
    if deep == 0:
        fpi = get_file_path_info_0(root_path)
    data = []
    path = []
    interception = []
    # g_count = 0
    while True:
        try:
            if deep == -1:
                file_path_info = root_path
            else:
                file_path_info = next(fpi)
            json_data = extract_pressure(file_path_info.replace('.json', '.dat'))
            with open(file_path_info, 'r') as load_file:
                print(file_path_info)
                load_json = json.load(load_file)
                cut = load_json['footstep']
            # g_count += 1
            data.append(json_data)
            path.append(file_path_info)
            interception.append(cut)
            if deep == -1:
                break
        except StopIteration as e:
            # print('Generator 0 is over, and return value:', g_count)
            break
    return data, interception, path


if __name__ == "__main__":
    get_pre_data('/home/ri/user/Tem/医院数据', 1, show_plt=True)
