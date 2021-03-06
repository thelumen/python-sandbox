#!coding:utf-8

import glob
import json
import math
import os
import pickle
import sys

import numpy as np

from svmutil import *
from svm import *
from sklearn import svm
from sklearn.externals import joblib
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


def pressure_2_data(path, x_limit, point_limit):
    re_path = path
    for i in range(4):
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
                obs = .0
                if 'Observer' in json_file:
                    obs = 1.0
                step = interception[i]
                data_step = [scale_line(a_data[step[0]:step[1]], x_limit) for a_data in pre_data]
                data_reshape = np.array(data_step).flatten().tolist()
                data_reshape.append(obs)
                data_set.append(data_reshape)
    return np.array(data_set)


def load_model():
    return joblib.load('/home/ri/ml/model/model.pkl')


def model_svm(svm_x, svm_y, c=1, g=1):
    clf = svm.SVC(C=c, kernel='poly', gamma=g, decision_function_shape='ovr')
    clf.fit(svm_x, svm_y.ravel())
    joblib.dump(clf, '/home/ri/ml/model/model.pkl')
    return clf


def save_train_data():
    x_l = 30
    p_l = [0, 2]
    test_path = '/home/ri/Data'
    data = pressure_2_data(test_path, x_l, p_l)
    x, y = np.split(data, [(x_l * (p_l[1] - p_l[0])), ], axis=1)
    with open('/home/ri/ml/train-data/x.txt', 'wb') as x_file:
        pickle.dump(x, x_file)
    with open('/home/ri/ml/train-data/y.txt', 'wb') as y_file:
        pickle.dump(y, y_file)


def load_train_data():
    with open('/home/ri/ml/train-data/x.txt', 'rb') as x_file:
        train_x = pickle.load(x_file)
    with open('/home/ri/ml/train-data/y.txt', 'rb') as y_file:
        train_y = pickle.load(y_file)
    return train_x, train_y


if __name__ == '__main__':
    # save_train_data()
    x, y = load_train_data()
    # x = x[:, :2]
    # x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=2)
    x_train = np.concatenate((x[:133], x[234:500]), axis=0)
    x_test = np.concatenate((x[134:233], x[500:]), axis=0)
    y_train = np.concatenate((y[:133], y[234:500]), axis=0)
    y_test = np.concatenate((y[134:233], y[500:]), axis=0)
    model_svm_1 = load_model()
    model_svm_2 = model_svm(x_train, y_train)
    print(model_svm_1.score(x_train, y_train))
    # y_hat = clf.predict(x_train)
    # print(y_hat, y_train, '训练集')
    print(model_svm_2.score(x_test, y_test))
    # y_hat = clf.predict(x_test)
    # print(y_hat, y_test, '测试集')
