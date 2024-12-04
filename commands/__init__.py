from commands.feishu_command import FeiShuCommand
from commands.room_command import RoomCommand
from commands.system_command import SystemCommand
from commands.topic_command import TopicCommand
from dto.command_dto import Command

system_command = SystemCommand()
topic_command = TopicCommand()
feishu_command = FeiShuCommand()
room_command = RoomCommand()


def register_commands():
    """
    注册命令
    :return:
    """
    commands = [
        Command(
            prefixes=("话题列表", "话题清单"),
            handler=topic_command.topic_list,
            require_content=False,  # 是否需要内容
            description="查看当前启用的话题列表"
        ),
        Command(
            prefixes=("全部话题列表",),
            handler=topic_command.topic_list_all,
            require_content=False,
            description="返回全部话题列表"
        ),
        Command(
            prefixes=("话题详情",),
            handler=topic_command.topic_detail,
            description="例: 话题详情1"
        ),
        Command(
            prefixes=("添加话题", "添加短剧"),
            handler=topic_command.add_topic,
            description="例: 添加话题小当家"
        ),
        Command(
            prefixes=("话题启用", "启用话题"),
            handler=topic_command.enable_topic,
            description="例: 话题启用1"
        ),
        Command(
            prefixes=("话题禁用", "禁用话题"),
            handler=topic_command.disable_topic,
            description="例: 话题禁用1"
        ),
        Command(
            prefixes=("话题删除", "删除话题"),
            handler=topic_command.delete_topic,
            description="例: 话题删除1"
        ),
        Command(
            prefixes=("批量禁用话题", "批量话题禁用"),
            handler=topic_command.disable_topics,
            description="例: 批量禁用话题1,2,3"
        ),
        Command(
            prefixes=("批量删除话题", "批量话题删除"),
            handler=topic_command.delete_topics,
            description="例: 批量删除话题1,2,3"
        ),
        Command(
            prefixes=("删除全部话题", "清空所有话题"),
            handler=topic_command.del_topic_all,
            require_content=False,
            description="此操作不可逆, 请谨慎操作"
        ),
        Command(
            prefixes=("话题搜索", "搜索话题"),
            handler=topic_command.search_topic,
            description="例: 话题搜索婚姻的轨道"
        ),
        Command(
            prefixes=("话题趋势", "趋势图"),
            handler=topic_command.topic_trends,
            description="例: 话题趋势1"
        ),
        Command(
            prefixes=("话题预测", "预测话题"),
            handler=topic_command.topic_prediction,
            description="例: 话题预测1"
        ),
        Command(
            prefixes=("同步喜乐短剧",),
            handler=feishu_command.sync_topic,
            require_content=False,  # 是否需要内容
            description="自动同步当天飞书文档的短剧内容"
        ),
        Command(
            prefixes=("视频解析", "解析视频"),
            handler=system_command.video_parse,
            description="发送抖音视频地址, 返回无水印下载地址"
        ),
        Command(
            prefixes=("搜索短剧", "短剧搜索", "搜剧"),
            handler=system_command.search_dj,
            description="例: 搜索短剧婚姻的轨道"
        ),
        Command(
            prefixes=("通知所有人", "通知全体成员"),
            handler=room_command.notify_all,
            description="机器人必需是管理员",
            is_admin=True
        ),
        Command(
            prefixes=("授权此群",),
            handler=room_command.authorize_room,
            description="必须是超级管理员执行的命令",
            require_content=False,  # 是否需要内容
            is_admin=True
        ),
        Command(
            prefixes=("设置有效期",),
            handler=room_command.update_expire_time,
            description="设置群有效时间(月)",
            is_admin=True
        ),
        Command(
            prefixes=("设置管理员",),
            handler=room_command.setting_admin_account,
            description="给指定群设置管理",
            is_admin=True
        ),
        Command(
            prefixes=("设置同步间隔",),
            handler=room_command.set_sync_time,
            description="话题同步间隔时间(分钟)",
            is_admin=True
        ),
        Command(
            prefixes=("设置最小热度值",),
            handler=room_command.set_min_heat,
            description="设置通知最小热度值, 大于此值才会通知",
            is_admin=True
        ),
        Command(
            prefixes=("启用机器人",),
            handler=room_command.enable_robot,
            description="启用机器人",
            require_content=False,
            is_admin=True
        ),
        Command(
            prefixes=("禁用机器人",),
            handler=room_command.disable_robot,
            description="禁用机器人",
            require_content=False,
            is_admin=True
        ),
    ]

    return commands
