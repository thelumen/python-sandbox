#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

rootdir = "/home/ri/user/Tem/"
rootdir_list = ['2018-02-12']

outfilepath = "/home/ri/Data/"
outfile_list = ['T13']


def data_seprate(openfile_name, root_dir, outfile_path):
    f = open(root_dir + '/' + openfile_name + '.dat', 'rb')
    out = [open(outfile_path + '/pcm/' + openfile_name + '.pcm', 'wb'),
           open(outfile_path + '/prs/' + openfile_name + '.prs', 'wb'),
           open(outfile_path + '/imu/' + openfile_name + '.imu', 'wb')]
    mode = 0
    limit = [8, 408, 448, 508]
    index = 4
    while True:
        data = f.read(1024 * 4)
        length = len(data)
        if length == 0:
            break
        while length > 0:
            cur_limit = limit[mode]
            if index + length < cur_limit:
                if mode > 0:
                    out[mode - 1].write(data)
                index += length
                length = 0
            else:
                if mode > 0:
                    out[mode - 1].write(data[: cur_limit - index])
                data = data[cur_limit - index:]
                length -= cur_limit - index
                mode += 14
                if mode == 4:
                    mode = 0
                    index = 0
                else:
                    index = cur_limit
    f.close()
    for o in out:
        o.close()


if __name__ == '__main__':
    for i in range(len(rootdir_list)):
        for parent, dirnames, filenames in os.walk(rootdir + rootdir_list[i]):
            for filename in filenames:
                data_seprate(filename[:-4], rootdir + rootdir_list[i], outfilepath + outfile_list[i])
