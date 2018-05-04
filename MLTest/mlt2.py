#!coding:utf-8

import pickle

import numpy as np
from svm import *
from svmutil import *


def save_libsvm(model):
    svm_save_model('/home/ri/ml/model/model_libsvm', model)


def load_libsvm():
    return svm_load_model('/home/ri/ml/model/model_libsvm')


def load_train_data():
    with open('/home/ri/ml/train-data/x.txt', 'rb') as x_file:
        train_x = pickle.load(x_file)
    with open('/home/ri/ml/train-data/y.txt', 'rb') as y_file:
        train_y = pickle.load(y_file)
    return train_x, train_y


def reload_train_data_4_libsvm(load_x):
    libsvm_data_x = []
    for a_x in load_x:
        d_x = {}
        for a in range(len(a_x)):
            if a_x[a] != 0:
                d_x[a] = a_x[a]
        libsvm_data_x.append(d_x)
    return libsvm_data_x


def make_libsvm_data(make_x, make_y):
    axis_2 = make_x[0].size
    with open('/home/ri/ml/train-data/libsvm.txt', 'w') as libsvm_file:
        for num_line in range(len(make_x)):
            libsvm_file.write(str(make_y[num_line]) + ' ')
            for a_value in range(axis_2):
                if make_x[num_line][a_value] == 0:
                    continue
                libsvm_file.write(str(a_value) + ':' + str(make_x[num_line][a_value]) + ' ')
            libsvm_file.write('\n')


if __name__ == '__main__':
    # x_load, y_load = load_train_data()
    # make_libsvm_data(x_load, y_load.ravel())
    # x = reload_train_data_4_libsvm(x_load)
    # y = y_load.ravel()
    y, x = svm_read_problem('/home/ri/ml/train-data/libsvm.txt')
    # x_train = np.concatenate((x[:133], x[234:500]), axis=0).tolist()
    # x_test = np.concatenate((x[134:233], x[500:]), axis=0).tolist()
    # y_train = np.concatenate((y[:133], y[234:500]), axis=0).tolist()
    # y_test = np.concatenate((y[134:233], y[500:]), axis=0).tolist()
    # prob = svm_problem(y, x)
    # param = svm_parameter('-t 2 -g 3.0517578125e-05 -c 8.0')
    # model = svm_train(prob, param)
    model = load_libsvm()
    p_label, p_acc, p_val = svm_predict(y, x, model)
    print(p_label)
