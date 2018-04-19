#!coding:utf-8
import csv
import os
import copy


def makecsv(filepath):
    with open(filepath, 'r') as cvsf:
        people = {}
        count = 0
        men = 0
        women = 0
        for line in cvsf.readlines():
            info_group = line.split(',')
            name = info_group[1]
            if name[-1:] == '1':
                name = name[:-1]
            if name not in people:
                people[name] = []
            people[name].append(info_group)
            count += 1
        for man in people:
            people[man] = sorted(people[man], key=lambda s: s[0])
            if people[man][0][3] == '男':
                men += 1
            else:
                women += 1
    path, filename = os.path.split(filepath)
    filename = filename[:-4] + '_re.csv'
    path = os.path.join(path, filename)
    with open(path, 'w', newline='') as resultfile:
        writer = csv.writer(resultfile, dialect='excel', delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['姓名', '时间', '阶段', '年龄', '性别', '身高', '体重', '联系方式', '病因'])
        names = people.keys()
        for aman in names:
            if len(people[aman]) > 1:
                agroupinfo = people[aman]
                name = agroupinfo[0][1]
                for i in range(len(agroupinfo)):
                    agroupinfo[i][1] = name + str(i)
            first = True
            for ainfo in people[aman]:
                line = []
                if first:
                    line.append(aman)
                else:
                    line.append('')
                for anum in range(len(ainfo)):
                    astr = ainfo[anum]
                    if anum == 7:
                        astr = astr[:-1]
                    line.append(astr)
                first = False
                writer.writerow(line)
        writer.writerow([])
        statistics_people = '男：' + str(men) + '人 女：' + str(women) + '人'
        statistics_man = '总计：' + str(len(people)) + '人'
        statistics_info = '总计：' + str(count) + '条记录'
        writer.writerow([statistics_people])
        writer.writerow([statistics_man])
        writer.writerow([statistics_info])
    return people


b = makecsv('/home/ri/user/Tem/people.csv')
