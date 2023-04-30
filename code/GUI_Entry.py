"""测试Entry组件的基本用法，使用面向对象的方式"""
import os
import logging
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import sys
from tkinter import ttk
from selenuim_zhidao_CY import  *
import threading
from tkinter import filedialog

import re

import json

from ConnectCourse import *
from ConnectAnswer import *

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)      #super()代表的是父类的定义，而不是父类对象
        self.master=master
        self.userphone = ""
        self.userpassword = ""
        self.pack()
        self.createWidget()
        self.second_window = None
        self.code = None
    def open_child_window(self):
        try:
            self.userphone=self.entry01.get()
            self.userpassword=self.entry02.get()
            # 存储用户密码
            self.localstorage_user()
            messagebox.showinfo("登录页", "登录成功！")
            print("用户名:" + self.userphone)  # 将账户和密码打印到控制台
            print("密码:" + self.userpassword)
            self.code = LazyChangeWorld(self.userphone, self.userpassword)
            #子窗口建立
            self.master.withdraw()      #隐藏登录窗口
            if not self.second_window:
                # def on_closing():
                #     self.second_window.destroy()
                def on_closing():
                    if messagebox.askokcancel("退出", "确定退出嘛"):
                        root.destroy()
                self.second_window = TaskPage(self)
                self.second_window.protocol("WM_DELETE_WINDOW", on_closing)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def localstorage_user(self):
        if(self.userphone != "" and self.userpassword != ""):
            user_data = {
                "username":self.userphone,
                "password":self.userpassword,
            }
            # 打开文件，以覆写的方式写入JSON字符串
            with open('User_data.txt', 'w') as f:
                f.write(json.dumps(user_data))
    def get_user(self):
        filename = "User_data.txt"
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                print(f"File '{filename}' created successfully.")
        else:
            print(f"File '{filename}' already exists.")
        with open('User_data.txt', 'r') as f:
            user_data_json = f.read()
        if(user_data_json == None or user_data_json == ""):
            return
        else:
            # 将字符串转换为 Python 字典对象
            user_data = json.loads(user_data_json)
            print(user_data)
            self.userphone = user_data["username"]
            self.userpassword = user_data["password"]
    def createWidget(self):
        """创建登录界面的组件"""
        root.title("Lazy Change World V1.0.9")
        self.label01 = Label(self,text="用户名")
        self.label01.pack()
        #StringVar变量绑定到指定的组件
        #StringVar变量的值发生变化，组件内容也变化
        #组件内容发生变化，StringVar变量的值也发生变化。
        v1=StringVar()
        self.entry01=Entry(self,textvariable=v1)
        self.entry01.pack()

        # 初始化用户信息
        self.get_user()

        v1.set(self.userphone)
        # v1.set("18637220088")
        #创建密码框
        self.label02=Label(self,text="密码")
        self.label02.pack()
        v2 = StringVar()
        self.entry02 = Entry(self, textvariable=v2,show="*")#,show="*"
        self.entry02.pack()

        v2.set(self.userpassword)
        # v2.set("Xiandan*19780815")

        self.button = tk.Button(self.master, text="登录", command=self.open_child_window)
        self.button.pack()

class TaskPage(tk.Toplevel,threading.Thread):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.create_widgets()
        self.geometry("440x600+700+300")#设置窗口位置
    def create_widgets(self):
        # 创建一个标签用来显示任务的相关信息
        task_label = tk.Label(self, text="本软件获取答案指定网页:")
        task_label.place(x=30,y=7)

        # 创建一个下拉列表框，用来显示任务列表
        answer_html_text = StringVar()
        answer_html_text.set("https://www.3gmfw.cn/")
        self.answer_html = Entry(self, textvariable=answer_html_text)
        self.answer_html.place(width=150, height=20, x=180,y=7)

        task_label = tk.Label(self, text="answer_url:")
        task_label.place(x=30,y=45)

        v1=StringVar()
        self.url_content=Entry(self,textvariable=v1)
        self.url_content.place(width=180,height=20,x=150,y=45)
        self.url=self.url_content.get()

        # 创建运行按钮，运行任务
        run_button = tk.Button(self, text="运行", command=self.run_task)
        run_button.place(x=160,y=120)

        self.search_button = tk.Button(self)
        self.search_button["text"] = "手动爬取"
        # self.search_button["bg"]='cyan'
        self.search_button["command"] = self.crawl
        self.search_button.place(x=350, y=40)

        self.search_button = tk.Button(self)
        self.search_button["text"]="导出答案"
        # self.search_button["bg"]='cyan'
        self.search_button["command"]=self.search
        self.search_button.place(x=350,y=75)

        self.search_button = tk.Button(self)
        self.search_button["text"]="保存日志"
        # self.search_button["bg"]='cyan'
        self.search_button["command"]=self.log_to_file
        self.search_button.place(x=350,y=110)

        self.clear_button=tk.Button(self)
        self.clear_button["text"]="清除数据"
        # self.clear_button["bg"]='cyan'
        self.clear_button["command"]=self.clear_all
        self.clear_button.place(x=350,y=5)

        # 创建两个可勾选框
        self.option1 = tk.BooleanVar()
        self.checkbutton1 = tk.Checkbutton(self, text="是否观看网课", variable=self.option1)
        self.checkbutton1.place(x=75,y=75)

        self.option2 = tk.BooleanVar()
        self.checkbutton2 = tk.Checkbutton(self, text="是否答题", variable=self.option2)
        self.checkbutton2.place(x=250,y=75)

        # 创建一个控制台输出区域
        self.console_output = Console(self, height=30, width=60)     #设置console窗口大小
        self.console_output.place(x=5,y=175)

        self.back_button = tk.Button(self)
        self.back_button["text"] = "返回"
        self.back_button["command"] = self.go_back
        self.back_button.place(x=260,y=120)

        # 把标准输出流重新定向到界面上输出区域
        sys.stdout = self.console_output
    def log_to_file(self):
        filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
        if filename:
            # 配置logging模块，将日志输出到指定文件
            logging.basicConfig(filename=filename, level=logging.DEBUG)
            console_text = self.console_output.get('1.0', 'end-1c')
            logging.debug(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {console_text}')
            messagebox.showinfo(title="保存成功", message="日志已保存到文件中！")
    #清除按钮
    def clear_all(self):
        try:
            print("\n清楚数据")
            answerdb = Answer()
            coursedb = Course()
            answerdb.destroy()
            coursedb.destroy()
            messagebox.showinfo(title="销毁成功", message="数据库销毁成功，您可以重新登录爬取网课以重置数据库")
            print("\n清除数据成功")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    #导出答案
    def search(self):
        print("\n导出答案")
        try:
            if not os.path.exists("./Answer.db"):  # 判断是否存在文件夹如果不存在则创建为文件夹
                messagebox.showinfo(title="警告", message="未正确生成数据库文件，请正确爬取")
                return
            answerdb = Answer()
            coursedb = Course()
            answerdb.output()
            coursedb.output()
        except Exception as e:
            messagebox.showerror("Error", "excle表正在使用,请关闭后重新导出")
    #爬取答案
    def crawl(self):
        try:
            crawl_thread = threading.Thread(target=self.crawl_thread)
            crawl_thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def crawl_thread(self):
        try:
            CrawlAnswer.hand_url = self.url_content.get()
            print("Taskpageurl : " + CrawlAnswer.hand_url)
            # print("爬取答案")
            url = CrawlAnswer.hand_url
            print("pageurl : " + url)
            if (url.strip() == ""):
                messagebox.showinfo(title="爬取地址错误", message="爬取地址可能为空或者有误，请重新输入")
                return
            tree = CrawlAnswer.get_content(url=url)
            name = tree.xpath('/html/body/div[1]/div/div/div[3]/div[1]/div/h5/text()')[0].strip()
            print(name)
            pattern = r'《(.*?)》'
            matchs = re.findall(pattern, name)
            if matchs:
                name = matchs[0]
            else:
                messagebox.showinfo("非正常爬取中","您输入的地址为非正常爬取地址，请以\"智慧树知到《网课名称》\"搜索\n仍继续为您爬取")
            # name = name.replace("——", "")
            print(name)
            answer = CrawlAnswer(name)
            answerlist = answer.getanswerlist()
            answerdb = Answer(name)
            if(answerdb.check_isdata()):
                for answer in answerlist:
                    answerdb.add_item(item=answer)
            print(".............\n.............\n爬取答案完毕!!!\n.............\n.............")
        except Exception as e:
            messagebox.showerror("Error", "请输入正确的答案首地址")
    # 将标准输出流重新定向回控制台，用于多次登录后显示子窗口,防止多次打开子窗口时输出信息混乱
    def destroy(self):
        sys.stdout = sys.__stdout__
        super().destroy()
        self.master.second_window = None #下次打开窗口可以创建新的窗口
    def go_back(self):
        self.destroy()
        self._root().deiconify()  # 显示登录窗口(根窗口)
    def run_task(self):
        option1_checked = self.option1.get()    #<是否看网课>的布尔值
        option2_checked = self.option2.get()    #<是否答题>的布尔值
        try:
            t=threading.Thread(target=self.master.code.initmain,args=(option1_checked,option2_checked))
            t.start()
        except Exception as e:
            messagebox.showerror("出现了一个未知的错误", "错误可能原因：\n"
                                               "1.当前edge浏览器驱动为112.0.1722.58(64位),请检查您的浏览器是否高于当前版本\n"
                                               "2.网速过慢，请检查是否挂载VPN，如是请关闭\n"
                                               "3.出现异地登录请求，请手动点击答案关闭，并重新点击运行\n"
                                               "4.该软件为全自动化运行，请不要在当前浏览器驱动下点击其他网页或者关闭该驱动\n"
                                               "5.未知的错误，请联系管理员或在当前github项目地址下留言")
        print(f"是否观看网课：{option1_checked}")   #打印出次框是否已被勾选的布尔值
        print(f"是否答题：{option2_checked}")


class Console(tk.Text):
    def __init__(self, *args, **kwargs):#用来接收任意数量的参数
        super().__init__(*args, **kwargs)
        self.configure(state='disabled')
    def write(self, msg):
        self.configure(state='normal')
        self.insert(tk.END, msg)
        self.see(tk.END)
        self.configure(state='disabled')
if __name__=='__main__':

    root = tk.Tk()
    root.geometry("350x200+800+400")
    app=Application(master=root)
    root.mainloop()     #进入等待与处理窗口事件