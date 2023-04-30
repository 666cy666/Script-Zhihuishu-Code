import requests
import urllib.parse
from lxml import etree
import re
from ConnectAnswer import *

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}

class CrawlAnswer(object):
    #手动爬取网站地址
    # hand_url = "https://www.3gmfw.cn/article/html2/2020/05/10/525864.html"
    hand_url = ""
    def __init__(self,name):
        # self.redis = dbHandle()
        self.name = name
    def get_content(url):
        requests = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(requests)
        content = response.read().decode('gb18030')
        tree = etree.HTML(content)
        return tree
    def search_url(self):
        name = "《" + self.name + "》" + "/"
        name = urllib.parse.quote(name.encode('utf-8'))
        url = "https://www.3gmfw.cn/so/" + name
        print(url)
        tree = CrawlAnswer.get_content(url)
        res = 'https://www.3gmfw.cn' + tree.xpath('/html/body/div[1]/div/div/div[4]/div/div[1]/p[1]/strong/a/@href')[0]
        print(res)
        return res
    def search_page(self):
        url = CrawlAnswer.hand_url
        if(url == ""):
            print("正在自动爬取答案")
            url = self.search_url()
        print("爬取的答案地址首页:")
        print(url)
        urllist = []
        preurl = url[:url.rfind('/') + 1]
        urllist.append(url)
        requests = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(requests)
        content = response.read().decode('gb18030')
        tree = etree.HTML(content)
        texts = tree.xpath('/html/body/div[1]/div/div/div[3]/div[2]/div/nav/ul/a')
        # print(texts)
        for text in texts[1:len(texts) - 1]:
            sufurl = text.get('href')
            sufurl = preurl + sufurl
            urllist.append(sufurl)
        print("答案网址:")
        for i in urllist:
            print(i)
        return urllist

    def gettexts(self):
        urllist = self.search_page()
        # print(urllist)
        texts = []
        for (index, url) in enumerate(urllist):
            response = requests.get(url=url, headers=headers)
            html = response.text
            html = html.encode('iso-8859-1').decode('gbk')
            # 将HTML文本转换为XML对象
            xml = etree.HTML(html)
            text = xml.xpath('.//div[@class="content is-normal"]/text()')
            # def contains_chinese(text):
            #     print(text)
            #     """判断字符串是否包含汉字"""
            #     count = 0
            #     pattern = re.compile(r'[\u4e00-\u9fa5]')
            #     for s in text:
            #         match = pattern.search(s)
            #         if match is not None:
            #             count = count + 1
            #     print("count : "+str(count) + " length : "+ str(len(text)))
            #     if(count >= len(text)/2):
            #         return True
            #     return False
            # if(not contains_chinese(text)):
            #     text = xml.xpath('/html/body/div[1]/div/div/div[3]/div[2]/div//p//text()')
            # print(text)
            texts = texts + text
            text = xml.xpath('/html/body/div[1]/div/div/div[3]/div[2]/div//p//text()')
            texts = texts +text
        filtered_lst = [s.strip() for s in texts if s.strip()]
        # print(filtered_lst)
        return filtered_lst
    def getanswerlist(self):
        texts = self.gettexts()
        # print(texts)
        chapter = "绪论"
        self_answer = {
            "title": "",
            "answer": "",
            "chapter": chapter
        }
        choose = {}
        answerlist = []
        # 题目下标
        title_num = 1
        # 章节下标
        chapter_num = 0
        for text in texts:
            # 去除空格
            text = text.strip()
            # print(text)
            # 答案
            if ("答案:" in text or "答案：" in text):
                # print(text)
                text = text[3:]
                text = text.strip()
                if ('A' in text or 'B' in text or 'C' in text or 'D' in text or 'E' in text):
                    newstr = ""
                    if (len(text) > 1 and len(text) != len(choose)):
                        for i in text:
                            try:
                                newstr += choose[i] + ","
                            except Exception:
                                pass
                        text = newstr
                self_answer["answer"] = text
                # print(self_answer)
                answerlist.append(self_answer)
                self_answer = {
                    "title": "",
                    "answer": "",
                    "chapter": chapter
                }
                choose = {}
            elif ("第" in text and "章" in text):
                chapter_num = chapter_num + 1
                title_num = 1
                chapter = "第"+self.num_to_chinese(chapter_num)+"章"
                self_answer = {
                    "title": "",
                    "answer": "",
                    "chapter": chapter
                }
            # 答案标题
            elif (text[0].isdecimal()):
                # print("标题 : "+text)
                num_regex = re.compile(r'^(\d+)')
                # 使用正则表达式提取数字
                match1 = num_regex.match(text)
                title_num_current = match1.group(1)
                if(int(title_num_current) < int(title_num)):
                    chapter_num = chapter_num+1
                    chapter = "第" + self.num_to_chinese(chapter_num) + "章"
                    print("当前爬取答案章节号有误，已自动修正")
                    print("可能有误章节号 : " + chapter)
                    self_answer = {
                        "title": "",
                        "answer": "",
                        "chapter": chapter
                    }
                    title_num = int(title_num_current)
                title_num = title_num + 1
                self_answer["title"] = text[2::]
            # 答案选项
            elif ("." in text or ":" in text or (
                    ("A、" in text) or ("E、" in text) or ("B、" in text) or ("C、" in text) or ("D、" in text))):
                # print("答案选项")
                if ("." in text):
                    parts = text.split(".")
                elif (":" in text):
                    parts = text.split(":")
                else:
                    parts = text.split("、")
                choose[parts[0]] = parts[1]
                # print(choose)
        return answerlist

    def num_to_chinese(self,num):
        chinese_dict = {
            0: '零', 1: '一', 2: '二', 3: '三', 4: '四',
            5: '五', 6: '六', 7: '七', 8: '八', 9: '九',
            10: '十', 11: '十一', 12: '十二', 13: '十三', 14: '十四',
            15: '十五', 16: '十六', 17: '十七', 18: '十八', 19: '十九',
            20: '二十', 21: '二十一', 22: '二十二', 23: '二十三', 24: '二十四',
            25: '二十五', 26: '二十六', 27: '二十七', 28: '二十八', 29: '二十九',
        }
        num = int(num)
        return chinese_dict[num]


    def get_all_list(self):
        name = ["第一章","第二章","第三章","第四章","第五章"]
        for i in name:
            self.get_answerlist_by_name(i)
# if __name__ == '__main__':
    # answer = CrawlAnswer("国家安全环境强化版（北京大学）")
    # answer = CrawlAnswer("创新思维训练")
    # answer = CrawlAnswer("创新思维及方法")
    # answer = CrawlAnswer("构美空间形态设计")
    # answer = CrawlAnswer("解码国家安全（国际关系学院）")
    # answer = CrawlAnswer("创新设计前沿")
    # answerlist = answer.getanswerlist()
    # for i in answerlist:
    #     print(i)
    # AnswerDb = Answer("国家安全环境强化版（北京大学）")
    # for answer in answerlist:
    #     AnswerDb.add_item(answer)
    # answers = AnswerDb.find_All("第一章")
    # for i in answers:
    #     print(i)
        # CourseDb.add_item(item=answer)
    # s = "第13章章节测试"
    # CourseDb = Course("test_guojiaanquan")
    # for answer in answerlist:
    #     CourseDb.add_item(item=answer)
    # answers = CourseDb.find_All("第四章")
    # for i in answers:
    #     print(i)
    # print(match.group())
    # for i in answerlist:
    #     print(i)
    # s = "第一章测试"
    # chapter_text = s.replace("测试", "")
    # print(chapter_text)
    # print(answer.getanswerlist())
    # answer.set_redis()
    # print(answer.get_answerlist_by_name("第四章"))
    # answer.get_all_list()