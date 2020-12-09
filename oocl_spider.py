
from random import randint
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 模拟滑动函数
def get_track(distance: int=0) -> list:
    track = []
    current = 0
    mid = distance*(3/5)
    t,v,v1,a1,a = 3,0,0,2,5

    while current < distance:
        if current < mid:
            move = v*t + 1/2*a*t*t
            current += move
            track.append(round(move))
            v = v + a*t
        else:
            move1 = v1*t + 1/2*a1*t*t
            current += move1
            track.append(round(move1))
            v1 = v1 + a1*t
    
    # 补全调整因公式不符产生的偏差量
    _distance = distance
    _gap = 0
    _track = []
    for idx, value in enumerate(track):
        _distance -= value
        if _distance <= 0:
            _gap = distance-sum(track[0:idx])
            _track = track[0:idx]
            _track.append(_gap)
            break
        else:
            continue
    
    return _track

# print(get_track(258))
# sleep(600)

# 使用开发者模式创建一个浏览器对象
option = Options()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(chrome_options=option)
cookie1 = {
    "domain": "www.oocl.com",
    # "domain": "webchat.oocl.com",
    "name": "AcceptCookie",
    "value": "yes"
}
cookie2 = {
    "domain": "webchat.oocl.com",
    "name": "ASP.NET_SessionId",
    "value": "kenwxk55yate3a3iegdvmj45"  # 注意更新该session id
}

# 重置浏览器webdriver的值
# driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#   "source": """
#     Object.defineProperty(navigator, 'webdriver', {
#       get: () => undefined
#     })
#   """
# })

# 打开谷歌浏览器
try:
    # # 打开网站
    # driver.get('https://www.oocl.com/schi/Pages/default.aspx')
    
    # # add_cookie 必须在网页打开之后，否则会报错
    # driver.add_cookie(cookie_dict=cookie1)
    # # driver.add_cookie(cookie_dict=cookie2)

    # sleep(10)
    
    # # 打印当前窗口句柄
    # idx_handle = driver.current_window_handle
    # print("-"*30+"\n"+"Index Window Handle is " + idx_handle+"-"*30+"\n")
    
    # # 找到SEARCH_NUMBER这个元素
    # input = driver.find_element_by_id('SEARCH_NUMBER')
    # # 输入搜索信息
    # input.send_keys('OOCL12345678')
    # # 敲入回车
    # input.send_keys(Keys.ENTER)

    # # 获取当前打开页的所有句柄并打印
    # all_handles = driver.window_handles
    # print("-"*30+"\n"+"All Window Handle is ")
    # print(all_handles)
    # print("-"*30+"\n")

    # # 获取当前弹窗句柄
    # new_handle = [handle for handle in all_handles if handle != idx_handle]
    # print("-"*30+"\n"+"New Window Handle is " + new_handle[0]+"-"*30+"\n")

    # driver 转到当前弹出窗口
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
      "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.get("https://moc.oocl.com/party/cargotracking/ct_search_from_other_domain.jsf?ANONYMOUS_BEHAVIOR=BUILD_UP&domainName=PARTY_DOMAIN&ENTRY_TYPE=OOCL&ENTRY=MCC&ctSearchType=BL&ctShipmentNumber=OOCL12345678")
    # driver.switch_to.window(new_handle[0])
    driver.add_cookie(cookie_dict=cookie1)
    # driver.add_cookie(cookie_dict=cookie2)

    # 拖动滑块
    print("-"*30+"\n"+"url before sliding the button is "+driver.current_url+"-"*30+"\n")
    
    button = driver.find_element_by_id('nc_1_n1z')  # 找到滑块，大小42 X 34
    action = ActionChains(driver)
    action.click_and_hold(button).perform()
    # action.move_by_offset(258, 0)  # 滑道总长度 300 X 34

    trace = get_track(distance=258)

    # 模拟先快后慢的滑动方式
    for step in trace:
        try:
            # action.drag_and_drop_by_offset(button, xoffset=step, yoffset=randint(1,3)).perform()
            action.move_by_offset(step,0).perform()
        except UnexpectedAlertPresentException:
            break
        action.reset_actions()

    sleep(60)
    # action.release().perform()

    # 等待
    # sleep(600)

    # wait.until(EC.presence_of_element_located((By.ID, 'content_left')))
    # 等待元素被加载出来
    print("-"*30+"\n"+"url after sliding the button is "+driver.current_url+"-"*30+"\n")
    print(driver.page_source)

    text = driver.page_source
    with open('page_after_skipping_captcha.html',"w") as f:
        _text = text.encode('utf-8').decode('unicode-escape')
        f.write(_text)
    
finally:
    driver.close()


# 滑块html <span id="nc_1_n1z" class="nc_iconfont btn_slide"></span>
# https://moc.oocl.com/party/cargotracking/ct_search_from_other_domain.jsf?ANONYMOUS_BEHAVIOR=BUILD_UP&domainName=PARTY_DOMAIN&ENTRY_TYPE=OOCL&ENTRY=MCC&ctSearchType=BL&ctShipmentNumber=OOCL2345678
