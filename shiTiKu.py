import requests
import json
import bs4
import re
import xlrd
import sys
import time

path = sys.path[0]
count = 0

class sheet():
    singleChioceDict = dict()
    judgeDict = dict()

    def __init__(self, filenames):
        for filename in filenames:
            workbook = xlrd.open_workbook("/".join([path, filename]))
            singleChioce = workbook.sheet_by_name("单选题")
            judge = workbook.sheet_by_name("判断题")

            for i in range(singleChioce.nrows):
                self.singleChioceDict[singleChioce.row(i)[0].value] = singleChioce.row(i)[-1].value
            for i in range(judge.nrows):
                self.judgeDict[judge.row(i)[0].value] = judge.row(i)[-1].value

    def getAnswer(self, question, qesType):
        if qesType == 1:
            return self.singleChioceDict[question]
        if qesType == 2:
            return self.judgeDict[question]


def loadCookie():
    cookies = open("/".join([path, "cookie.json"]), 'r').read()
    cookies = json.loads(cookies)
    for cookie in cookies:
        sess.cookies.set(cookie["name"], cookie["value"])

    sess.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
    sess.headers["X-Requested-With"] = "XMLHttpRequest"

def getCourses():
    res = sess.get("http://tkkc.hfut.edu.cn/student/index.do")
    html = bs4.BeautifulSoup(res.text, "lxml")
    courses = html.find(name="div", attrs={"class": "listcourse"}).find_all(name="li")
    courseLinks = list()
    for course in courses:
        value = course.get("onclick")
        if (value):
            courseLinks.append("http://tkkc.hfut.edu.cn" + re.findall(r"\'(.*)\'", value)[0])
    return courseLinks


def getTaskLinks(courseLinks):
    tasksLinks = list()
    for courseLink in courseLinks:
        res = sess.get(courseLink)
        html = bs4.BeautifulSoup(res.text, "lxml")
        raw = html.find(name="div", attrs={"class": "lf"})
        link = raw.find(name="a").get("href")
        name = raw.find(name="span", attrs={"class": "courseName"}).text
        tasksLinks.append(dict({"name": name,"link": "http://tkkc.hfut.edu.cn" + link}))
    return tasksLinks


def getTestLinks(tasksLinks):
    testLinks = list()
    for tasksLink in tasksLinks:
        res = sess.get(tasksLink["link"])
        html = bs4.BeautifulSoup(res.text, "lxml")
        table = html.find_all(name="tr", attrs={"class": "a"})
        for raw in table:
            if str(raw).find("作业") != -1:
                testLinks.append(dict({"name": tasksLink["name"], "link": "http://tkkc.hfut.edu.cn" + raw.find(name="a").get("href")}))
    return testLinks


def answerTheQuestion(question, examReplyId, examId, teachingTaskId):
    global count

    postData = {
        "method": "getExerciseInfo",
        "examStudentExerciseId": question["examStudentExerciseId"],
        "exerciseId": question["exerciseId"],
    }
    res = sess.post("http://tkkc.hfut.edu.cn/student/exam/manageExam.do", postData)
    answer = st.getAnswer(res.json()["title"].replace("&nbsp;", ""), res.json()["type"])

    postData = {
        "examReplyId": examReplyId,
        "examId": examId,
        "teachingTaskId": teachingTaskId,
        "examStudentExerciseId": question["examStudentExerciseId"],
        "exerciseId": question["exerciseId"],
    }

    if res.json()["type"] == 1: # 1 是单选题, 2 是判断
        postData["DXanswer"] = answer
    else:
        if answer == "正确":
            answer = "A"
        if answer == "错误":
            answer = "B"
        postData["PDanswer"] = answer

    success = False
    while not success:
        try:
            res = sess.post("http://tkkc.hfut.edu.cn/student/exam/manageExam.do?method=saveAnswer", postData, timeout=5)
            success = True
        except requests.exceptions.Timeout:
            print("Time out, retrying.")
            pass

    print(res.text, count, answer)
    time.sleep(0.5) # Don't abuse the poor server :)
    count += 1


def getQuestions(testLinks):
    for testLink in testLinks:
        res = sess.get(testLink["link"])
        html = bs4.BeautifulSoup(res.text, "lxml")

        examReplyId = html.find(name="input", attrs={"name": "examReplyId"}).get("value")
        examId = html.find(name="input", attrs={"name": "examId"}).get("value")
        teachingTaskId = html.find(name="input", attrs={"name": "teachingTaskId"}).get("value")

        questionsJson = re.findall(r"eval\((\[[\s\S]+?\])\)", res.text)[0]
        questions = json.loads(questionsJson)
        for question in questions:
            answerTheQuestion(question, examReplyId, examId, teachingTaskId)


st = sheet(["1.xls", "2.xls"])
print("Sheets loaded.")
sess = requests.session()
loadCookie()
getQuestions(getTestLinks(getTaskLinks(getCourses())))
