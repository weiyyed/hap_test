from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sweetest.elements import e
from sweetest.globals import g
from sweetest.windows import w
from sweetest.log import logger
from sweetest.config import element_wait_timeout
from selenium.common.exceptions import TimeoutException

def locating_element(element, action=''):
    #移动端翻页找元素
    if g.platform.lower() == 'android':
        i = 0
        while True:
            try:
                return _locating_element(element,element_wait_timeout-2)
            except TimeoutException as e:
                # page=g.driver.page_source
                # num=len(g.driver.find_elements_by_class_name('android.widget.FrameLayout'))
                g.driver.swipe(g.width / 2, g.height * 0.8, g.width / 2, g.height * 0.2)
                i = i + 1
                # or len(g.driver.find_elements_by_class_name('android.widget.FrameLayout')) == num
                if i >= 3 :
                    raise e
                    # return
    else:
        return _locating_element(element,element_wait_timeout)




def _locating_element(element,waittime,action='',):
    el_location = None
    try:
        el, value = e.get(element)
    except:
        logger.exception(
            'Locating the element:%s is Failure, no element in define' % element)
        raise Exception('Locating the element:%s is Failure, no element in define' % element)

    wait = WebDriverWait(g.driver, waittime)

    if el['by'].lower() in ('title', 'url', 'current_url'):
        return None
    elif action == 'CLICK':
        el_location = wait.until(EC.element_to_be_clickable(
            (getattr(By, el['by'].upper()), value)))
    else:
        logger.debug('locating the element %s'%value)
        el_location = wait.until(EC.presence_of_element_located(
            (getattr(By, el['by'].upper()), value)))

    return el_location


def locating_elements(elements):
    elements_location = {}
    for el in elements:
        elements_location[el] = locating_element(el)
    return elements_location


def locating_data(keys):
    data_location = {}
    for key in keys:
        data_location[key] = locating_element(key)
    return data_location
