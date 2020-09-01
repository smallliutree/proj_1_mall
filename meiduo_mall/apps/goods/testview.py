class DetailView(View):

    def get(self,request,sku_id):
        """
        1.分类数据
        2.面包屑数据
        3.商品信息
        4.规格信息
        :param request:
        :param sku_id:
        :return:
        """
        # 1.商品信息
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
        # 2.分类数据
        categories=get_categories()
        # 3.面包屑数据
        breadcrumb=get_breadcrumb(sku.category)
        # 4.规格信息
        specs = get_goods_specs(sku)

        #
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': specs,
        }

        return render(request,'detail.html',context=context)