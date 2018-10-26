from copy import deepcopy
import requests
import json
from injson import check
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format


class Http:

    def __init__(self, step):
        # 获取 baseurl
        el, baseurl = e.get(step['page'] + '-' + 'baseurl', True)
        if not baseurl:
            self.baseurl = ''
        else:
            if not baseurl.endswith('/'):
                baseurl += '/'
            self.baseurl = baseurl

        self.r = requests.Session()
        # 获取 headers
        el, self.headers_get = e.get(step['page'] + '-' + 'headers_get', True)
        el, self.headers_post = e.get(step['page'] + '-' + 'headers_post', True)


def get(step):
    request('get', step)

def post(step):
    request('post', step)

def put(step):
    request('put', step)

def patch(step):
    request('patch', step)

def delete(step):
    request('delete', step)

def options(step):
    request('options', step)

def request(kw, step):
    element = step['element']
    el, url = e.get(element)
    if url.startswith('/'):
        url = url[1:]

    data = step['data']
    _data = {}
    _data['headers'] = eval(data.pop('headers', 'None'))
    if data.get('cookies'):
        data['cookies'] = eval(data['cookies'])
    if kw == 'get':
        _data['params'] = eval(data.pop('params', 'None')) or eval(data.pop('data', 'None'))
    elif kw == 'post':
        _data['data'] = eval(data.pop('data', 'None'))
        _data['json'] = eval(data.pop('json', 'None'))
        _data['files'] = eval(data.pop('files', 'None'))
    elif kw in ('put', 'patch'):
        _data['data'] = eval(data.pop('data', 'None'))

    for k in data:
        for s in ('{', '[', 'False', 'True'):
            if s in data[k]:
                try:
                    data[k] = eval(data[k])
                except Exception as exception:
                    logger.warning('Try eval data fail: %s' %data[k])
                break
    expected = step['expected']
    expected['status_code'] = expected.get('status_code', None)
    expected['text'] = expected.get('text', None)
    expected['json'] = eval(expected.get('json', None))
    expected['cookies'] = eval(expected.get('cookies', '{}'))

    if not g.http.get(step['page']):
        g.http[step['page']] = Http(step)
    http = g.http[step['page']]

    if kw == 'post':
        if http.headers_post:
            http.r.headers.update(eval(http.headers_post))
    else:
        if http.headers_get:
            http.r.headers.update(eval(http.headers_get))

    logger.info('URL: %s' % http.baseurl + url)
    if _data['headers']:
        for k in [x for x in _data['headers']]:
            if not _data['headers'][k]:
                del http.r.headers[k]
                del _data['headers'][k]
        http.r.headers.update(_data['headers'])

    if kw == 'get':
        r = getattr(http.r, kw)(http.baseurl + url,
                                params=_data['params'], **data)
    elif kw == 'post':
        r = getattr(http.r, kw)(http.baseurl + url,
            data=_data['data'], json=_data['json'], files=_data['files'], **data)
    elif kw in ('put', 'patch'):
        r = getattr(http.r, kw)(http.baseurl + url,
            data=_data['params'], **data)
    elif kw in ('delete', 'options'):
        r = getattr(http.r, kw)(http.baseurl + url, **data)

    logger.info('status_code: %s' % repr(r.status_code))
    try: # json 响应
        logger.info('response json: %s' % repr(r.json()))
    except: # 其他响应
        logger.info('response text: %s' % repr(r.text))

    if expected['status_code']:
        assert str(expected['status_code']) == str(r.status_code)

    if expected['text']:
        if expected['text'].startswith('*'):
            assert expected['text'][1:] in r.text
        else:
            assert expected['text'] == r.text

    if expected['cookies']:
        cookies = requests.utils.dict_from_cookiejar(r.cookies)
        logger.info('response cookies: %s' % cookies)
        result = check(expected['cookies'], cookies)
        if result['result']:
            step['remark'] += str(result['result'])
        logger.info('cookies check result: %s' % result)
        assert result['code'] == 0

    if expected['json']:
        result = check(expected['json'], r.json())
        if result['result']:
            step['remark'] += str(result['result'])
        logger.info('json check result: %s' % result)
        assert result['code'] == 0

    output = step['output']
    # if output:
    #     logger.info('output: %s' % repr(output))

    for k, v in output.items():
        if v == 'status_code':
            g.var[k] = r.status_code
            logger.info('%s: %s' %(k, repr(g.var[k])))
        elif v == 'text':
            g.var[k] = r.text
            logger.info('%s: %s' %(k, repr(g.var[k])))
        elif k == 'json':
            sub = eval(output.get('json', '{}'))
            result = check(sub, r.json())
            # logger.info('Compare json result: %s' % result)
            g.var = dict(g.var, **result['var'])
            logger.info('json var: %s' %(repr(result['var'])))
        elif k == 'cookies':
            sub = eval(output.get('cookies', '{}'))
            cookies = requests.utils.dict_from_cookiejar(r.cookies)
            result = check(sub, cookies)
            # logger.info('Compare json result: %s' % result)
            g.var = dict(g.var, **result['var'])
            logger.info('cookies var: %s' %(repr(result['var'])))
