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
        # subs = Area.objects.filter(parent=parent_id)
        # 1
        parent_area = Area.objects.get(id=parent_id)
        subs = parent_area.subs.all()

        sub_list = []
        for item in subs:
            sub_list.append({
                'id': item.id,
                'name': item.name
            })

        sub_data = {
            'id': parent_area.id,
            'name': parent_area.name,
            'subs': sub_list
        }

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'sub_data': sub_data})