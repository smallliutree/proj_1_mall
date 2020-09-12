def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }

from rest_framework.pagination import PageNumberPagination


class NumPage(PageNumberPagination):
    """
        /meiduo_admin/users/?page=1&pagesize=10&keyword=
    """
    # 指定页容量参数  page=1&pagesize=10 第一页的10条数据
    page_size_query_param = 'pagesize'
    # 指定每页最大返回数量
    max_page_size = 10