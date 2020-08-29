from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse

# Create your views here.
class AreasView(View):
    def get(self, request):
        provinces = Area.objects.filter(parent__isnull=True)

        province_list = []
        for item in provinces:
            province_list.append({
                'id': item.id,
                'name': item.name
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})


class SubAreasView(View):
    def get(self, request, parent_id):
        pass