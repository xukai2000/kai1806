import hashlib
from celery import task
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template import loader
from django.views.decorators.csrf import csrf_exempt


from myaxf.my_utils import get_uuique_str


@task
@csrf_exempt
def send_verify_mail(url,user_id,reciever):

    title="红浪漫"
    content=""
    #加载
    template=loader.get_template("user/email.html")
    html=template.render({"url":url})
    email_from=settings.DEFAULT_FROM_EMAIL
    send_mail(title,content,email_from,[reciever],html_message=html)
    #设置缓存
    cache.set(url.split("/")[-1],user_id,settings.VERIFY_CODE_MAX_AGE)