from django.shortcuts import render
from fdfs_client.client import Fdfs_client
from django.views import View

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