
from os import path
import os
import time
import sys
import json
from sweetest.data import testsuite_format, testsuite2data, testsuite2report
from sweetest.parse import parse
from sweetest.elements import e
from sweetest.globals import g
from sweetest.windows import w
from sweetest.testsuite import TestSuite
from sweetest.testcase import TestCase
from sweetest.utility import Excel, get_record,get_all_record
from sweetest.log import logger
from sweetest.report import Report
from sweetest.config import _testcase, _elements, _report


class Autotest:

    def __init__(self, file_name, sheet_name, desired_caps={}, server_url=''):
        g.start_time = time.strftime("@%Y%m%d_%H%M%S", time.localtime())

        if desired_caps:
            self.desired_caps = desired_caps
            desired_caps_init={
                "noReset": True,
                "unicodeKeyboard": True,
                "newCommandTimeout": "600",
            }
            self.desired_caps.update(desired_caps_init)
        else:
            self.desired_caps = {
                'platformName': 'Desktop', 'browserName': 'Chrome'}
        self.server_url = server_url

        self.conditions = {}
        
        g.project_name = file_name.split('-')[0]
        self.testcase_file = path.join(
            'testcase', file_name + '-' + _testcase + '.xlsx')
        self.elements_file = path.join(
            'element', g.project_name + '-' + _elements + '.xlsx')
        if not path.exists('junit'):
            os.mkdir('junit')
        self.report_xml = path.join(
            'junit', file_name + '-' + _report + g.start_time + '.xml')
        #打开excel
        self.testcase_workbook = Excel(self.testcase_file, 'r')
        #获取列表
        self.sheet_names = self.testcase_workbook.get_sheet(sheet_name)
        if not path.exists('report'):
            os.mkdir('report')
            #写方式打开report-excel
        self.report_workbook = Excel(
            path.join('report', file_name + '-' + _report + g.start_time + '.xlsx'), 'w')

        self.report_data = {}  # 测试报告详细数据


    def fliter(self, **kwargs):
        # 筛选要执行的测试用例
        self.conditions = kwargs

    #测试套件执行
    def plan(self):
        self.code = 0  # 返回码
        # 1.解析配置文件
        try:
            e.get_elements(self.elements_file)
        except:
            logger.exception('*** Parse config file fail ***')
            self.code = -1
            sys.exit(self.code)

        self.report = Report()
        self.report_ts = {}

        # 2.逐个执行测试套件
        for sheet_name in self.sheet_names:
            g.sheet_name = sheet_name
            # xml 测试报告初始化
            self.report_ts[sheet_name] = self.report.create_suite(
                g.project_name, sheet_name)
            self.report_ts[sheet_name].start()

            self.run(sheet_name)

        self.report_workbook.close()

        with open(self.report_xml, 'w', encoding='utf-8') as f:
            self.report.write(f)

        self.report.data()

    #用例执行
    def run(self, sheet_name):
        # 1.从 Excel 获取测试用例集
        try:
            data = self.testcase_workbook.read(sheet_name)
            testsuite = testsuite_format(data)
            # logger.info('Testsuite imported from Excel:\n' +
            #             json.dumps(testsuite, ensure_ascii=False, indent=4))
            logger.info('From Excel import testsuite success')
        except:
            logger.exception('*** From Excel import testsuite fail ***')
            self.code = -1
            sys.exit(self.code)

        # 2.初始化全局对象
        try:
            g.init(self.desired_caps, self.server_url)
            g.set_driver()
            # 如果测试数据文件存在，则从该文件里读取一行数据，赋值到全局变量列表里
            data_file = path.join(
                'data', g.project_name + '-' + sheet_name + '.csv')
            if path.exists(data_file):
                g.var = get_record(data_file)
            data_file = path.join(
                'data', g.project_name + '-' + sheet_name + '-globle.txt')
            if path.exists(data_file):
                g.var.update(get_all_record(data_file))
            w.init()
        except:
            logger.exception('*** Init global object fail ***')
            self.code = -1
            sys.exit(self.code)

        # 3.解析测试用例集
        try:
            parse(testsuite)
            logger.debug('testsuite has been parsed:\n' + str(testsuite))
        except:
            logger.exception('*** Parse testsuite fail ***')
            self.code = -1
            sys.exit(self.code)

        # 4.执行测试套件
        ts = TestSuite(testsuite, self.report_ts[sheet_name], self.conditions)
        ts.run()

        # 5.判断测试结果
        if self.report_ts[sheet_name].high_errors + self.report_ts[sheet_name].medium_errors + \
                self.report_ts[sheet_name].high_failures + self.report_ts[sheet_name].medium_failures:
            self.code = -1

        # 6.保存测试结果
        try:
            self.report_data[sheet_name] = testsuite2report(testsuite)
            data = testsuite2data(testsuite)
            self.report_workbook.write(data, sheet_name)
        except:
            logger.exception('*** Save the report is fail ***')
