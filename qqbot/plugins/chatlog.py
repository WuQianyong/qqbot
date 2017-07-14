#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : chatlog
# Fatures:
# Author : qianyong
# Time   : 2017/7/4 14:38
# Version: V0.0.1
#

# -*- coding: utf-8 -*-
import pymysql
import datetime
import os
# 如果不希望加载本插件，可以在配置文件中的 plugins 选项中删除 qqbot.plugins.chatlog
from qqbot.utf8logger import DEBUG, INFO, ERROR, WARN

from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import requests
from urllib.parse import unquote, quote


def _conn(db, only=None):
    engine_str = 'mysql+pymysql://{}:{}@{}/{}?charset={}'.format(db.get('user'),
                                                                 db.get('pwd'),
                                                                 db.get('host'),
                                                                 db.get('db'),
                                                                 db.get('charset'))

    engine = create_engine(engine_str)
    if only is None:
        base = automap_base()
        base.prepare(engine, reflect=True)
    else:
        metadata = MetaData()
        metadata.reflect(engine, only=only)
        base = automap_base(metadata=metadata)
        base.prepare()

    # 创建数据会话
    session = Session(engine)

    return session, base


def conn_orm(DB, TABLENAME):
    session_dict, base_dict = {}, {}
    for key in DB.keys():
        # print()
        session, base = _conn(DB.get(key), TABLENAME.get(key))
        session_dict[key] = session
        base_dict[key] = base
    return session_dict, base_dict


inner_group_name = {}
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}


def onInit(bot):
    # 初始化时被调用
    # 注意 : 此时 bot 尚未启动，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    DEBUG('ON-INIT : qqbot.plugins.sampleslots')
    # 链接mysql,获取内部群
    db = {'host': '54.223.109.46:3306',
          'user': 'zhanghongjie',
          'pwd': 'WJBC#FavIaj1kL6Q',
          'db': 'qqrobot',
          'charset': 'utf8'}
    session, base = _conn(db, only=['sys_config'])
    a = base.classes['sys_config']
    list_a = list(session.query(a.val))
    # print(list_a)
    h_key = list_a[1][0].split(',')
    s_key = list_a[2][0].split(',')
    inner_group_name['h_key'] = h_key
    inner_group_name['s_key'] = s_key
    INFO('内部化工群： {}'.format(h_key))
    INFO('内部塑料群： {}'.format(s_key))


def onQrcode(bot, pngPath, pngContent):
    # 获取到二维码时被调用
    # 注意 : 此时 bot 尚未启动，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    # pngPath : 二维码图片路径
    # pngContent : 二维码图片内容
    DEBUG('ON-QRCODE: %s (%d bytes)', pngPath, len(pngContent))


def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # contact : QContact 对象，消息的发送者
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
    qq = bot.conf.qq
    if contact.ctype == 'group':
        print(qq)
        # print(bot.qq)
        # # 从 sqlite3 数据库查询 group 的 qq 号 和 group_member 的qq 号
        # dbname = '%s-contact.db' % (self.conf.qq)
        # dbdatabase = os.path.join(os.path.expanduser('~'), '.qqbot-tmp', dbname)  # sqlite3 的路径
        #
        # demo = ContactDB(dbname=dbdatabase)
        # group_qq = demo.select('group', 'uin', fromUin)[0][0]
        # # INFO('qq group: {}'.format(group_qq))
        # # INFO('qq group type: {}'.format(type(group_qq)))
        # table_name = 'group_member_{}'.format(fromUin)
        # meb_qq = demo.select(table_name, 'uin', membUin)[0][0]
        #
        # qq_date = time.strftime("%Y-%m-%d", time.localtime())
        # # id = get_md5('{}{}'.format(content, qq_date))
        # INFO(contact)
        # INFO(str(member))
        # g = str(contact)
        # m = str(member)
        # INFO(type(g))
        # INFO(type(m))
        # groupname = re.findall('\“(.*?)\”', g)[0]
        # qq_nick = re.findall('\“(.*?)\”', m)[0]
        #
        # 判断是内部化工群-h 、内部塑料群-s 还是外部群-o
        groupname = contact.name
        if groupname in inner_group_name['h_key']:
            type_check = 'h'
            INFO('群 {} 是内部化工群'.format(groupname))
        elif groupname in inner_group_name['s_key']:
            type_check = 's'
            INFO('群 {} 是内部塑料群'.format(groupname))
        else:
            type_check = 'o'
            INFO('群 {} 是外部群'.format(groupname))
        now = datetime.datetime.now()
        qq_date = now.strftime('%Y-%m-%d %H:%M:%S')
        data = {
            "currentqq": qq,
            "groupname": groupname,
            "gid": contact.qq,
            "fromqqnick": member.name,
            "fromqq": member.qq,
            "id2": "123456145648451",
            "date": qq_date,
            "content": content,
            "type": 2,
            "pass": "hsh@1234",
            "type_check": type_check
        }
        ### 开始保存数据
        if member.qq == '#NULL' or member.qq == '#NULL':
            WARN('缺少meb_qq(fromqq) 或者 group_qq(gid)')
        else:
            # sutao.post(data)
            tail = quote('{}'.format(data))

            # 用Java 那边配合 api
            # url = 'http://192.168.4.168:8080/hsh-qq/api/qqrobot/saveSolrMsg?contentJson={}&typeCheck={}'.format(tail,data.pop('type_check'))
            url = 'http://hshqq.huasuhui.com:8380/hsh-qq/api/qqrobot/saveSolrMsg?contentJson={}&typeCheck={}'.format(tail,
                                                                                                                     data.pop(
                                                                                                                         'type_check'))

            print('数据 导入 接口  {}'.format(data))
            try:
                requests.get(url, timeout=30)
            except Exception as e:
                ERROR('{} 无法存储 ，超时，{}'.format(data, e))

        # ### 开始保存数据
        # if meb_qq == '#NULL' or group_qq == '#NULL':
        #     WARN('缺少meb_qq(fromqq) 或者 group_qq(gid)')
        # else:
        #     sutao.post(data)
        insertChatContent(bot, contact, member, content)


def onInterval(bot):
    # 每隔 5 分钟被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('INTERVAL')


def onStartupComplete(bot):
    # 启动完成时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('START-UP-COMPLETE')


def onUpdate(bot, tinfo):
    # 某个联系人列表更新时被调用
    # bot : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # tinfo : 联系人列表的代号，详见文档中关于 bot.List 的第一个参数的含义解释
    DEBUG('ON-UPDATE: %s', tinfo)


def onPlug(bot):
    # 本插件被加载时被调用，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # 提醒：如果本插件设置为启动时自动加载，则本函数将延迟到登录完成后被调用
    # bot ： QQBot 对象
    DEBUG('ON-PLUG : qqbot.plugins.sampleslots')


def onUnplug(bot):
    # 本插件被卸载时被调用
    # bot ： QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    DEBUG('ON-UNPLUG : qqbot.plugins.sampleslots')


def onExpire(bot):
    # 登录过期时被调用
    # 注意 : 此时登录已过期，因此请勿在本函数中调用 bot.List/SendTo/GroupXXX/Stop/Restart 等接口
    #       只可以访问配置信息 bot.conf
    # bot : QQBot 对象
    DEBUG('ON-EXPIRE')


def insertChatContent(bot, contact, member, content):
    try:
        # 连接数据库
        connect = pymysql.Connect(
            host='localhost',
            port=3306,
            user='yong',
            passwd='19950105',
            db='qq_data',
            charset='utf8'
        )

        # 获取游标
        cursor = connect.cursor()
        now = datetime.datetime.now()
        createtime = now.strftime('%Y-%m-%d %H:%M:%S')
        # 插入数据
        sql = "INSERT INTO chat_logs (group_number,group_name,qq,nickname,mark,content,create_time) VALUES ( '%s', '%s', '%s','%s','%s', '%s', '%s')"
        name = pymysql.escape_string(contact.name)
        nickname = pymysql.escape_string(member.name)
        mark = pymysql.escape_string(member.name)
        data = (contact.qq, name, member.qq, nickname, mark, content, createtime)
        print('聊天数据 {}'.format(data))
        cursor.execute(sql % data)
        connect.commit()
        connect.close()
        print('insert success', cursor.rowcount, ' record')
    except Exception as e:
        ERROR('存储mysql 失败 原因是： {}'.format(e))
