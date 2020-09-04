from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
import json
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

class OrderSettlementView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(user=user, is_delete=False)
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        redis_cli = get_redis_connection('carts')
        sku_id_count = redis_cli.hgetall('carts_%s' % user.id)

        redis_carts = {}
        for sku_id, count in sku_id_count.items():
            redis_carts[int(sku_id)] = int(count)
        selected_ids = redis_cli.smembers('selected_%s' % user.id)
        skus = []
        for sku_id in selected_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(sku_id_count[sku_id]),
                'price': sku.price
            })
        context = {
            'addresses': address_list,
            'skus': skus,
            'freight': 10  # 运费
        }
        return JsonResponse({'code': 0, 'context': context, 'errmsg': 'ok'})


class CommentView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        if not all([address_id, pay_method]):
            return JsonResponse({'code':400,'errmsg':'参数错误'})

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})

        if pay_method not in [1, 2]:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})

        user = request.user
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S')+'%09d'%user.id

        freight = Decimal('10')
        total_price = Decimal('0')
        total_count = 0
        if pay_method == 1:
            status = 2
        else:
            status = 1
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=total_count,
            total_amount=total_price,
            freight=freight,
            pay_method=pay_method,
            status=status
        )

        redis_cli = get_redis_connection('carts')
        sku_id_count = redis_cli.hgetall('carts_%s' % user.id)
        selected_ids = redis_cli.smembers('selected_%s' % user.id)
        selected_carts = {}

        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_count[sku_id])

        ids = selected_carts.keys()
        for id in ids:
            sku = SKU.objects.get(id=id)
            custom_count = selected_carts[id]
            if custom_count > sku.stock:
                return JsonResponse({'code':400,'errmsg':'购买量太大，库存不足'})
            sku.stock -= custom_count
            sku.sales += custom_count
            sku.save()
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=custom_count,
                price=sku.price
            )
            order.total_count += custom_count
            order.total_amount += (custom_count * sku.price)
        order.save()

        return JsonResponse({'code':0,'order_id':order.order_id,'errmsg':'ok'})
