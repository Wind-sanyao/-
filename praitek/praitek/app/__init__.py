# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
这个包里不能导入项目内其他任何包里内容，不然很容易发生循环引用
"""
import json
import logging
import os
import sys
from contextlib import contextmanager
from datetime import timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Union

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy


class SQLAlchemy(BaseSQLAlchemy):
    """
    自定义SQLAlchemy类，扩展了自动提交功能
    """
    @contextmanager
    def auto_commit_db(self):
        """
        数据库自动提交上下文管理器
        在上下文中执行数据库操作，成功则自动提交，失败则回滚
        """
        try:
            yield
            self.session.commit()
        except Exception as e:
            log.error(e)
            self.session.rollback()
            raise e


def get_app_conf_value(key: str, section: str = None,
                       default: Union[str, int, float, bool, None] = None) -> Union[str, int, float, bool, None]:
    """
    获取配置文件的值
    :param key: 配置项名称
    :param section: 配置节名称（可选）
    :param default: 默认值（当配置项不存在时返回）
    :return: 配置值或默认值
    """
    if section is None:
        return app.config.get(key, default)
    return app.config.get(section, {}).get(key, default)


# 创建Flask应用实例
app = Flask('praitek', static_folder='../static', static_url_path='/static')
app.config['port'] = 8001

# 日志配置
logPath = "c:/ProgramData/Promise/praitek/"
if not os.path.exists(logPath):
    os.makedirs(logPath)
file_handler = TimedRotatingFileHandler(os.path.join(logPath, "praitek.log"), when="D", interval=1,
                                        backupCount=15, encoding="UTF-8", delay=False)
logger_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(thread)d - %(message)s')
file_handler.setFormatter(logger_format)
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.DEBUG)
app.logger.addHandler(console_handler)

app.logger.setLevel(logging.DEBUG)

log = app.logger
log.info('log start')

# JWT配置
app.config["JWT_SECRET_KEY"] = "promisetek"  # JWT密钥
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # 访问令牌有效期1小时
JWTManager(app)

# 初始化数据库实例
db = SQLAlchemy()

# 添加应用上下文
app.app_context().push()


# 加载自定义配置
def get_config_path() -> str:
    """
    获取配置文件路径
    :return: 配置文件所在目录路径
    """
    return "c:/ProgramData/Promise/praitek"


def __get_config_file() -> str:
    """
    获取配置文件的完整路径
    优先从系统目录加载，如果不存在则从项目根目录加载
    :return: 配置文件的完整路径
    """
    config_path = os.path.join(get_config_path(), 'config.json')
    if os.path.exists(config_path):
        return config_path
    else:
        return 'config.json'


# 加载配置文件
__cfg_file = __get_config_file()
print(f'loading config from {__cfg_file}')
app.config.from_file(__cfg_file, load=json.load, silent=False, text=False)

# 创建人脸图片存储目录
face_path = os.path.join(str(get_app_conf_value('IMAGE_FOLDER')), 'FACES')
if not os.path.exists(face_path):
    os.makedirs(face_path)
app.config["IMAGE_FACE_FOLDER"] = face_path

# 初始化数据库
db.init_app(app)
