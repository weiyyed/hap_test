from sweetest.autotest import Autotest
import sys


# 项目名称
project_name = 'Prod3'

# 单用例调试或挑用例执行
sheet_name = ['pre-m']

# 项目所有用例执行，*模糊匹配
#sheet_name = 'hap*'

# 环境配置信息
# Chrome
desired_caps = {
        "deviceName": "weiyongyou",
        "platformName": "android",
        "Android": "7.0",
        "appActivity": "com.hayden.hap.fv.login.ui.SplashActivity",
        "appPackage": "com.hayden.hap.fv",
        # "automationName": "uiautomator2"
                }
server_url = 'http://127.0.0.1:4723/wd/hub'


# 初始化自动化实例
sweet = Autotest(project_name, sheet_name, desired_caps, server_url)

# 按条件执行,支持筛选的属性有：'id', 'title', 'designer', 'priority'
sweet.fliter(id=['phd_m_0011','phd_m_002','phd_m_003'])

# 执行
sweet.plan()

#测试报告详细数据
#print(sweet.report_data)

# 如果是集成到 CI/CD，可以给出退出码
#sys.exit(sweet.code)
