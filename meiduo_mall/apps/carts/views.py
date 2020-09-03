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

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            selected_ids = redis_cli.smembers('selected_%s' % user.id)
            sku_id_counts = redis_cli.hgetall('carts_%s' % user.id)
            carts = {}

            for sku_id, count in sku_id_counts.items():
                carts[sku_id] = {
                    'count': count,
                    'selected': sku_id in selected_ids
                }
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts is not None:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}

        ids = carts.keys()
        skus = SKU.objects.filter(id__in=ids)
        skus_list = []
        for sku in skus:
            skus_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts.get(sku.id).get('count'),
                'selected': str(carts.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts.get(sku.id).get('count')),
            })
        return JsonResponse({'code': 0, 'cart_skus': skus_list, 'errmsg': 'ok'})

    def put(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')

        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
            # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '商品sku_id不存在'})
            # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return JsonResponse({'code': 400, 'errmsg': '参数count有误'})

        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                redis_cli.sadd('selected_%s' % user.id, sku_id)
            else:
                redis_cli.srem('selected_%s' % user.id, sku_id)

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return JsonResponse({'code': 0, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart is not None:
                carts = pickle.loads(base64.b64decode(cookie_cart))
            else:
                carts = {}

            if sku_id in carts:
                carts[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            base64_cart = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code': 0, 'count':count})
            response.set_cookie('carts', base64_cart.decode(), max_age=14 * 24 * 3600)

            return response

    def delete(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')

        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hdel('carts_%s' % user.id,sku_id)
            redis_cli.srem('selected_%s' % user.id, sku_id)
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            cookie_cart = request.COOKIES.get('carts')
            if cookie_cart is not None:
                carts = pickle.loads(base64.b64decode(cookie_cart))
            else:
                carts = {}
            if sku_id in carts:
                del carts[sku_id]
            base64_carts = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', base64_carts.decode(), max_age=14 * 24 * 3600)
            return response
