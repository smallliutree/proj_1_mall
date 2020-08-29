from django.core.mail import send_mail
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User
from django.http import JsonResponse
import json
from django import http
import re
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin

class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


class RegisterView(View):

    def post(self, request):
        body_str = request.body.decode()
        body_dict = json.loads(body_str)

        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数!'})
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.JsonResponse({'code': 400, 'errmsg': 'username格式有误!'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})
        # 判断两次密码是否一致
        if password != password2:
            return http.JsonResponse({'code': 400, 'errmsg': '两次输入不对!'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': 'mobile格式有误!'})
        # 判断是否勾选用户协议
        if allow != True:
            return http.JsonResponse({'code': 400, 'errmsg': 'allow格式有误!'})

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)  # sms_code_server是bytes
        # 判断短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码失效'})
        # 对比用户输入的和服务端存储的短信验证码是否一致
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})

        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': '注册失败!'})

        login(request, user)

        return http.JsonResponse({'code': 0, 'errmsg': '注册成功!'})


class LoginView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remembered')

        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        if re.match('^1[3-9]\d{9}$', username):
            # 手机号
            User.USERNAME_FIELD = 'mobile'
        else:
            # account 是用户名
            # 根据用户名从数据库获取 user 对象返回.
            User.USERNAME_FIELD = 'username'

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码不正确'})

        login(request, user)

        if remember:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})

        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        # 获取界面需要的数据,进行拼接
        info_data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})


class EmailView(View):
    def put(self, request):
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not email:
            return JsonResponse({'code': 400, 'errmsg': '缺少email参数'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '参数email有误'})

        try:
            request.user.email = email
            request.user.save()

            # subject = 'asd'
            # message = ''
            # from_email = 'qi_rui_hua@163.com'
            # recipient_list = [email]
            #
            # from apps.users.utils import generic_email_access_token
            # access_token = generic_email_access_token(request.user.id, email)
            #
            # verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % access_token
            # html_message = '<p>尊敬的用户您好！</p>' \
            #                '<p>感谢您使用美多商城。</p>' \
            #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
            #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
            # send_mail(subject, message, from_email, recipient_list, html_message=html_message)
            # asd

            from apps.users.utils import generic_email_access_token
            access_token = generic_email_access_token(request.user.id, email)

            from celery_tasks.email.tasks import celery_send_mail
            celery_send_mail.delay(email, access_token)

            return JsonResponse({'code': 0, 'errmsg': 'success'})
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '添加邮箱失败'})
