from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render

from apps.goods.models import SKU
from apps.users.models import Address
# Create your views here.
from django.views import View
from django_redis import get_redis_connection


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

