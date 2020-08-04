# -*- coding: UTF-8 -*-
import os, jpype
# pip install JPype1==0.7.0


# 加密实例
instance = None

def init():
    global instance
    # 需要导入的jar位置
    jarpath = './lib/conf/encrypt.jar'
    # 获取java安装路径
    jdkpath = os.environ['JAVA_HOME']

    # 启动jvm，加载jar
    jpype.startJVM(jdkpath + "/jre/bin/server/jvm.dll",
                   "-Djava.class.path=%s" % jarpath,
                   convertStrings=False)
            # 当有依赖的JAR包存在时，一定要使用-Djava.ext.dirs参数进行引入

    # 获取jar中的类
    JClass = jpype.JClass('com.testingedu.will.Encrypt')
    # 初始化类，就是执行构造函数
    instance = JClass()


def encrypt(s):
    """
    加密函数
    :param s: 需要加密的字符串
    :return: 加密后的字符串
    """
    global instance

    # 调用加密函数，instance相当于java的对象
    result = str(instance.enCrypt(s))
    return result


def decrypt(s):
    """
    加密函数
    :param s: 需要解密密的字符串
    :return: 解密后的明文
    """
    global instance
    # 调用解密函数
    result = str(instance.deCrypt(s))
    return result


def shutdown():
    """
    关闭jvm
    :return: 无
    """
    # 关闭jvm
    jpype.shutdownJVM()


if __name__ == "__main__":
    init()
    print(decrypt('BJJDvOKMSgjAr2ua0FK6dqpvtkBJrmjPS5ZytYGeLcxnSDxsTJa8F04qwgmSE3GcB/MCgRzLN07HXDlYm7N75b0z5RGDLnKVVrr9GPS/8HnNQG9DhOes4kqnsT+XAek1N05IV78onr6E2F1DgcekkQTjnlasCOA3WVRk3IHDeGmFSlyOZLdOcBwZlC9u1WHgHNoMN+K77q+fB1ErSC9vleh3GWzJ2QwQoiKC8s5V+5JmO7YIILwFYaFjO9Lwy0FtJSWeDfwI6WfZ+2TdZibCYAz6X9iMNYzhmHQ9Z5nwCmHaivJBxQs0gxBN7Q+gZwkfkDs5B9yVZfSxjujE0i/Jhg=='))