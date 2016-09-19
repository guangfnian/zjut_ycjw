import requests
from datetime import datetime
from bs4 import BeautifulSoup

urls = (
    'http://172.16.7.83/',
    'http://172.16.7.84/',
    'http://172.16.7.86/',
    'http://www.ycjw.zjut.edu.cn/',
    'http://172.16.7.77/',
)


class Ycjw(object):
    def __init__(self, name, pwd, u=0):
        self.name = name
        self.pwd = pwd
        self.url = urls[u]
        self.s = requests.Session()
        self.html = self.s.get(self.url)
        self.bs = BeautifulSoup(self.html.text, 'lxml')
        # 登录
        self.data = {
            'Cbo_LX': '学生'.encode('gb2312'),
            'Txt_UserName': name,
            'Txt_Password': pwd,
            'Img_DL.x': '14',
            'Img_DL.y': '4',
        }
        self.update_form()
        response = self.s.post(self.url + 'logon.aspx', data=self.data)
        if response.url != self.url+'/stdgl/stdgl_index.aspx':
            self.success = False
            print('登录失败')
        else:
            self.success = True
            self.html = self.s.get(self.url+'/stdgl/stdgl_index.aspx')
            self.bs = BeautifulSoup(self.html.text, 'lxml')

    def update_form(self): # 更新__VIEWSTATE等字段
        event_list = self.bs.findAll('input', {'type': 'hidden'})
        for event in event_list:
            self.data[event['name']] = event['value']

    def go_to_cxxt(self): # 前往查询系统
        self.data = {
            'Header1:TextBox1': '该功能主要是让学生修改自己的密码，以保证密码的安全性。'.encode('gb2312'),
        }
        self.update_form()
        self.data['__EVENTTARGET'] = 'LB_cxxt'
        self.html = self.s.post(self.url+'/stdgl/stdgl_index.aspx', data=self.data)
        self.bs = BeautifulSoup(self.html.text, 'lxml')

    def get_xq(self): # 返回当前学期
        today = datetime.today()
        year = today.date().year
        month = today.date().month
        x = 2 if 3 <= month < 9 else 1
        y = year if month >= 9 else year-1
        return str(y)+r'/'+str(y+1)+'('+str(x)+')'

    def get_grade(self, xq = None): # 获取成绩
        if xq is None:
            xq = self.get_xq()
        self.go_to_cxxt()
        self.data = {
            'Header1:Image1.x': '26',
            'Header1:Image1.y': '16',
            'Header1:TextBox1': '通过该项功能，学生可以查询到所有学期的成绩，包括等级考成绩。'.encode('gb2312'),
            'Header2:TextBox1': '使用该功能，您可以查询到某学期的个人课表。'.encode('gb2312'),
            'Header3:TextBox1': '通过该功能,可以查询到自己的培养计划!'.encode('gb2312'),
            'HEADER4:TextBox1': '通过该功能,可以查询到自己的考试安排!'.encode('gb2312'),
            'HEADER5:TextBox1': '通过该功能,可以查询到自己的符合毕业情况!'.encode('gb2312'),
        }
        self.update_form()

        self.s.post(self.url+'/stdgl/stdgl_index.aspx', data=self.data)

        self.html = self.s.get(self.url+'/stdgl/cxxt/cjcx/Cjcx_Xsgrcj.aspx')
        self.bs = BeautifulSoup(self.html.text, 'lxml')
        self.data = {
            '1': 'rbtnXq',
            'ddlXq': xq,
            'ddlKc': '＝所有课程＝'.encode('gb2312'),
            'Button1': '普通考试成绩查询'.encode('gb2312'),
        }
        self.update_form()
        self.html = self.s.post(self.url+'/stdgl/cxxt/cjcx/Cjcx_Xsgrcj.aspx', data=self.data)
        self.bs = BeautifulSoup(self.html.text, 'lxml')
        all_data = self.bs.findAll('font', {'color': '#000066', 'size': '2'})
        for i in range(len(all_data)):
            print(all_data[i].text, end=' ')
            if (i+1)%6 == 0:
                print('')

if __name__ == '__main__':
    for i in range(len(urls)):
        a = Ycjw('123456', '123456', i)
        if not a.success:
            continue
        a.get_grade()
        break
