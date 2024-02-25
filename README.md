# 大麦抢票脚本 V2.1

最强大麦抢票脚本 

##  更新记录

增加选座购买，暂时只支持抢购指定价格下的座位，且暂不支持连坐购买。

## 功能介绍

之前的版本通过按钮操作，还要等待页面元素加载，效率低下。 此版本仅需登录时用到页面，通过selenium打开页面进行登录。其余操作均通过requests进行请求。

## 配置文件

```json
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
        2
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
    }
}

```

## 注意事项
1. 账号必须先做好实名制认证，并添加至少一个实名制的人的信息
2. 第一次打开后会进入登录页面，需要手动选择扫码登陆
3. 如果太久没用，需要先清空目录下的 cookie 文件，然后在重新登录

# 使用说明
1. 安装所需要的环境
2. 需要下载与系统安装对应的ChromeDriver驱动并配置(也可以改用其他浏览器驱动)
> 下载地址: http://chromedriver.storage.googleapis.com/index.html
3. 初次登陆没有cookies，默认登录方式为账号密码登录方式，可改成其他方式进行登录，如扫码或短信登录。

免责声明：详见MIT License，此仓库仅用于个人参考学习，但如他人用本仓库代码用于商业用途(鄙视黄牛)，侵犯到大麦网利益等，本人不承担任何责任。
