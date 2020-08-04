'''
    自动化架构体系
    数据驱动运行入口
'''
import time

from frameworkutils import logger, Encrypt
from frameworkutils.NewExcel import Reader, Writer
from frameworkutils.baseutils import runcase
from frameworkutils.excelresult import Res
from frameworkutils import config
from frameworkutils.mail import Mail
from frameworkutils.txt import Txt
from keywords.App_keyWords import App
from keywords.HTTP_keyWords import HTTP
from keywords.SOAP_keyWords import SOAP
from keywords.Web_keyWords import Web

logger.info("开始运行")

#初始化配置

config.get_config(r'F:\Code\trunk\Code\all_auto_testing\configFile\conf.properties')


#用例名称
casename='HTTP接口用例-all'

reader=Reader()
reader.open_excel('./../testdata/%s.xlsx' % casename)
writer=Writer()
writer.copy_open('./../testdata/%s.xlsx' % casename,'./../testdata/result-%s.xlsx' % casename)
sheetname = reader.get_sheets()

# 写开始时间
starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
writer.set_sheet(sheetname[0])
writer.write(1,3,starttime)

# 运行的实例对象，默认是HTTP
http = HTTP(writer)
# soap = SOAP(writer)
# web = Web(writer)
# app = App(writer)
obj = http



for sheet in sheetname:
    # 设置当前读取的sheet页面
    reader.set_sheet(sheet)
    writer.set_sheet(sheet)

    # openpyxl
    lines = reader.readline()

    # 分用例类型执行
    line = lines[1]
    if line[1] == "HTTP":
        obj = http
    # elif line[1] == "SOAP":
    #     obj = soap
    # elif line[1] == "WEB":
    #     obj = web
    # elif line[1] == "APP":
    #     obj = app

    for i in range(reader.rows):
        obj.row = i
        line = lines[i]
        logger.info(line)
        runcase(obj, line)


# 写结束时间
endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
writer.set_sheet(writer.get_sheets()[0])
writer.write(1,4,endtime)
writer.save_close()


# 获取结果数据
res = Res()
summary = res.get_res('./../testdata/result-%s.xlsx' % casename)
logger.info(summary)
groups = res.get_groups('./../testdata/result-%s.xlsx' % casename)
logger.info(groups)

txt = Txt('./../configFile/' + config.config['mailtxt'])
html = txt.read()[0]

# 替换汇总信息
for key in summary.keys():
    if summary[key]=="Pass":
        html = html.replace('<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;">status</td>',
                     '<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;color:blue;">Pass</td>')
    elif summary[key]=="Fail":
        html = html.replace('<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;">status</td>',
                     '<td height="28" bgcolor="#FFFFFF" align="center" style="border:1px solid #ccc;color:red;">Fail</td>')
    else:
        html = html.replace(key,summary[key])

# 获取分组显示
tr = '<tr><td width="100" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">分组信息</td><td width="80" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">用例总数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">通过数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">状态</td></tr>'
trs = ""
for i in range(len(groups)):
    tmp = tr.replace('分组信息',str(groups[i][0]))
    tmp = tmp.replace('用例总数', str(groups[i][1]))
    tmp = tmp.replace('通过数', str(groups[i][2]))
    tmp = tmp.replace('状态', str(groups[i][3]))
    trs += tmp

html = html.replace('mailbody',trs)
mail = Mail()
mail.send(html)

