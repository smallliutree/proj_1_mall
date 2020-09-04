import base64
import pickle
from django_redis import get_redis_connection

def merge_cookie_to_redis(request, response):
    cookie_cart = request.COOKIES.get('carts')
    if cookie_cart is not None:
        carts = pickle.loads(base64.b64decode(cookie_cart))
        new_carts = {}
        selected_ids = []
        unselected_ids = []
        for sku_id, count_selected_dict in carts.items():
            new_carts[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)

        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()
        pipeline.hmset('carts_%s' % request.user.id, new_carts)
        if len(selected_ids) > 0:
            pipeline.sadd('selected_%s' % request.user.id, *selected_ids)
        if len(unselected_ids) > 0:
            pipeline.srem('selected_%s' % request.user.id, *unselected_ids)

        pipeline.execute()
        response.delete_cookie('carts')

        return response
