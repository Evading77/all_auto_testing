
# 数据驱动运行
import inspect

from frameworkutils import logger


def getfunc(obj, method):
    """
    反射获取函数和参数列表
    :param obj: 对象
    :param method: 方法名
    :return:
    """
    try:
        func = getattr(obj, method)
    except Exception as e:
        return None

    arg = inspect.getfullargspec(func).__str__()
    arg = arg[arg.find('args=') + 5:arg.find(', varargs')]
    arg = eval(arg)
    arg.remove('self')
    return func, len(arg)


def runcase(obj, line):
    if len(line[0]) > 0 or len((line[1])) > 0:
        # 分组信息不执行
        return

    func = getfunc(obj, line[3])
    if func is None:
        logger.warn("关键字%s不存在" % line[3])
        return

    if func[1] == 0:
        func[0]()
    elif func[1] == 1:
        func[0](line[4])
    elif func[1] == 2:
        func[0](line[4], line[5])
    elif func[1] == 3:
        func[0](line[4], line[5], line[6])
    else:
        logger.warn("关键字暂不支持超过3个参数")