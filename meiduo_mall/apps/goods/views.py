from django.shortcuts import render
from fdfs_client.client import Fdfs_client
from django.views import View
from utils.goods import get_breadcrumb
from apps.goods.models import GoodsCategory, SKU
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
from apps.contents.models import ContentCategory
from utils.goods import get_categories

client = Fdfs_client('utils/fastdfs/client.conf')
client.upload_by_filename('/home/ubuntu/Desktop/0.png')


class IndexView(View):
    def get(self, request):

        contents = {}
        categories = get_categories()
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context=context)


class ListView(View):
    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此分类'})

        breadcrumb = get_breadcrumb(category)

        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)
        ordering = request.GET.get('ordering', '-create_time')

        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)

        paginator = Paginator(skus, per_page=page_size)
        page_sku = paginator.page(page)
        total_count = paginator.num_pages

        sku_list = []
        for sku in page_sku:
            sku_list.append({
                'id':sku.id,
                'default_image_url':sku.default_image.url,
                'name':sku.name,
                'price':sku.price
            })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'breadcrumb': breadcrumb,
            'list': sku_list,
            'count': total_count
        })


class HotView(View):
    def get(self, request, category_id):

        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[0 : 2]
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return JsonResponse({'code':0, 'errmsg':'OK', 'hot_skus':hot_skus})


class DetailView(View):

    def get(self, request, sku_id):

        context = {

        }
        return render(request, 'detail.html', context=context)
