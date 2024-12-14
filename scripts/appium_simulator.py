from appium import webdriver

def start_simulation(account_info):
    # 初始化Appium驱动
    desired_caps = {
        "platformName": "Android",
        "deviceName": "device",
        "appPackage": "com.damai.android",
        "appActivity": ".activity.MainActivity",
    }
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    # 执行模拟操作
    # 例如模拟点击、滑动、输入等
    driver.find_element_by_id("com.damai.android:id/login_button").click()
    driver.quit()
