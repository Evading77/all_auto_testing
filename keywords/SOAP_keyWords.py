import json, traceback, requests,jsonpath
from suds.client import Client
from frameworkutils import logger
from keywords.commenkeys import sysKey


class SOAP:
    """
        自动化架构体系
        数据驱动运行入口

    """

    def __init__(self, writer):
        # 创建头部管理
        self.headers = {}
        # wsdl描述文档请求地址
        self.wsdl = ""
        # 保存请求结果
        self.result = None
        # 保存json解析后的字典
        self.jsonres = None
        # 写入结果的对象
        self.writer = writer
        # 记录关键字运行时，写入excel的行
        self.row = 0
        # 请求webservice接口的客户端对象
        self.client = None

    def setwsdl(self, url):
        """
        设置项目接口基本地址
        :param url: wsdl文档地址
        :return: 成功失败
        """
        # 对传入参数的处理
        if url is None or url == '':
            url = ''

        self.wsdl = url
        # 创建一个客户端去请求服务器
        try:
            self.client = Client(self.wsdl)
            self.__write_excel(True, self.wsdl)
        except Exception as e:
            logger.exception(e)
            self.__write_excel(False, traceback.format_exc())
            return False

        return True

    def callmethod(self, path, params):
        """
        以列表形式传webservice接口参数
        :param path: 接口名
        :param params: 参数
        :return: 成功失败
        """

        # 实现关联
        params = self.__get__relations(params)

        # 对传入参数的处理
        if params is None or params == '':
            params = None
        else:
            params = self.__get_list(params)

        # 对path进行处理
        if path is None or path == '':
            # 接口地址不应该为空
            self.__write_excel(False, "接口名字错误")
            return False

        # 处理url连接失败的情况
        try:
            if params is None:
                self.result = self.client.service.__getattr__(path)()
            else:
                self.result = self.client.service.__getattr__(path)(*params)
        except Exception as e:
            logger.exception(e)
            self.result = None

        print(self.result)

        try:
            # 如果返回的是json字符串，就处理为字典
            resulttext = self.result
            resulttext = resulttext[resulttext.find('{'):resulttext.rfind('}') + 1]
            self.jsonres = json.loads(resulttext)
            self.__write_excel(True, self.jsonres)
        except Exception as e:
            logger.exception(e)
            self.jsonres = None
            if self.result is None:
                self.__write_excel(False, None)
            else:
                self.__write_excel(True, self.result)

        return True

    def addheader(self, key, value):
        """
        往请求头里面添加一个键值对
        :param key: 头的键
        :param value: 头的值
        :return: 成功失败
        """
        value = self.__get__relations(value)
        self.headers[key] = value
        # 创建一个客户端去请求服务器
        try:
            self.client = Client(self.wsdl,headers=self.headers)
            self.__write_excel(True, self.headers)
        except Exception as e:
            logger.exception(e)
            self.__write_excel(False, traceback.format_exc())
            return False

        return True

    def removeheader(self, key):
        """
        从请求头删除一个键值对
        :param key: 需要删除的键
        :return: 成功失败
        """
        try:
            self.headers.pop(key)
        except Exception as e:
            pass

        # 创建一个客户端去请求服务器
        try:
            self.client = Client(self.wsdl,headers=self.headers)
            self.__write_excel(True, self.headers)
        except Exception as e:
            logger.exception(e)
            self.__write_excel(False, traceback.format_exc())
            return False

        return True

    def assertequals(self, key, value):
        """
        断言json结果里面某个键的值和value相等
        :param key: json的键
        :param value: 期望值
        :return: 是否相等
        """
        # 如果请求返回不是json，就直接return
        if self.jsonres is None:
            self.__write_excel(False, None)
            return False

        value = self.__get__relations(value)

        try:
            actual = str(jsonpath.jsonpath(self.jsonres, key)[0])
            if actual == str(value):
                self.__write_excel(True, actual)
                return True
            else:
                self.__write_excel(False, actual)
                return False
        except Exception as e:
            # 处理键不存在的情况
            self.__write_excel(False, traceback.format_exc())
            return False

    def savejson(self, jsonkey, paramname):
        """
        从jsonres里面保存某个键的值，用来关联
        :param jsonkey: 需要保存的json的键
        :param paramname: 保存后参数的名字
        :return: 成功失败
        """
        # 去jsonres里面取值
        try:
            value = str(jsonpath.jsonpath(self.jsonres, jsonkey)[0])
        except Exception as e:
            value = None
        # 保存键值对到关联字典
        sysKey.relations[paramname] = value

        self.__write_excel(True, sysKey.relations)
        return True

    def assertequaljson(self, jsonp):
        """
        断言json结果里多个键值对相等
        :param jsonp: 传入你需要比较的多个键值对的json字符串
        :return: 是否相等
        """
        # 如果请求返回不是json，就直接return
        if self.jsonres is None:
            self.__write_excel(False, None)
            return False

        try:
            # 传入的参数不是json，传参错误
            jsonp = json.loads(jsonp)
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

        try:
            # 处理键不存在的情况
            for key in jsonp.keys():
                # 只要有一个键值对不相等，就不相等
                value = str(jsonpath.jsonpath(self.jsonres, key)[0])
                if not value == str(jsonp[key]):
                    self.__write_excel(False, self.jsonres)
                    return False
            # 所有键值对都相等，才返回True
            self.__write_excel(True, self.jsonres)
            return True
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

    def assertcontains(self, value):
        """
        断言返回结果的字符串包含value
        :param value: 被包含的字符串
        :return: 是否包含
        """
        try:
            # 如果返回结果为空，就报错
            result = str(self.result.text)
        except Exception as e:
            self.__write_excel(False, traceback.format_exc())
            return False

        value = self.__get__relations(value)

        if result.__contains__(str(value)):
            self.__write_excel(True, self.result.text)
            return True
        else:
            self.__write_excel(False, self.result.text)
            return False

    def __get_list(self, params):
        """
        url参数转字典
        :param params: 需要转字典的参数
        :return: 转换后的字典
        """
        if params is None:
            return None

        param = params.split('、')
        return param

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