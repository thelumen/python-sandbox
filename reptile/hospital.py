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