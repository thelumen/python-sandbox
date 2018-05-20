#!coding:utf-8
import glob
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


def get_file_with_suffix(path, suffix):
    return glob.glob(os.path.join(path, '*.' + suffix))


def get_json_file_path(path, suffix='json'):
    """获取路径下包括子目录下的全部.json文件"""
    json_file_path = []
    json_file_path.extend(get_file_with_suffix(path, suffix))
    for dir_name in get_dir_names(path):
        json_file_path.extend(get_json_file_path(os.path.join(path, dir_name), suffix))
    return json_file_path


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


def get_pre_data(root_path):
    result = []
    path = []
    for json_path in get_json_file_path(root_path):
        data = extract_pressure(json_path.replace('.json', '.dat'))
        with open(json_path, 'r') as load_file:
            print(json_path)
            load_json = json.load(load_file)
            interception = load_json['footstep']
            data_r = []
            for i in range(len(interception)):
                step = interception[i]
                data_r.append([a_data[step[0]:step[1]] for a_data in data])
        result.append(data_r)
        path.append(json_path)
    return result, path


def get_pre_and_step_data(root_path):
    """
        根据路径获取压力数据

        return-----------
        data : 压力数据
        path : 压力数据的路径
        interception : 截断列表
    """
    data = []
    path = []
    interception = []
    for json_path in get_json_file_path(root_path):
        json_data = extract_pressure(json_path.replace('.json', '.dat'))
        with open(json_path, 'r') as load_file:
            print(json_path)
            load_json = json.load(load_file)
            cut = load_json['footstep']
        data.append(json_data)
        path.append(json_path)
        interception.append(cut)
    return data, path, interception


if __name__ == "__main__":
    get_pre_and_step_data('/home/ri/user/Tem/医院数据/积水潭')

