from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTING_MODULE", "axfxk.settings")
#实例化celery
app = Celery(__name__)

app.conf.timezone = "Asia/Shanghai"

#指定celery的配置来源 用的是项目的配置文件settings.py
app.config_from_object("django.conf:settings")

#让celery 自动去发现我们的任务（task）
app.autodiscover_tasks(lambda : settings.INSTALLED_APPS) #你需要在app目录下 新