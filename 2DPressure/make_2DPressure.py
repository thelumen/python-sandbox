#!coding:utf-8
import glob
import json
import os
import time

import numpy as np
import matplotlib.pyplot as plt

from docx import Document
from docx.shared import Pt
from docx.shared import Inches
from docx.oxml.ns import qn
from numpy.ctypeslib import load_library, ndpointer

from getpredata import get_dir_names, get_pre_and_step_data


def make_2d_pressure(path):
    patients = sorted(get_dir_names(path))
    for patient in patients:
        patient_data = os.path.join(path, patient)
        pa_f_d, pa_i_d, pa_p_d = get_pre_and_step_data(patient_data)


def get_lib_interpolate_foot():
    """读取C文件  arg[8],empty_arg[660]"""
    lib = load_library('/home/ri/a.so', '.')
    interpolate_foot = lib.interpolate_foot
    interpolate_foot.argtypes = [ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS'),
                                 ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS')]
    interpolate_foot.restype = None
    return interpolate_foot


if __name__ == '__main__':
    begin = time.time()
    patient_path = '/home/ri/Data/patient/足根'
    lib_if = get_lib_interpolate_foot()
    data_reshape = []
    for prs in data_reshape:
        grid = np.empty(660, dtype='f4')
        lib_if(np.array(prs).astype('f4'), grid)
        plt.imshow(grid.reshape((44, 15)), interpolation='nearest', origin='lower')
        plt.show()
