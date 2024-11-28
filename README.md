# 短剧微信群机器人

> 一个基于微信群的短剧机器人, 用于搜索指定抖音话题的热度数据, 并通知到微信群中。

## 功能
- [x] 搜索指定话题的热度数据
- [x] 多个微信群独立管理
- [x] 支持多个超级管理员
- [x] 支持自定义指令
- [x] 接入 [硅基流动](https://cloud.siliconflow.cn/i/NO6ShUc3) 以实现数据预测模块
- [x] 接入飞书文档 API, 以便采集飞书文档表格数据
- [x] 支持多消息队列任务处理, 以实现多任务并发处理
- [x] 支持动态授权群并设置管理员
- [x] 支持每个群设置有效期, 到期后机器人将无法使用


### 普通指令
1. 话题列表 - 查看当前启用的话题列表
2. 全部话题列表 - 返回全部话题列表
3. 话题详情 - 例: 话题详情1
4. 添加话题 - 例: 添加话题小当家
5. 话题启用 - 例: 话题启用1
6. 话题禁用 - 例: 话题禁用1
7. 话题删除 - 例: 话题删除1
8. 批量禁用话题 - 例: 批量禁用话题1,2,3
9. 批量删除话题 - 例: 批量删除话题1,2,3
10. 删除全部话题 - 此操作不可逆, 请谨慎操作
11. 话题搜索 - 例: 话题搜索婚姻的轨道
12. 话题趋势 - 例: 话题趋势1
13. 话题预测 - 例: 话题预测1
14. 同步喜乐短剧 - 自动同步当天飞书文档的短剧内容
15. 视频解析 - 发送抖音视频地址, 返回无水印下载地址
16. 搜索短剧 - 例: 搜索短剧婚姻的轨道
17. 帮助 - 显示所有可用命令
18. 管理员指令 - 显示管理员可用的命令

### 管理员指令
1. 通知所有人 - 机器人必需是管理员
2. 授权此群 - 必须是超级管理员执行的命令
3. 设置有效期 - 设置群有效时间(月)
4. 设置管理员 - 给指定群设置管理
5. 设置最小热度值 - 设置通知最小热度值, 大于此值才会通知
6. 启用机器人 - 启用机器人
7. 禁用机器人 - 禁用机器人

## 如何使用

### 环境
- Python 3.9
- MySQL 5.7

### 导入数据库
[db.sql](db.sql) 文件中包含了数据库结构, 导入到你的数据库中即可。

### 下载字体

Ubuntu/Debian:

```shell
apt-get install fonts-wqy-microhei

# 安装文泉驿微米黑字体
sudo apt-get update
sudo apt-get install -y fonts-wqy-microhei

# 或者安装更多中文字体
sudo apt-get install -y fonts-wqy-zenhei ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy
```

CentOS:

```shell
yum install wqy-microhei-fonts
```

### 微信机器人 hooks

参考： [wxbot](https://github.com/RipperTs/wxbot) 项目， 目前接口均是对接此项目。

### 安装依赖

```shell
pip install -r requirements.txt
```

完成以上步骤后, 运行程序后将下面接口注册到 **wxbot** http 回调中 (注意替换自己的 ip 和端口).
```shell
curl --location --request POST 'http://127.0.0.1:8080/api/sync-url' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "http://127.0.0.1:12300/api/robot-msg",
    "timeout": 3000,
    "type": "general-msg"
}'
```

### 配置文件
[.env.example](.env.example) 文件中包含了所有配置项, 请将其复制一份并命名为 `.env` 并修改其中的配置项。

### 如何定时通知

每间隔 x 分钟自行运行 [data_acquisition.py](data_acquisition.py) 此脚本即可, 可以将其添加到 crontab 中。   
示例: 每 5 分钟运行一次   
```shell
*/5 * * * * python3 /path/to/data_acquisition.py
```

### 如何注册新指令
查看 [__init__.py](commands/__init__.py) 中注册新指令即可。   

如果你注册的新指令不希望出现在帮助列表中, 可以在 [__init__.py](commands/__init__.py) 中添加 `hidden=True` 参数。      

如果你需要注册管理员指令, 可以在 [__init__.py](commands/__init__.py) 中添加 `is_admin=True` 参数。   


## 其他
- 仅用于学习交流，禁止用于商业用途。
- 项目基于 `MIT` 协议发布，你可以修改，但请保留原作者信息。
- 有任何问题可以提交 `Issue` 给我，欢迎 PR。