from selenium import webdriver
from sweetest.config import element_wait_timeout, page_flash_timeout

# 启动浏览器，
class Global:
    # 项目，用例页签名
    def __init__(self):
        self.start_time = ''
        self.project_name = ''
        self.sheet_name = ''

    def init(self, desired_caps, server_url):
        self.desired_caps = desired_caps
        self.server_url = server_url
        self.platform = desired_caps.get('platformName', '')
        self.browserName = desired_caps.get('browserName', '')
        self.var = {} #测试数据
        self.snippet = {}
        self.current_page = '通用'
        self.db = {}
        self.http = {}
        self.baseurl = {}
        self.driver = ''
        self.action = {}
        self.width=''
        self.height=''
#启动
    def set_driver(self):
        if self.platform.lower() == 'desktop':
            if self.browserName.lower() == 'ie':
                self.driver = webdriver.Ie()
            elif self.browserName.lower() == 'firefox':
                self.driver = webdriver.Firefox()
                self.driver.maximize_window()
            elif self.browserName.lower() == 'chrome':
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                prefs = {"": ""}
                prefs["credentials_enable_service"] = False
                prefs["profile.password_manager_enabled"] = False
                options.add_experimental_option("prefs", prefs)
                options.add_argument('disable-infobars')
                options.add_experimental_option(
                    "excludeSwitches", ["ignore-certificate-errors"])
                self.driver = webdriver.Chrome(chrome_options=options)
            else:
                raise Exception(
                    'Error: this browser is not supported or mistake name：%s' % self.browserName)
            # 等待元素超时时间
            self.driver.implicitly_wait(element_wait_timeout)  # seconds
            # 页面刷新超时时间
            self.driver.set_page_load_timeout(page_flash_timeout)  # seconds

        elif self.platform.lower() == 'ios':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)

        elif self.platform.lower() == 'android':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)
            self.width = self.driver.get_window_size()['width']
            self.height = self.driver.get_window_size()['height']


    def close(self):
        self.driver.close()


g = Global()
