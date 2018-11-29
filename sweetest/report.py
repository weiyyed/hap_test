from datetime import datetime
from xml.dom.minidom import Document


class Report():

    def __init__(self):
        self.testsuites = []

    def create_suite(self, name, hostname="localhost"):
        # 返回TestSuite实例
        ''' 返回TestSuite实例'''
        suite = TestSuite(name, hostname)
        self.testsuites.append(suite)
        return suite

    def finish(self):
        for suite in self.testsuites:
            if suite.open == True:
                suite.finish()

    def write(self, file):
        self.finish()
        doc = Document()
        root = doc.createElement("testsuites")
        doc.appendChild(root)
        for suite in self.testsuites:
            root.appendChild(suite.to_xml(doc))
        file.write(doc.toprettyxml())


    def data(self):
        self.data = {}
        for suite in self.testsuites:
            s = self.data[suite.name+'-'+suite.hostname] = {}
            s['project'] = suite.name
            s['suite'] = suite.hostname
            s['timestamp'] = suite.timestamp
            s['tests'] = suite.tests
            s['failures'] = suite.failures
            s['errors'] = suite.errors
            s['time'] = suite.time

            cases = s['cases'] = []
            for case in suite.cases:
                c = {}
                c['name'] = case.name
                c['classname'] = case.classname
                c['priority'] = case.priority
                c['time'] = case.time
                c['state'] = case.state
                if case.state != "success":
                    c['type'] = case.type
                    c['message'] = case.message
                else:
                    c['type'] = ''
                    c['message'] = ''
                cases.append(c)

        return self.data


class TestSuite():
    def __init__(self, name, hostname):
        self.properties = []
        self.name = name
        self.hostname = hostname
        self.open = False
        self.cases = []
        self.systemout = None
        self.systemerr = None

    def start(self):
        self.open = True
        self.time = datetime.now()
        self.timestamp = datetime.isoformat(self.time)
        return self

    def create_case(self, name, classname=""):
        if self.open:
            case = TestCase(name, classname)
            self.cases.append(case)
            return case
        else:
            raise Exception(
                "This test suite cannot be modified in its current state")

    def append_property(self, name, value):
        self.properties.append([name, value])

    def finish(self, output=None, error=None):
        if self.open == True:
            self.open = False
            # set the number of test cases, error cases, failed cases, and the amount of time taken in seconds.
            td = datetime.now() - self.time
            self.time = float(
                (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6
            self.errors = 0
            self.high_errors = 0
            self.medium_errors = 0
            self.low_errors = 0
            self.failures = 0
            self.high_failures = 0
            self.medium_failures = 0
            self.low_failures = 0
            for case in self.cases:
                if case.state == None:
                    case.error(
                        "XmlUnit Finished", "The test was forced to finish since the suite was finished.")
                status = case.state.lower()
                if status == "failure":
                    self.failures += 1
                    if case.priority == 'H':
                        self.high_failures += 1
                    if case.priority == 'M':
                        self.medium_failures += 1
                    if case.priority == 'L':
                        self.low_failures += 1
                elif status == "error":
                    self.errors += 1
                    if case.priority == 'H':
                        self.high_errors += 1
                    if case.priority == 'M':
                        self.medium_errors += 1
                    if case.priority == 'L':
                        self.low_errors += 1
                else:
                    pass
            self.tests = len(self.cases)
            self.output = output
            self.error = error
            return None
        else:
            raise Exception("This test suite is already finished.")

    def to_xml(self, doc):
        node = doc.createElement("testsuite")
        node.setAttribute("name", self.name)
        node.setAttribute("hostname", self.hostname)
        node.setAttribute("timestamp", self.timestamp)
        node.setAttribute("tests", "%s" % self.tests)
        node.setAttribute("failures", "%s" % self.failures)
        node.setAttribute("failures_detail", "H:%s M:%s L:%s" % (
            self.high_failures, self.medium_failures, self.low_failures))
        node.setAttribute("errors", "%s" % self.errors)
        node.setAttribute("errors_detail", "H:%s M:%s L:%s" % (
            self.high_errors, self.medium_errors, self.low_errors))
        node.setAttribute("time", "%s" % self.time)
        for case in self.cases:
            node.appendChild(case.to_xml(doc))

        return node


class TestCase():

    def __init__(self, name, classname):
        self.state = None
        self.name = name
        self.classname = classname
        self.priority = 'M'
        return None

    def start(self):
        self.time = datetime.now()
        return self

    def custom(self, state, type, message):
        if self.state != None:
            raise Exception("This test case is already finished.")
        self.state = state
        self.message = message
        self.type = type
        td = datetime.now() - self.time
        self.time = float(
            (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6

    def fail(self, type, message):
        self.custom("failure", type, message)

    def skip(self, type, message):
        self.custom("skipped", type, message)

    def error(self, type, message):
        self.custom("error", type, message)

    def block(self, type, message):
        self.custom("blocked", type, message)

    def succeed(self):
        if self.state != None:
            raise Exception("This test case is already finished.")
        self.state = "success"
        td = datetime.now() - self.time
        self.time = float(
            (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6

    def to_xml(self, doc):
        node = doc.createElement("testcase")
        node.setAttribute("name", self.name)
        node.setAttribute("classname", self.classname)
        node.setAttribute("priority", self.priority)
        node.setAttribute("time", "%s" % self.time)
        if self.state != "success":
            subnode = doc.createElement(self.state)
            subnode.setAttribute("type", self.type)
            subnode.setAttribute("message", self.message)
            node.appendChild(subnode)
        return node
