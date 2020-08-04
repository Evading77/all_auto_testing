import json, os, threading, traceback
import time


from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction

from frameworkutils import logger
from keywords.commenkeys import sysKey


class App:
    """
    app自动化关键字库

    """

    def __init__(self, writer):
        """
        初始化实例变量
        """
        self.writer = writer
        self.row = 0
        # 保存appium和APP的配置
        self.conf = {}
        # APP运行驱动
        self.driver = None

    def startappium(self, port=''):
        if port == '':
            port = '4723'

        self.conf['port'] = port

        def runappium(port='4723'):
            """

            :return:
            """
            cmd = r"node E:\Appium\resources\app\node_modules\appium\build\lib\main.js -p " + port
            # 阻塞
            os.popen(cmd).read()

        # 创建一个子线程，叫th
        th = threading.Thread(target=runappium, args=(port,))
        # 启动线程
        th.start()
        time.sleep(5)
        self.__write_excel(True, "等待成功")

    def stopappium(self, port=''):
        try:
            if port == '':
                port = '4723'

            pid = os.popen('netstat -aon | findstr LISTENING | findstr ' + port).read()
            pid = pid.split(' ')
            if len(pid) < 2:
                return
            else:
                pid = pid[len(pid) - 1]

            res = os.popen('taskkill /F /PID ' + pid).read()
            logger.info(res)
        except Exception as e:
            pass

        self.__write_excel(True, "关闭appium成功")

    def startapp(self, conf):
        try:
            conf = conf.replace(r'\n', '')
            conf = eval(conf)
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            self.writer.save_close()
            self.stopappium(self.conf['port'])
            exit(-1)
            return False

        try:
            self.conf.update(conf)
            self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", conf)
            self.driver.implicitly_wait(20)
            self.__write_excel(True, "等待成功")
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            self.writer.save_close()
            self.stopappium(self.conf['port'])
            exit(-1)
            return False

    def sleep(self, t):
        """
        固定等待
        :param t: 时间，单位s
        :return: 返回成功失败
        """
        try:
            time.sleep(int(t))
            self.__write_excel(True, "等待")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def waitele(self, locator):
        """
        使用隐式等待，等待元素出现
        :param locator: 需要等待的元素
        :return:
        """
        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(True, "等待失败")
        else:
            self.__write_excel(True, "等待成功")

    def slide(self, p1, p2):
        try:
            p1 = p1.split(',')
            p2 = p2.split(',')
            # 滑动
            TouchAction(self.driver).press(x=int(p1[0]), y=int(p1[1])).move_to(x=int(p2[0]),
                                                                               y=int(p2[1])).release().perform()
            self.__write_excel(True, "滑动成功")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def input(self, locator, text, t=''):
        """

        :param locator: 定位器
        :param text: 需要输入的文本
        :return: 输入是否成功
        """
        if t == '':
            t = 10
        time.sleep(int(t))

        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            text = self.__get__relations(text)
            ele.send_keys(text)
            self.__write_excel(True, "输入成功")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def gettext(self, locator, param="text", t=''):
        """
        获取元素的文本，并保存为关联后参数名：param
        :param locator: 定位器
        :param param: 保存后的参数名
        :return: 获取成功失败
        """
        if t == '':
            t = 10
        time.sleep(int(t))

        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False

        try:
            text = ele.text
            # 设置到关联字典
            sysKey.relations[param] = text
            self.__write_excel(True, "输入成功")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def assertcontains(self, expectv, actualv):
        """
        web断言关键字，断言实际结果包含预期结果
        :param expectv: 预期结果
        :param actualv: 实际结果
        :return: 是否包含
        """

        # 关联
        actualv = self.__get__relations(actualv)
        expectv = self.__get__relations(expectv)

        if actualv.__contains__(str(expectv)):
            self.__write_excel(True, actualv)
            return True
        else:
            self.__write_excel(False, actualv)
            return False

    def click(self, locator, t=''):
        """
        通过定位器找到元素，并完成点击操作
        :param locator: 定位器
        :return: 点击成功/失败
        """
        if t == '':
            t = 10
        time.sleep(int(t))

        ele = self.__find_ele(locator)
        if ele is None:
            self.__write_excel(False, self.e)
            return False
        try:
            ele.click()
            self.__write_excel(True, "点击成功")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def adbclick(self, x, y, t=''):
        """
        通过定位器找到元素，并完成点击操作
        :param locator: 定位器
        :return: 点击成功/失败
        """
        if t == '':
            t = 10
        time.sleep(int(t))

        try:
            logger.info('adb shell input tap %s %s' % (x, y))
            os.popen('adb shell input tap %s %s' % (x, y)).read()
            self.__write_excel(True, "adb点击成功")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def quit(self):
        """
        退出浏览器
        :return: 成功失败
        """
        try:
            self.driver.quit()
            self.__write_excel(True, "退出")
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def __get__relations(self, params):
        """
        使用关联结果
        :param params: 需要关联的参数
        :return: 关联后的字符串
        """
        if params is None:
            return None
        else:
            params = str(params)

        for key in sysKey.relations.keys():
            params = params.replace('{' + key + '}', str(sysKey.relations[key]))
        return params

    def __find_ele(self, locator):
        """
        通过定位器找到元素
        :param locator: xpath
        :return: 返回找到的元素
        """
        try:
            if locator.startswith("/"):
                ele = self.driver.find_element_by_xpath(locator)
            elif locator.index(':id/') > 0:
                ele = self.driver.find_element_by_id(locator)
            else:
                ele = self.driver.find_element_by_accessibility_id(locator)

        except Exception as e:
            self.e = traceback.format_exc()
            return None

        return ele

    def __write_excel(self, status, msg):
        """
        写入关键字运行结果
        :param status: 运行的状态
        :param msg: 实际运行结果
        :return: 无
        """
        if status is True:
            self.writer.write(self.row, 7, "PASS", 3)
        else:
            self.writer.write(self.row, 7, "FAIL", 2)

        # 有时候实际结果过长，我们就只保存前1024个字符
        msg = str(msg)
        if len(msg) > 32767:
            msg = msg[0:32767]

        self.writer.write(self.row, 8, str(msg))