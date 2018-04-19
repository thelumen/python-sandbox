#!coding:utf-8

import math

import matplotlib.pyplot as plt
import numpy as np
import os


def g_file_path():
    count = 1
    while count < 14:
        direct_name = 'T' + str(count)
        home_path = '/home/ri/Data/' + direct_name
        prs_path = str(home_path) + '/prs'
        for parent_names, dir_names, file_names in os.walk(prs_path):
            for filename in file_names:
                yield prs_path + '/' + filename, filename[:-4]
        count += 1


def interception(begin, end, data_foot, filename):
    index_l_d_r = [1, 0, 6, 7, 5, 2, 3, 4]
    index_r_d_r = [6, 7, 0, 1, 3, 4, 5, 2]
    index_c = ['k', 'r', 'tan', 'orange', 'm', 'b', 'g', 'yellow']
    type_foot = index_r_d_r
    if filename[-4:] == 'left':
        type_foot = index_l_d_r
    for i in range(8):
        data_t = data_foot[type_foot[i]::8]
        plt.plot(data_t[begin:end], color=index_c[i])
    plt.title(filename)
    plt.ylim(0, 180)
    plt.show()


get_file_path = g_file_path()
with open('/home/ri/Data/interception.be', 'w+')as save_path:
    for i in range(330):
        complete = False
        file_path, file_name = next(get_file_path)
        data = np.array(np.fromfile(file_path, 'u1'), dtype='f4')
        while not complete:
            plt.cla()
            begin = input("Enter begin: ")
            end = input("Enter end: ")
            interception(int(begin), int(end), data, file_name)
            save = input("Save and Next :")
            if save == 'Y':
                save_path.write(str([file_path, begin, end]))
            if save == 'esc':
                complete = True
                break
        if input('exit:') == 'Y':
            break
