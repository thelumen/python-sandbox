#!coding:utf-8
import pymysql
import time
import sched
import random
from reptile.hospital import Hospital
from urllib import request
from pyquery import PyQuery as pq


# 随机延时
def time_delayed(delayed=3, random_l=2):
    time.sleep(delayed + random.uniform(0, random_l))


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
            time_delayed(1)
            response = request.urlopen(url)
            html = response.read().decode("utf-8")
        except Exception as e:
            try:
                if e.code == 404:
                    print('->访问 %s 失败' % url)
                    break
            except:
                print('->出错 重试 %s' % e)
    # print(html)
    return html


def get_pq_with_url(url, use_agent=0, delayed=3):
    p = 0
    retry = 5
    if use_agent == 0:
        while p == 0:
            try:
                time_delayed(delayed)
                p = pq(url)
            except Exception as e:
                if e.code == 404:
                    print('->not found %s' % url)
                    break
                else:
                    if retry > 0:
                        print('->出错重试 %s' % retry)
                        retry -= 1
                    else:
                        print('->访问 %s 失败' % url)
                        break
    elif use_agent == 1:
        html = get_html(url)
        if html != 0:
            p = pq(html)
    return p


# 数据库操作
def operate_mysql(info=0, operation='insert'):
    # 打开数据库连接
    db = pymysql.connect(host='192.168.1.203', port=3306, user='root',
                         passwd='Zkhc,.2017', db='znkf_new', charset='utf8')
    cursor = db.cursor()
    if operation == 'insert':
        if info == 0:
            return 0
        try:
            effect_row = cursor.executemany('INSERT INTO sys_hospital\
                              (province,city,region, name, address, grade,phone,email,operation)\
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                            [(h_i.province, h_i.city, h_i.area, h_i.name, h_i.address, h_i.grade,
                                              h_i.phone, h_i.email, h_i.operation) for h_i in info])
            print("  完成数 : %s " % effect_row)
            print('-----------------------------------------')
            db.commit()
        except Exception as e:
            print('%s' % e)
            print('->出错 回滚')
            print('-----------------------------------------')
            db.rollback()
        finally:
            db.close()
    elif operation == 'select':
        try:
            cursor.execute('SELECT DISTINCT city FROM sys_hospital')  # 执行sql语句
            results = cursor.fetchall()  # 获取查询的所有记录
            city_list = []
            # 遍历结果
            for row in results:
                city_list.append(row[0])
            return city_list
        except Exception as e:
            raise e
        finally:
            db.close()


# 省份页面处理
def solve_province(url, use_agent=0, delayed=3):
    base_prefix = 'http://www.a-hospital.com'
    country = get_pq_with_url(url, use_agent, delayed)
    if country == 0:
        print('->获取全国列表失败')
        return 0
    print('  获取全国列表成功')
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


# 城市页面处理
def solve_city(province, city, base_url, test_print=0, use_agent=0, delayed=3):
    revoke_field = ['医院网站', '医院地址', '联系电话', '医院等级', '经营方式', '电子邮箱', '重点科室', '传真号码']
    p = get_pq_with_url(base_url, use_agent, delayed)
    if p == 0:
        print('->获取%s失败' % city)
        return 0
    print('  获取%s成功' % city)
    p_t = 0
    area_url = {}
    if province[-1:] == '省' or province[-3:] == '自治区':
        for p_i in p('ul').eq(0).children().items():
            if p_i.text() == '三甲医院':
                break
            link = p_i.children().attr('href')
            if link is not None:
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
        area_h = solve_area(area_url[a], province, city, a, use_agent, delayed)
        if area_h == 0:
            continue
        if len(area_h) == 0:
            print('->解析%s返回数为0' % a)
            continue
        hospital_info += area_h
    hospital_name = [i.name for i in hospital_info]
    t = p('ul').items()
    for h_i in t:  # ->ul
        for j in h_i.children().items():  # ->li
            hospital = 0
            for k in j.children().items():  # ->b,ul
                if hospital == 0:
                    if len(k('b')) == 0:
                        break
                    elif k.text() in revoke_field:
                        break
                    else:
                        if k.text() not in hospital_name:
                            hospital = Hospital(k.text(), province, city, city)
                else:
                    if hospital != 0:  # ->b
                        for x in k.children().items():  # ->li
                            hospital.insert_info(x.text())
                        hospital_info.append(hospital)
                        hospital = 0
    if test_print == 1:
        # 打印
        print('-----------------------------------------')
        print('  获取%s %s %d家医院成功' % (province, city, len(hospital_info)))
    return hospital_info


# 区域页面处理
def solve_area(url, province, city, area, use_agent=0, delayed=3):
    revoke_field = ['医院网站', '医院地址', '联系电话', '医院等级', '经营方式', '电子邮箱', '重点科室', '传真号码']
    d = get_pq_with_url(url, use_agent, delayed)
    if d == 0:
        print('->获取%s失败' % area)
        return 0
    print('  获取%s成功' % area)
    t = d('ul').items()
    area_hospital_list = []
    for h_i in t:  # ->ul
        for j in h_i.children().items():  # ->li
            hospital = 0
            for k in j.children().items():  # ->b,ul
                if hospital == 0:
                    if len(k('b')) == 0:
                        break
                    elif k.text() in revoke_field:
                        break
                    else:
                        hospital = Hospital(k.text(), province, city, area)
                else:
                    if hospital != 0:  # ->b
                        for x in k.children().items():  # ->li
                            hospital.insert_info(x.text())
                        area_hospital_list.append(hospital)
                        hospital = 0
    return area_hospital_list


def main(url):
    use_agent = 1
    print("Start : %s" % time.ctime())
    city_info_dict = solve_province(url, use_agent=use_agent)
    if city_info_dict == 0:
        exit(1)
    # 查询数据库中已包含的城市，作为剔除列表
    c_list = operate_mysql(operation='select')
    for i in city_info_dict:
        city_info = city_info_dict[i]
        print('  解析 %s  %s' % (city_info[0], i))
        if i in c_list:
            print('->已存入数据库')
            continue
        hospital_info_list = solve_city(city_info[0], i, city_info[1], 1, use_agent=use_agent)
        if hospital_info_list != 0:
            operate_mysql(hospital_info_list, operation='insert')
    print("End : %s" % time.ctime())


if __name__ == '__main__':
    country_url = 'http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'
    main(country_url)
    # h_info = solve_city('广东省', '东莞市',
    #                     'http://www.a-hospital.com/w/%E8%8B%8F%E5%B7%9E%E5%B8%82%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8',
    #                     1, use_agent=1)
    # h_info = solve_area('', '广东省', '东莞市', 'test', 1)
    # if h_info != 0:
    #     insert_mysql(h_info)
