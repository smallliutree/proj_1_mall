from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import pickle, base64, json
# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import SKU


class CartsView(View):

    def post(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        try:
            count = int(count)
        except Exception:
            count = 1

        user = request.user

        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hset('carts_%s' % user.id, sku_id, count)
            redis_cli.sadd('selected_%s' % user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts is None:
                carts = {}
            else:
                carts = pickle.loads(base64.b64decode(cookie_carts))

            if sku_id in carts:
                origin_count = carts[sku_id]['count']
                count += origin_count
            carts[sku_id] = {
                'count': count,
                'selected': True
            }
            carts_bytes = pickle.dumps(carts)
            carts_base64 = base64.b64encode(carts_bytes)
            response = JsonResponse({'code': 0, 'errmsg': '添加成功'})
            response.set_cookie(key='carts', value=carts_base64.decode(), max_age=14 * 24 * 3600)
            return response
