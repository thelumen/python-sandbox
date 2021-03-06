#!coding:utf-8
import math
import numpy as np


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


# Euclidean distance.
def euc_dist(pt1, pt2):
    return math.sqrt(sum([(pt1[i] - pt2[i]) ** 2 for i in range(len(pt1))]))


def _c(ca, i, j, p, q):
    if ca[i, j] > -1:
        return ca[i, j]
    elif i == 0 and j == 0:
        ca[i, j] = euc_dist(p[0], q[0])
    elif i > 0 and j == 0:
        ca[i, j] = max(_c(ca, i - 1, 0, p, q), euc_dist(p[i], q[0]))
    elif i == 0 and j > 0:
        ca[i, j] = max(_c(ca, 0, j - 1, p, q), euc_dist(p[0], q[j]))
    elif i > 0 and j > 0:
        ca[i, j] = max(min(_c(ca, i - 1, j, p, q), _c(ca, i - 1, j - 1, p, q), _c(ca, i, j - 1, p, q)),
                       (p[i] - q[j]))
    else:
        ca[i, j] = float("inf")
    return ca[i, j]


def frechet_distance(p, q):
    ca = np.ones((len(p), len(q)))
    ca = np.multiply(ca, -1)
    return _c(ca, len(p) - 1, len(q) - 1, p, q)


def mean(x, y):
    sum_x = sum(x)
    sum_y = sum(y)
    n = len(x)
    x_mean = float(sum_x + 0.0) / n
    y_mean = float(sum_y + 0.0) / n
    return x_mean, y_mean


def pearson(x, y):
    x_mean, y_mean = mean(x, y)
    n = len(x)
    sum_top = 0.0
    sum_bottom = 0.0
    x_pow = 0.0
    y_pow = 0.0
    for i in range(n):
        sum_top += (x[i] - x_mean) * (y[i] - y_mean)
    for i in range(n):
        x_pow += math.pow(x[i] - x_mean, 2)
    for i in range(n):
        y_pow += math.pow(y[i] - y_mean, 2)
        sum_bottom = math.sqrt(x_pow * y_pow)
    if sum_bottom == 0:
        return 0
    p = sum_top / sum_bottom
    return p


if __name__ == "__main__":
    a = [1, -2, 5, -4, 3, -2]
    a = np.array(a)
    b = a + 1
    c = pearson(a, b)
