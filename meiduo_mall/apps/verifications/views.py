from django.shortcuts import render

# Create your views here.
from django.views import View
from libs.captcha.captcha import captcha
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from random import randint
from libs.yuntongxun.sms import CCP


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('code')
        redis_conn.setex(uuid, 300, text)

        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        uuid = request.GET.get('image_code_id')
        user_text = request.GET.get('image_code')
        if not all([uuid, user_text]):
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        redis_conn = get_redis_connection('code')
        redis_text = redis_conn.get(uuid)
        if redis_text is None:
            return JsonResponse({'code': 400, 'errmsg': '图形验证码失效'})
        if redis_text.decode().lower() != user_text.lower():
            return JsonResponse({'code': 400, 'errmsg': '输入图形验证码有误'})
        redis_conn.delete(uuid)

        sms_code = '%06d' % randint(0, 999999)
        redis_conn.setex(mobile, 300, sms_code)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        return JsonResponse({'code': 0, 'errmsg': '发送短信成功'})