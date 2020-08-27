from django.shortcuts import render

# Create your views here.
from django.views import View
from libs.captcha.captcha import captcha
from django.http import HttpResponse
from django_redis import get_redis_connection


class ImageCodeView(View):
    def get(self, request, key):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s' % key, 300, text)

        return HttpResponse(image, content_type='image/jpeg')