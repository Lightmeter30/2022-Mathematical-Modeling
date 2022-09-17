# -*- coding: utf-8 -*-
# @Time    : 2022/9/9 18:06
# @Author  : LuMing
# @File    : bpnn.py
# @Software: PyCharm 
# @Comment : python3.10
import numpy as np
import pandas as pd
import xlwt


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def derived_sigmoid(x):
    return x * (1 - x)


def make_matrix(m, n, fill=0.0):  # m行n列
    a = []
    for i in range(m):
        a.append([fill] * n)
    return np.array(a)


def softmax(array):  # 这个函数的作用是将一组数据转化为概率的形式
    n = 0
    for i in array:
        n += np.exp(i)
    return array / n


def save(rows, name):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sheet")

    for i in range(1, len(rows) + 1):
        for j in range(len(rows[i - 1])):
            sheet.write(i, j, rows[i - 1][j])

    workbook.save(name + ".xls")


def error_func(yo_vector, targets):
    return 0.5 * np.dot((targets - yo_vector).T,
                        (targets - yo_vector))


class Bpnn:  # BP neural network 一个三层的BP神经网络
    def __init__(self, x_num, h_num, y_num):
        self.x_num = x_num + 1  # 添加一个偏置
        self.h_num = h_num
        self.y_num = y_num

        # 初始化向量
        self.x_vector = np.array([0.0] * self.x_num)
        self.hi_vector = np.array([0.0] * self.h_num)
        self.ho_vector = np.array([0.0] * self.h_num)
        self.yi_vector = np.array([0.0] * self.y_num)
        self.yo_vector = np.array([0.0] * self.y_num)

        # 初始化权值矩阵
        self.weight_xh = (np.random.random([self.x_num, self.h_num]) - 0.51)  # 输入数据到隐藏层输入的变换矩阵
        self.weight_hy = (np.random.random([self.h_num, self.y_num]) - 0.51)  # 隐藏层输出到输出层输入的变换矩阵
        # 学习率
        self.lr = 0.1

        # 动量因子
        self.input_correction = make_matrix(self.x_num, self.h_num)
        self.output_correction = make_matrix(self.h_num, self.y_num)

    def forward_propagation(self, x_vector):  # 正向传播
        if len(x_vector) != self.x_num - 1:
            raise ValueError("输入数据与输入结点数量不同")

        # 简单的处理一下输入数据
        self.x_vector[1:self.x_num] = x_vector
        self.x_vector = np.array(self.x_vector)

        # 输入层->隐藏层
        self.hi_vector = np.dot(self.x_vector, self.weight_xh)
        # print(self.hi_vector)

        # 激活隐藏层神经元
        self.ho_vector = np.array(sigmoid(self.hi_vector))
        # print(self.ho_vector)

        # 隐藏层->输出层
        self.yi_vector = np.dot(self.ho_vector, self.weight_hy)
        # print(self.yi_vector)

        # 激活输出层神经元
        self.yo_vector = np.array(sigmoid(self.yi_vector))
        # print(self.yo_vector)

        return self.yo_vector

    def backward_propagation(self, labels, correct):
        if len(labels) != self.y_num:
            raise ValueError("标记数量与输出数量不符")

        targets = np.array(labels)  # 简单处理输入

        # 计算误差
        error = 0.5 * np.dot((targets - self.yo_vector).T,
                             (targets - self.yo_vector))

        # 计算残差
        delta_hy = np.array((targets - self.yo_vector) * derived_sigmoid(self.yo_vector))
        delta_xh = np.array(np.dot(delta_hy, self.weight_hy.T) * derived_sigmoid(self.ho_vector))

        # 更新权值
        # print(self.weight_xh)
        self.weight_hy += self.lr * np.dot(delta_hy.reshape(-1, 1),
                                           self.ho_vector.reshape(1, -1)).T + correct * self.output_correction

        self.weight_xh += self.lr * np.dot(delta_xh.reshape(-1, 1),
                                           self.x_vector.reshape(1, -1)).T + correct * self.input_correction

        # 更新
        self.output_correction = self.lr * np.dot(delta_hy.reshape(-1, 1), self.ho_vector.reshape(1, -1)).T
        self.input_correction = self.lr * np.dot(delta_xh.reshape(-1, 1), self.x_vector.reshape(1, -1)).T
        return error

    def train(self, train_data, train_label, loop):
        if len(train_label) != len(train_data):
            raise ValueError("训练数据与标签数量不符")

        for k in range(loop):
            error = 0
            for i in range(len(train_data)):
                self.forward_propagation(train_data[i])
                error += self.backward_propagation(train_label[i], 0.1)
            if k % 100 == 0:
                print('########################误差 %-.5f######################第%d次迭代' % (error / len(train_data), k))

    def test(self, test_data, test_label):
        if len(test_label) != len(test_data):
            raise ValueError("测试数据与标签数量不符")
        error = 0
        for i in range(len(test_data)):
            yo_vector = self.forward_propagation(test_data[i])
            error += error_func(yo_vector, test_label[i])
        print("全局误差：%f" % (error / len(test_label)))
        print("测试完成")

    def saveMatrix(self, xh_name, hy_name):
        save(self.weight_xh, xh_name)
        save(self.weight_hy, hy_name)

    def getWeightFromXlsx(self, xh_xlsx_path, hy_xlsx_path):
        self.weight_xh = np.array(pd.read_excel(xh_xlsx_path, "Sheet"))
        self.weight_hy = np.array(pd.read_excel(hy_xlsx_path, "Sheet"))

    def predict(self, data):
        return self.forward_propagation(data)
