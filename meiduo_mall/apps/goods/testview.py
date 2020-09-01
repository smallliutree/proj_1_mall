class ListView(View):

    def get(self,request,category_id):
        """
        1.获取分类id
        2.根据分类id查询分类数据
          获取面包屑数据
        3.获取排序和分页数据
        4.查询列表数据
        5.进行分页操作
        6.将分页的对象列表转换为字典列表
        7.返回响应
        :param request:
        :return:
        """
        # 1.获取分类id
        # 2.根据分类id查询分类数据
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类'})
        # 获取面包屑数据
        breadcrumb=get_breadcrumb(category)
        # 3.获取排序和分页数据
        # ordering前端传递的 排序字段 -create_time , price ,-sales
        ordering=request.GET.get('ordering','-create_time')
        # 页码
        page=request.GET.get('page',1)
        # 每页多少条记录
        page_size=request.GET.get('page_size',5)
        # 4.查询列表数据
        skus=SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        # 5.进行分页操作
        from django.core.paginator import Paginator
        # 5.1 创建分页类
        #object_list,       列表数据
        # per_page          每页多少条数据
        paginator=Paginator(skus,per_page=page_size)
        # 5.2 获取分页数据
        # number 页码
        page_sku=paginator.page(page)
        # 5.3 获取分页数
        total_page=paginator.num_pages

        # 6.将分页的对象列表转换为字典列表
        sku_list=[]
        for sku in page_sku:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url,
            })
        # 7.返回响应
        return JsonResponse({
            'code':0,
            'count':total_page,
            'breadcrumb':breadcrumb,
            'list':sku_list
        })