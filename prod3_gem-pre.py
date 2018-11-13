from sweetest.autotest import Autotest
import sys


# 项目名称
project_name = 'Prod3'

# 单用例调试或挑用例执行
# sheet_name = ['single']

# 项目所有用例执行，*模糊匹配
sheet_name = 'gem-pre'


# 环境配置信息
# Chrome
desired_caps = {'platformName': 'Desktop', 'browserName': 'Chrome'}
server_url = ''


# 初始化自动化实例
sweet = Autotest(project_name, sheet_name, desired_caps, server_url)

# 按条件执行,支持筛选的属性有：'id', 'title', 'designer', 'priority'
# sweet.fliter(priority='H')

# 执行
sweet.plan()

#测试报告详细数据
#print(sweet.report_data)

# 如果是集成到 CI/CD，可以给出退出码
#sys.exit(sweet.code)
