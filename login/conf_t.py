import datetime
import hashlib
from . import views
from django.conf import settings


def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def make_comfirm_string(user):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code = hash_code(user.name, now)
    views.models.ConfirmString.objects.create(code=code, user=user,)

    return code


def send_email(email, code):
    from django.core.mail import  EmailMultiAlternatives

    subject = '来自127.0.0.1:8000的注册确认邮件'

    text_content = '感谢您注册127.0.0.1:8000网站'

    html_content = '''
            <p>感谢注册<a href = 'http://{}/confirm/?code={}' target=blank>www.lzm.com</a></p>
            <p>点这个连接确认注册</p>
            <p>有效期为{}天！</p>
    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content,settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

