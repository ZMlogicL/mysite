from django.shortcuts import render, redirect
from . import models
# Create your views here.
from . import form
import datetime
from . import conf_t as ct
from django.conf import settings


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    # 使用session判断是否登录
    # if request.session.get('is_login', None):
    #     return redirect('/index/')
    if request.method == 'POST':
        login_form = form.UserForm(request.POST)
        # username = request.POST.get('username')

        if login_form.is_valid():
            print("1")
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            # 验证用户输入是否合法
            # 验证用户是否存在
            try:
                user = models.User.objects.get(name=username)
            except:
                message = "该用户不存在！"
                return render(request, 'login/login.html',locals())

            if not user.has_confirmed:
                message = '该用户还未邮件确认'
                return render(request, 'login/login.html', locals())

            if user.password == ct.hash_code(password):
                # 设置session
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = "密码不正确!"
                return render(request, 'login/login.html', locals())
        else:
            message = "请正确填写内容!"
            return render(request, 'login/login.html', locals())
    login_form = form.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = form.RegisterForm(request.POST)
        message = "请填写正确内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            print(email)
            sex = register_form.cleaned_data.get('sex')

            if password1!=password2:
                message = '两次输入密码不一致！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在！'
                    return render(request, 'login/register.html', locals())
                same_eamil_user = models.User.objects.filter(email=email)
                if same_eamil_user:
                    message = '该邮箱已被注册！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = ct.hash_code(password2)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = ct.make_comfirm_string(new_user)
                ct.send_email(email, code)

                return redirect('/login/')
        else:
            return  render(request, 'login/register.html', locals())
    register_form = form.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果没有登录，返回首页
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求！'
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now>c_time+datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '你的邮件已经过期！请重新注册'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
