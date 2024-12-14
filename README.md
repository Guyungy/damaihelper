# 抢票脚本 V3.0
![Damaihelper Star History](https://api.star-history.com/svg?repos=Guyungy/damaihelper&type=Date)

> 黄牛太多，抢票困难。开发此脚本，支持大麦网、淘票票、缤玩岛等平台，提升抢票成功率。

## 更新记录模拟
- **2024年12月**: 
    - 增加渠道切换功能，解决“该渠道暂不支持购买”问题。
    - 修复页面刷新失败、按钮定位失效等常见问题，提升脚本稳定性。
- **2024年4月1日**: 
    - 增加选座购买功能和代理IP池，提高抢票成功率。
- **2023年9月15日**: 
    - 优化抢票算法，支持设置抢票时间段，增强稳定性。

### 模拟功能介绍

1. **模拟手机端人工操作**：
   - 使用Appium来模拟手机端的操作，包括模拟用户的点击、滑动、输入等行为
2. **多平台支持**：
   - 使用Selenium，通过分析不同平台的页面结构和API，实现多平台支持
3. **多账户抢票**：
   - 在配置文件中管理多个账户的信息，包括用户名、密码、抢票策略
   - 多线程或异步编程技术，同时处理多个账户的抢票任务

4. **切换代理IP池**：
   - 支持代理IP池，Scrapy和ProxyPool，实现IP的动态切换

5. **定时预约场次**：
   - 用定APScheduler，设置定时任务来执行预约场次的操作
   - 灵活地配置定时任务的执行时间，并实现任务的自动触发和执行

### 测试中的功能

- 验证码识别：百度OCR，识别抢票过程中出现的验证码




## 模拟配置文件说明

- `date`: 日期序号，仅支持一个日期选择。
- `sess`: 场次序号，优先选中的场次序号放在前，填写的场次序号若大于实际场次序号，则会选中实际场次序号最大的。
- `price`: 票档序号，优先选中的票档序号放在前，填写的票档序号若大于实际票档序号，则会选中实际票档序号最大的。
- `real_name`: 实名者序号，已经弃用。
- `nick_name`: 用户昵称，已经弃用。
- `ticket_num`: 购买票数，购买票数与观影人序号的数量务必一致。
- `viewer_person`: 观影人序号（预先添加实名观影人），优先选中的序号放在前，填写的序号若大于实际序号，则会放弃选中。
- `driver_path`: 驱动地址。
- `damai_url`: 大麦首页地址，用于登录。
- `target_url`: 购票的实际地址，需要使用手机端的地址，域名: https://m.damai.cn/ 开头。
- `queue`: 列入待抢的链接地址。
- `auto_buy`: 是否开启自动抢票功能，true表示开启，false表示关闭。
- `auto_buy_time`: 自动抢票时间，格式为 "HH:MM:SS"，例如 "08:30:00"。
- `retry_interval`: 自动抢票失败后重试间隔时间，单位为秒，默认为 5 秒。
- `proxy`: 是否使用代理IP进行请求，true表示使用，false表示不使用。
- `proxy_ip`: 代理IP地址。
- `proxy_port`: 代理IP端口号。

## 模拟注意事项

1. 账号必须先做好实名制认证，并添加至少一个实名制的人的信息。
2. 第一次打开后会进入登录页面，需要手动选择扫码登陆。
3. 如果太久没用，需要先清空目录下的 cookie 文件，然后在重新登录。

## 模拟使用说明

### 环境准备
1. 安装所需要的环境。
2. 需要下载与系统安装对应的 ChromeDriver 驱动并配置（也可以改用其他浏览器驱动）。
   > 下载地址: http://chromedriver.storage.googleapis.com/index.html
3. 初次登录没有 cookies，默认登录方式为账号密码登录方式，可改成其他方式进行登录，如扫码或短信登录。
4. 设置自动抢票功能时，请确保填写了 `auto_buy_time` 字段，并且时间格式正确。
5. 设置代理IP功能时，请确保填写了 `proxy_ip` 和 `proxy_port` 字段，并且格式正确。
   
### 多平台抢票
## 多账户抢票支持

为了满足用户同时使用多个账户进行抢票的需求，跨平台票务抢票脚本 V2.1 引入了多账户抢票功能。以下是如何配置和使用多账户进行抢票的详细说明：

### 配置多账户
1. **账户信息配置**：在脚本的配置文件中（通常是 `config.json` 或 `settings.ini`），您需要为每个账户设置一个账户标识符，并为其指定登录凭据和其他必要的个人信息。例如：

```json
<<<<<<< main
{
    "date": [
        14
    ],
    "sess": [
        1,
        2
    ],
    "price": [
        1,
        2,
        3,
        4,
        5,
        6
    ],
    "real_name": [
        1
    ],
    "nick_name": "",
    "ticket_num": 1,
    "viewer_person": [
        1
    ],
    "driver_path": "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
    "damai_url": "https://www.damai.cn/",
    "target_url": "https://m.damai.cn/damai/detail/item.html?itemId=708250808776&spm=a2o71.home.snatch_ticket.item&from=appshare&sqm=dianying.h5.unknown.value.hlw_a2o71_28004194",
    "comment": {
        "title": "comment 下的所有内容为自定义注释,无实际含义",
        "date": "日期序号,仅支持一个日期选择",
        "sess": "场次序号,优先选中的场次序号放在前,填写的场次序号若大于实际场次序号,则会选中实际场次序号最大的",
        "price": "票档序号,优先选中的票档序号放在前,填写的票档序号若大于实际票档序号,则会选中实际票档序号最大的",
        "real_name": "实名者序号,已经弃用",
        "nick_name": "用户昵称,已经弃用",
        "ticket_num": "购买票数,购买票数与观影人序号的数量务必一致",
        "viewer_person": "观影人序号(预先添加实名观影人),优先选中的序号放在前,填写的序号若大于实际序号,则会放弃选中",
        "driver_path": "驱动地址",
        "damai_url": "大麦首页地址,用于登录",
        "target_url": "购票的实际地址,需要使用手机端的地址,域名: https://m.damai.cn/ 开头",
        "queue": {
            "title": "列入待抢的链接地址",
            "zhoujielun_0403": "https://m.damai.cn/damai/detail/item.html?itemId=607865020360&from=appshare&sqm=dianying.h5.unknown.value.hlw_a2o71_28004194&prev_page=8hu5vjnq54&spm=a2o71.28004194.785344.item_horizontal_3"
        }
=======
"accounts": {
    "account1": {
        "username": "user1@example.com",
        "password": "password1",
        "target_url": "https://m.damai.cn/",
        "auto_buy_time": "08:30:00"
    },
    "account2": {
        "username": "user2@example.com",
        "password": "password2",
        "target_url": "https://m.taopiaopiao.com/",
        "auto_buy_time": "08:30:00"
>>>>>>> main
    }
}
```
**运行多账户抢票**
在配置完多账户后，您可以通过以下方式启动脚本，以同时使用所有配置好的账户进行抢票：
`python ticket_script.py --multi-account`

脚本将会遍历 accounts 配置中的每个账户，分别登录并尝试抢票。请确保每个账户的配置都是正确的，以避免在抢票过程中出现错误。

>使用多账户抢票时，请确保每个账户都遵守目标平台的使用条款，避免违规操作导致账户被封禁。
>确保每个账户都已经完成了必要的实名认证（如果目标平台要求）。
>根据目标平台的不同，登录方式（扫码、短信验证等）可能会有所不同，请根据实际情况调整账户配置。

### 多账户抢票策略

为了在多个票务平台（如大麦网、淘票票、缤玩岛等）上运行抢票脚本，您需要按照以下步骤进行操作：

1. **配置文件准备**：为每个平台准备一个独立的配置文件，例如`config_damai.json`、`config_taopiaopiao.json`等。
2. **平台特定设置**：在每个配置文件中，设置该平台特定的`target_url`、登录方式等信息。
3. **运行脚本**：在运行时，通过命令行参数`--config`指定要使用的配置文件，例如：`python ticket_script.py --config config_taopiaopiao.json`


   
## 免责声明

详见MIT License

此仓库仅用于个人学习软件界面设计

如他人用本仓库代码用于商业用途，侵犯到大麦网利益等，本人不承担任何责任