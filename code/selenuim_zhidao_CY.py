import cv2
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tkinter import messagebox

import requests
from lxml import etree

import threading
from time import sleep

# from ConnectMysql import *
from ConnectCourse import *
from ConnectAnswer import *
from getAnswer import *

# 多线程global list
videolist=[]
class LazyChangeWorld():
    userphone = None
    userpassword = None
    def __init__(self,userphone,userpassword):
        self.userpassword = userpassword
        self.userphone = userphone
# userphone = "15688225601"
# userpassword =  "QAZpl,1387399982"
    def getimg(self,url, name):
        content = requests.get(url=url, headers=headers).content
        print(name+"正在打印")
        with open(name, 'wb') as fp:
            fp.write(content)
        print("打印成功")
    def getidentify_x(self,bgimg_name,brokenimg_name):
        bg_img = cv2.imread(bgimg_name)  # 背景图片
        tp_img = cv2.imread(brokenimg_name)  # 缺口图片
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        cv2.imwrite("./img/black_bgimg.jpg", bg_pic)
        cv2.imwrite("./img/black_tpimg.jpg", tp_pic)
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
        X = max_loc[0]
        th, tw = tp_pic.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite('./img/out.jpg', bg_img)  # 保存在本地
        return X
    def login_frame(self,driver,action):
        folder = "./img"
        if not os.path.exists(folder):  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(folder)
        driver.get('https://onlineweb.zhihuishu.com/onlinestuh5')
        sleep(1)
        username = driver.find_element(By.ID, 'lUsername')
        # username.send_keys("15688225601")
        username.send_keys(self.userphone)
        sleep(1)
        password = driver.find_element(By.ID, 'lPassword')
        # password.send_keys("QAZpl,1387399982")
        password.send_keys(self.userpassword)
        sleep(1)
        login = driver.find_element(By.CLASS_NAME, "wall-sub-btn")
        login.click()
        sleep(2)
        bgimg_src = driver.find_element(By.XPATH,"/html/body/div[29]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]").get_attribute("src")
        brokenimg_src = driver.find_element(By.XPATH, "/html/body/div[29]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[2]").get_attribute("src")
        bgimg_name = "./img/bgimg_src.jpg"
        brokenimg_name = "./img/brokenimg_src.jpg"
        self.getimg(bgimg_src, bgimg_name)
        self.getimg(brokenimg_src, brokenimg_name)
        sleep(1)
        move_x = self.getidentify_x(bgimg_name, brokenimg_name)
        print("验证码拖动的距离:" + str(move_x) + "px")
        # 选择拖动滑块的节点
        drag_element = driver.find_element(By.CLASS_NAME, 'yidun_slider.yidun_slider--hover')
        action.click_and_hold(drag_element)
        # # 第二步：相对鼠标当前位置进行移动
        action.move_by_offset(move_x + 10, 0)
        # # 第三步：释放鼠标
        action.release()
        # # 执行动作
        action.perform()
        sleep(2)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='sharingClassed']/div[2]/ul/div/dl/dt/div[1]/div[1]")))
        # course_target = driver.find_element(By.XPATH, "//*[@id='sharingClassed']/div[2]/ul/div/dl/dt/div[1]/div[1]")
        # course_target.click()
        # sleep(4)
    def check_test_or_over(self,driver):
        isvideo_over = False
        currentTime = ""
        duration = ""
        t = "-1"
        videoArea = driver.find_element(By.CLASS_NAME, "videoArea")
        # 总时长
        duration = driver.find_element(By.CLASS_NAME, "duration").text
        while(not isvideo_over):
            # 当前时长
            currentTime = driver.find_element(By.CLASS_NAME, "currentTime").text
            if(t == currentTime):
                #开始答题
                self.play_action(driver)
                # 开始播放
                videoArea.click()
                print("答题结束，播放视频")
            # 让视频下方的进度条一直出现
            js = "document.getElementsByClassName('controlsBar')[0].style.display='block'"
            driver.execute_script(js)
            sleep(0.5)
            t = currentTime
            print("t : " + t + "  duration : " + duration)
            box_right = driver.find_element(By.CLASS_NAME,"box-right")
            ActionChains(driver).move_to_element(box_right)
            # 检测间隔时间
            sleep(5)
            driver.execute_script(js)
            if (currentTime >= duration):
                print("播放完毕")
                isvideo_over = True
    def playvideo(self,driver):
        # 先执行倍速
        js = "document.getElementsByClassName('controlsBar')[0].style.display='block'"
        driver.execute_script(js)
        sleep(0.5)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "speedBox")))
        speedBox = driver.find_element(By.CLASS_NAME, "speedBox")
        speedBox.click()
        driver.execute_script(js)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "speedTab.speedTab15")))
        speed = driver.find_element(By.CLASS_NAME, "speedTab.speedTab15")
        speed.click()
        # 再点击播放
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "videoArea")))
        videoArea = driver.find_element(By.CLASS_NAME, "videoArea")
        videoArea.click()
        sleep(1)
        # 进入播放系统
        self.check_test_or_over(driver)

    def check_iselement_inframe(self,driver,by,path):
        try:
            sleep(1)
            element = driver.find_element(by,path)
            print("查找到当前元素")
            return True
        except :
            print("没有当前元素")
            return False
    def checkchlidren_iselement_inframe(self,driver,element,by,path):
        try:
            sleep(1)
            newelement = element.find_element(By.CSS_SELECTOR,path)
            # print("查找到当前元素")
            return True
        except :
            return False

    # 开始答题
    def play_action(self,driver):
        # 开始答题
        right_list = driver.find_elements(By.CLASS_NAME, "topic-item")
        print("开始答题")
        try:
            for i in right_list:
                right_class = "iconfont.iconzhengque1"
                print("查找正确标签")
                if (self.check_iselement_inframe(driver,By.CLASS_NAME,right_class)):
                    print("当前答题正确")
                    print("答题结束")
                    break
                error_class = 'iconfont.iconcuowu1'
                print("查找错误标签")
                if(self.check_iselement_inframe(driver,By.CLASS_NAME,error_class)):
                    print("当前答题错误")
                i.click()
                sleep(2)
        except Exception:
            pass
        # 答题结束,取消答题
        print("答题结束")
        sleep(1)
        # WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")))
        try:
            cancle_test = driver.find_element(By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")
            cancle_test.click()
            sleep(1)
        except Exception:
            pass
    # 视频页面跳转初始化操作
    def video_herf_init(self,driver):
        # 检测是否超过时间
        if(self.check_iselement_inframe(driver,By.XPATH,'//*[@id="app"]/div/div[3]/div/div[3]/span/button')):
            overtime = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/div/div[3]/span/button')
            try:
                overtime.click()
            except Exception:
                pass
        # 检验刚进页面是否跳转答题
        if (self.check_iselement_inframe(driver, By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")):
            self.play_action(driver)
        # 取消广告界面
        sleep(2)
        if(self.check_iselement_inframe(driver,By.CLASS_NAME,"iconfont.iconguanbi")):
            # 这里必须抛出异常，经过检验，广告弹窗元素一直处于界面中，
            # 只不过被display:none隐藏起来，若不弹出，能查找到，但不能点击则会报错
            try:
                cancel_target = driver.find_element(By.CLASS_NAME, "iconfont.iconguanbi")
                sleep(0.5)
                print("广告")
                cancel_target.click()
                sleep(0.5)
            except Exception:
                pass
    # 多线程爬取章节名称
    def seprateNum(self,N, threadcount):
        # 对整个数字空间N进行分段CPU_COUNT
        selist = []
        n = int(N / threadcount) + 1;
        for i in range(threadcount - 1):
            right = N
            N = N - n
            if (N < 0):
                N = 0
            left = N
            s = (left, right)
            selist.append(s)
        right = N
        left = 0
        s = (left, right)
        selist.append(s)
        # print(selist)
        return selist
    # 添加章节名称至User.db
    def additem_tosql(self,driver,MysqlDb,percent_elements,numlist):
        t = numlist[0]
        for percent_element in percent_elements :
            video = {}
            video_text_xpath = percent_element.find_element(By.CLASS_NAME,'catalogue_title')
            # 打印当前元素名称
            video_text = video_text_xpath.text
            # print(video_text)
            global videolist
            if(self.checkchlidren_iselement_inframe(driver,percent_element,By.CSS_SELECTOR,"b.fl.time_icofinish")):
                video = {
                    'index':t,
                    'name':video_text,
                    'isStudies':1
                }
                videolist.append(video)
                # print(video_text_xpath.text+"已经观看完毕")
            else:
                video = {
                    'index': t,
                    'name':video_text,
                    'isStudies': 0
                }
                videolist.append(video)
                # print(video_text_xpath.text+"未观看完毕")
            # MysqlDb.add_item(index=t,item=video)
            print(video)
            t = t + 1

    # 添加答案至sqltie
    def addanswer_tosql(self,driver,MysqlDb,answerlist):
        for answer in answerlist:
            MysqlDb.add_item(item=answer)
    # 爬取章节名称
    def videolist_init(self,driver,MysqlDb):
        percent_elements = driver.find_elements(By.CLASS_NAME,'clearfix.video')
        n = len(percent_elements)
        print("n : "+str(n))
        threadcount = 10;
        numlist = self.seprateNum(n,threadcount)
        print(numlist)
        global videolist
        threads = []
        for i in numlist[0:len(numlist)]:
            print(i[0], i[1])
            split_elements = percent_elements[i[0]:i[1]]
            t = threading.Thread(target=self.additem_tosql, args=(driver,MysqlDb,split_elements,i,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        for video in videolist:
            MysqlDb.add_item(video)
        # video_list = MysqlDb.find_All();
        print("videolist")
        videolist = MysqlDb.find_All()
        print(videolist)
        return videolist

    def do_test_by_sqlite(self,driver,AnswerDb):
        print("开始做本章单元测试")
        sleep(1)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/h1')))
        answer_choose = {
            "A":0,
            "B":1,
            "C":2,
            "D":3,
            "E":4,
            "F":5,
            "G":6
        }
        chapter = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div/h1')
        chapter_text = chapter.text
        print("单元章节 : " + chapter_text)
        chapter_text = chapter_text.replace("测试","")
        # 总答案
        answers = AnswerDb.find_All(chapter_text)
        print(answers)
        # 总题数
        # WebDriverWait(driver, 10, 0.5).until(
        #     EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/ul/li[2]/span')))
        # requestions = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/ul/li[2]/span')
        # requestions = requestions.text
        # 页面中总选项父节点
        choose_targets_xpath = driver.find_elements(By.CLASS_NAME,'subject_node')
        # 页面中总题目类型节点
        subject_types = driver.find_elements(By.CLASS_NAME,"subject_type")
        for (index,answer) in enumerate(answers):
            check = False
            # 题目类型标签
            subject_type = subject_types[index].find_element(By.XPATH,'.//span[1]')
            type_text = subject_type.text
            print("type_text : "+type_text)
            choose_targets = choose_targets_xpath[index].find_elements(By.CLASS_NAME, "label.clearfix")
            # 多选题
            if ("多选" in type_text):
                print("进入多选")
                # 所有的选项
                print("答案为 : " + answer)
                # 如果答案是ABCD类型的选项直接点
                if ('A' in answer or 'B' in answer or 'C' in answer or 'D' in answer or 'E' in answer):
                    for i in answer:
                        choose_targets[answer_choose[i]].click()
                # 如若不是则遍历选项
                else:
                    for choose_target in choose_targets:
                        choose = choose_target.find_element(By.XPATH, ".//div[2]")
                        choose = choose.text
                        print("选项为 : " + choose_target.text)
                        if(choose in answer):
                            choose_target.click()
                            print("多选选中")
            # 单选题
            else:
                if ((len(answer) < 2) and ('A' in answer or 'B' in answer or 'C' in answer or 'D' in answer or 'E' in answer) ):
                    choose_targets[answer_choose[answer]].click()
                else:
                    for choose_target in choose_targets:
                        choose = choose_target.find_element(By.XPATH,".//div[2]")
                        choose = choose.text
                        print("选项为 : " + choose)
                        print("答案为 : " + answer)
                        if (choose in answer):
                            print("选中")
                            choose_target.click()
                            break
                        sleep(1)
            # 下一题的选项
            next_button = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[3]/button[2]')
            next_button.click()
            sleep(0.5)
        print(chapter.text+"已经做完")
        sleep(1)

    def do_test_by_redis(self,driver,Redis):
        sleep(1)
        answer_choose = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
            "E": 4,
            "F": 5,
            "G": 6
        }
        chapter = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/h1')
        # 总答案
        answers = Redis.get_answerlist_by_name(chapter.text[0:3])
        print(answers)
        # 总题数
        requestions = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/ul/li[2]/span')
        requestions = requestions.text
        print("总题数为 : " + str(requestions))
        if (int(requestions) != len(answers)):
            print("答案爬取错误，请联系管理员")
        choose_targets_xpath = driver.find_elements(By.CLASS_NAME, 'subject_node')
        subject_types = driver.find_elements(By.CLASS_NAME, "subject_type")
        print(subject_types)
        for (index, answer) in enumerate(answers):
            # 题目类型标签
            subject_type = subject_types[index].find_element(By.XPATH, './/span[1]')
            type_text = subject_type.text
            print("type_text : " + type_text)
            choose_targets = choose_targets_xpath[index].find_elements(By.CLASS_NAME, "label.clearfix")
            # 多选题
            if ("多选" in type_text):
                print("进入多选")
                # 所有的选项
                # 如果答案是ABCD类型的选项直接点
                if ('A' in answer or 'B' in answer or 'C' in answer or 'D' in answer or 'E' in answer):
                    for i in answer:
                        choose_targets[answer_choose[i]].click()
                # 如若不是则遍历选项
                else:
                    for choose_target in choose_targets:
                        choose = choose_target.text
                        print("选项为 : " + choose_target.text)
                        print("答案为 : " + answer)
                        if (choose in answer):
                            choose_target.click()
            # 单选题
            else:
                if ('A' in answer or 'B' in answer or 'C' in answer or 'D' in answer or 'E' in answer):
                    choose_targets[answer_choose[answer]].click()
                else:
                    for choose_target in choose_targets:
                        choose = choose_target.find_element(By.XPATH, ".//div[2]")
                        choose = choose.text
                        print("选项为 : " + choose)
                        print("答案为 : " + answer)
                        if (choose == answer):
                            print("选中")
                            choose_target.click()
                            break
                        sleep(1)
            # 下一题的选项
            next_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[3]/button[2]')
            next_button.click()
            sleep(1)
        print(chapter.text + "已经做完")
        sleep(2)

    def initmain(self,is_watch,is_dotest):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57'}
            s = Service('msedgedriver.exe')
            # 初始化driver
            driver = webdriver.Edge(service=s)
            # 初始化selenium行为
            action = ActionChains(driver)
            # 初始化mysql
            name = 'User_'+self.userphone
            CourseDb = Course(name)
            # 初始化videolist
            global videolist
            # 登录系统
            self.login_frame(driver, action)
            coursename_target = driver.find_element(By.XPATH, '//*[@id="sharingClassed"]/div[2]/ul/div/dl/dt/div[1]/div[1]')
            coursename = coursename_target.text
            coursename = coursename.replace('-', '')
            # print(coursename)
            AnswerDb = Answer(coursename)
            Redis = CrawlAnswer(coursename)
            coursename_target.click()
            sleep(2)
            # 打开视频页面的初始化
            self.video_herf_init(driver)
            # 本地数据
            # lessonlist = get_videolist(CourseDb)
            # print(videolist)
            if (is_watch):
                # 爬取数据的初始化,判断当前表是否有数据,若有则不爬取
                if (CourseDb.check_isdata()):
                    self.videolist_init(driver, CourseDb)
                else:
                    videolist = CourseDb.find_All()
                self.video_herf_init(driver)
                video_elements = driver.find_elements(By.CLASS_NAME, 'clearfix.video')
                print("总长度 : "+str(len(video_elements)))
                for (i,item) in enumerate(video_elements):
                    if (CourseDb.find_Byid(i)["isStudies"] == int(1)):
                        # print(CourseDb.find_Byid(i + 1))
                        print(str(i)+"号标题"+CourseDb.find_Byid(i)["name"] + "已经看过")
                        # sleep(1)
                        continue
                    # 点击当前需要看的界面
                    print("当前观看网课名称:"+CourseDb.find_Byid(i)["name"])
                    sleep(1)
                    # WebDriverWait(driver, 10, 0.5).until(item)
                    item.click()
                    sleep(0.5)
                    # 进入页面初始化
                    self.video_herf_init(driver)
                    # 可能刚进页面没跳转，关了广告才跳转
                    if (self.check_iselement_inframe(driver, By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")):
                        self.play_action(driver)
                    self.playvideo(driver)
                    # 结束播放,提交数据至数据库
                    CourseDb.updata_Byid(i)
                    sleep(1)
                messagebox.showinfo("已播放完毕")
            if (is_dotest):
                self.video_herf_init(driver)
                print("开始做测试")
                if(AnswerDb.check_isdata()):
                    answerlist = Redis.getanswerlist();
                    self.addanswer_tosql(driver, AnswerDb, answerlist)
                test_elements = driver.find_elements(By.CLASS_NAME, 'chapter-test')
                for test in test_elements:
                    test.click()
                    sleep(0.5)
                    if (self.check_iselement_inframe(driver, By.XPATH, '//*[@id="app"]/div/div[7]/div/div[3]/span/button[2]')):
                        print("当前测试已经做过")
                        cancle_test = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[7]/div/div[3]/span/button[2]')
                        cancle_test.click()
                        continue
                    sleep(2.5)
                    # 切换到第二个标签页
                    driver.switch_to.window(driver.window_handles[1])
                    print("切换至第二个标签页")
                    # 在第二个标签页中执行操作
                    # ...
                    self.do_test_by_sqlite(driver, AnswerDb)
                    # do_test_by_redis(driver,Redis)
                    # 切换回第一个标签页
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    print("切换回第一个标签页")
                messagebox.showinfo("已作答完毕")
        except Exception as e:
            messagebox.showerror("出现了一个未知的错误", "错误可能原因：\n"
                                           "1.当前edge浏览器驱动为112.0.1722.58(64位),请检查您的浏览器是否高于当前版本\n"
                                           "2.网速过慢，请检查是否挂载VPN，如是请关闭\n"
                                           "3.出现异地登录请求，请手动点击答案关闭，并重新点击运行\n"
                                           "4.该软件为全自动化运行，请不要在当前浏览器驱动下点击其他网页或者关闭该驱动\n"
                                           "5.未知的错误，请联系管理员或在当前github项目地址下留言\n"
                                           "解决方法:\n"
                                           "1.点击删除数据重新运行"
                                           "2.联系管理员QQ：1161864431或QQ：578009720\n")

# if __name__ == "__main__":
#     # userphone = "15688225601"
#     # userpassword =  "QAZpl,1387399982"
#     code =  LazyChangeWorld("15688225601","QAZpl,1387399982")
#     code.initmain(1,0)





