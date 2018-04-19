#!coding:utf-8
import numpy as np
import math


def scale_line(data, limit):
    """线性缩放"""
    data_size = len(data)
    data_scale = []
    if data_size == limit:
        return data
    else:
        for i in range(limit):
            x = i * data_size / (limit + 1)
            x_up = math.ceil(x)
            x_down = int(x)
            if x_up == x_down:
                data_scale.append(data[x_down])
                continue
            A = np.mat([[x_up, 1], [x_down, 1]])
            b = np.mat([data[x_up], data[x_down]]).T
            r = np.linalg.solve(A, b)
            y = r[0] * x + r[1]
            data_scale.append(float(y))
    return data_scale


a = [1, 2, 2, 1]
b = scale_line(a, 7)
print(b)
