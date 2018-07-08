#!coding:utf-8
from urllib import request
from pyquery import PyQuery as pq
import pymysql
import time


class Hospital:
    def __init__(self, name, province, city, area):
        tem = 0
        self.name = name
        self.province = province
        self.city = city
        self.area = area
        self.address = tem
        self.phone = tem
        self.grade = tem
        self.operation = tem
        self.email = tem

    def insert_info(self, info):
        key = info[:5]
        value = info[5:]
        if key == '医院地址：':
            self.address = value
        elif key == '联系电话：':
            self.phone = value
        elif key == '医院等级：':
            self.grade = value
        elif key == '经营方式：':
            self.operation = value
        elif key == '电子邮箱：':
            self.email = value
        else:
            return 0

    @staticmethod
    def judge(info):
        hospital_list = ['医院地址：', '联系电话：', '医院等级：', '经营方式：', '电子邮箱：']
        if info[:5] in hospital_list:
            return 1
        else:
            return 0

    def __str__(self):
        return '医院：%s \n地址：%s \n省份：%s \n城市：%s \n区域：%s \n电话：%s \n等级：%s \n类型：%s \n邮箱：%s \n------------\n' % (
            self.name, self.address, self.province, self.city, self.area, self.phone, self.grade, self.operation,
            self.email)


def insert_mysql(info):
    # 打开数据库连接
    db = pymysql.connect(host='192.168.1.203', port=3306, user='root',
                         passwd='Zkhc,.2017', db='znkf_new', charset='utf8')
    cursor = db.cursor()
    try:
        effect_row = cursor.executemany('INSERT INTO sys_hospital\
                      (province,city,region, name, address, grade,phone,email,operation)\
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                        [(h_i.province, h_i.city, h_i.area, h_i.name, h_i.address, h_i.grade,
                                          h_i.phone, h_i.email, h_i.operation) for h_i in info])
        print("完成数 : %s " % effect_row)
        print('-----------------------------------------')
        db.commit()
    except:
        print('出错')
        print('-----------------------------------------')
        db.rollback()
    db.close()


# 城市页面处理
def solve_city(province, city, base_url, test_print=0):
    p = pq(get_html(base_url))
    print('获取%s成功' % city)
    p_t = 0
    area_url = {}
    if province[-1:] == '省' or province[-3:] == '自治区':
        for p_i in p('ul').eq(0).children().items():
            link = p_i.children().attr('href')
            area_url[p_i.text()] = 'http://www.a-hospital.com' + link
    elif province[-1:] == '市':
        for h_i in p('p').items():
            if p_t == 0:
                p_t = 1
                continue
            for j in h_i.children().items():
                area_url[j.text()] = 'http://www.a-hospital.com' + j.attr('href')
            break
    hospital_info = []
    for a in area_url:
        d = pq(get_html(area_url[a]))
        print('获取%s成功' % a)
        t = d('ul').items()

        for h_i in t:  # ->ul
            for j in h_i.children().items():  # ->li
                hospital = 0
                for k in j.children().items():  # ->b,ui
                    if hospital == 0:
                        if len(k('b')) == 0:
                            break
                        else:
                            hospital = Hospital(k.text(), province, city, a)
                    else:
                        if hospital != 0:  # ->b
                            for x in k.children().items():  # ->li
                                hospital.insert_info(x.text())
                            hospital_info.append(hospital)
                            hospital = 0

    if test_print == 1:
        # 打印
        print('-----------------------------------------')
        print('获取%s %s %d家医院成功' % (province, city, len(hospital_info)))
    return hospital_info


def solve_province(url):
    base_prefix = 'http://www.a-hospital.com'
    country = pq(get_html(url))
    city_dict = {}
    province_dict = {}
    area_dict = {}
    province_list = country('h3').items()
    for i in province_list:
        sort_info = i.text()
        if sort_info[-1:] == '市':
            city_dict[sort_info] = 0
        elif sort_info[-1:] == '省' or sort_info[-3:] == '自治区':
            province_dict[sort_info] = 0
    offset = 3
    begin = 0
    effective_area = 0
    p_list = True
    province = 0
    province_p = country('p').items()
    for i in province_p:
        # 剔除前置无效行
        if begin != offset:
            begin += 1
            continue
        if p_list:
            list_info = i.text()[:-4]
            if list_info[-1:] == '市':
                if list_info in city_dict:
                    href = i.children().children().attr('href')
                    area_dict[list_info] = [list_info, '%s%s' % (base_prefix, href)]
            elif list_info[-1:] == '省' or list_info[-3:] == '自治区':
                if list_info in province_dict:
                    province = list_info
                    effective_area = 1
                    p_list = False
            continue
        else:
            if effective_area == 0:
                continue
            elif effective_area == 1:
                for province_i in i.children().items():
                    area_dict[province_i.text()] = [province, '%s%s' % (base_prefix, province_i.attr('href'))]
                p_list = True
    return area_dict


def get_html(url):
    proxy_list = [
        '220.191.103.69:808',
        '218.106.98.166:53281'
    ]
    proxy = {'http': proxy_list[1]}
    proxy_support = request.ProxyHandler(proxy)
    opener = request.build_opener(proxy_support)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0')]
    request.install_opener(opener)
    html = 0
    while html == 0:
        try:
            time.sleep(1)
            response = request.urlopen(url)
            html = response.read().decode("utf-8")
        except:
            print('出错')
    # print(html)
    return html


if __name__ == '__main__':
    country_url = 'http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'
    # print(get_html('http://www.a-hospital.com/w/%E4%B8%8A%E6%B5%B7%E5%B8%82%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'))
    solve_city('江苏省', '苏州市',
               'http://www.a-hospital.com/w/%E4%B8%8A%E6%B5%B7%E5%B8%82%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8', 1)
    # print("Start : %s" % time.ctime())
    # city_info_dict = solve_province(country_url)
    # f_list = ['上海市']
    # c_list = ['北京市', '天津市', '重庆市']
    # for i in city_info_dict:
    #     if i in c_list:
    #         continue
    #     city_info = city_info_dict[i]
    #     print('%s  %s  %s' % (city_info[0], i, city_info[1]))
    #     hospital_info_list = solve_city(city_info[0], i, city_info[1], 1)
    #     # 录入数据库
    #     insert_mysql(hospital_info_list)
    # print("End : %s" % time.ctime())
