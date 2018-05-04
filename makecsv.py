#!coding:utf-8
import csv
import os
import re


def makecsv(filepath):
    with open(filepath, 'r') as cvsf:
        people = {}
        count = 0
        men = 0
        women = 0
        for line in cvsf.readlines():
            info_group = line.rstrip().split(',')
            name = info_group[1]
            if re.match(r'\d', name[-1:]):
                name = name[:-1]
            if name not in people:
                people[name] = []
            info_group[0] = info_group[0][:5]
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
        writer.writerow(['时间', '姓名', '年龄', '性别', '身高', '体重', '联系方式', '病因', '阶段'])
        names = people.keys()
        for man in names:
            agroupinfo = people[man]
            group_size = len(agroupinfo)
            if group_size == 1:
                agroupinfo[0].append(0)
            else:
                num = 0
                agroupinfo[0].append(0)
                c = False
                for i in range(1, group_size):
                    if agroupinfo[i - 1][0] == agroupinfo[i][0]:
                        agroupinfo[i].append(num + 1)
                        num += 1
                        c = True
                    else:
                        if c:
                            agroupinfo[i].append(num + 1)
                            num += 1
                            c = False
                        else:
                            agroupinfo[i].append(num + 2)
                            num += 2
            # first = True
            # for ainfo in people[man]:
            #     line = []
            #     if first:
            #         line.append(man)
            #     else:
            #         line.append('')
            #     for anum in range(len(ainfo)):
            #         astr = ainfo[anum]
            #         if anum == 7:
            #             astr = astr[:-1]
            #         line.append(astr)
            #     first = False
            #     writer.writerow(line)
            for ainfo in people[man]:
                writer.writerow(ainfo)
        writer.writerow([])
        statistics_people = '男：' + str(men) + '人 女：' + str(women) + '人'
        statistics_man = '总计：' + str(len(people)) + '人'
        statistics_info = '总计：' + str(count) + '条记录'
        writer.writerow([statistics_people])
        writer.writerow([statistics_man])
        writer.writerow([statistics_info])
    return people


if __name__ == '__main__':
    b = makecsv('/home/ri/user/Tem/people.csv')
