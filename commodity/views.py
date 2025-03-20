import json
from django.db.models import F, Min, Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Types, CommodityInfos


class commodityView(APIView):
    '''
    Product listing page
    '''
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # Get request parameters
        types = request.GET.get('types', '')
        search = request.GET.get('search', '')
        sort = request.GET.get('sort', 'sold')
        context = {'state': 'success', 'msg': 'Data retrieved successfully', 'data': {}}
        context['data']['types'] = []

        # Get all first-level categories and corresponding second-level categories
        firsts = Types.objects.values_list('firsts', flat=True).distinct()
        for f in firsts:
            t = Types.objects.filter(firsts=f).values_list('seconds', flat=True).all()
            context['data']['types'].append(dict(name=f, value=t))

        # Product query and filtering
        cf = CommodityInfos.objects.all()

        if types:
            # Split type string for search
            if ' - ' in types:
                first_cat, second_cat = types.split(' - ', 1)
                cf = cf.filter(product_type__firsts=first_cat, product_type__seconds=second_cat)
            else:
                cf = cf.filter(product_type__firsts=types)

        if sort:
            cf = cf.order_by('-' + sort)
        if search:
            cf = cf.filter(name__contains=search)
        count = cf.count()

        # Paginated query
        pg = PageNumberPagination()
        p = pg.paginate_queryset(queryset=cf, request=request)

        # Pass paginated data to serializer to generate JSON data object
        c = CommodityInfosListSerializer(instance=p, many=True)

        # Get previous page, next page and total page count
        pageCount = pg.page.paginator.num_pages
        try:
            next = pg.page.next_page_number()
        except:
            next = pageCount
        try:
            previous = pg.page.previous_page_number()
        except:
            previous = 0
        d = dict(data=c.data, previous=previous,
                 next=next, count=count, pageCount=pageCount)
        context['data']['commodityInfos'] = d
        return Response(context)


class detailView(APIView):
    '''
    Product detail page
    '''
    authentication_classes = []
    permission_classes = []

    def get(self, request, id):
        context = {'state': 'success', 'msg': 'Data retrieved successfully', 'data': {}}

        c = CommodityInfos.objects.filter(id=id).first()

        if not c:
            context = {'state': 'fail', 'msg': 'Product not found', 'data': {}}
            return Response(context)

        # Use detail serializer, including full specification info
        context['data']['commoditys'] = CommodityInfosDetailSerializer(instance=c).data

        # Get recommended products (top 5 by sales excluding current product)
        r = CommodityInfos.objects.exclude(id=id).order_by('-sold')[:5]
        context['data']['recommend'] = CommodityInfosListSerializer(instance=r, many=True).data

        # Check if user has already collected this product
        if id in request.session.get('likes', []):
            context['data']['likes'] = True
        else:
            context['data']['likes'] = False

        return Response(context)


class collectView(APIView):
    '''
    Product collection/favorite
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        json_str = json.loads(request.body.decode())
        id = json_str.get('id', '')
        context = {'state': 'fail', 'msg': 'Collection failed'}
        likes = request.session.get('likes', [])

        # If product ID is valid and user hasn't collected this product before
        if id and not int(id) in likes:
            # Increment the collection count of the product by 1
            CommodityInfos.objects.filter(id=id).update(likes=F('likes') + 1)

            # Update session to include this product in user's collection
            request.session['likes'] = likes + [int(id)]
            context = {'state': 'success', 'msg': 'Collection successful'}
        return Response(context)


# Add route for handling second-level categories
@require_GET
def get_second_categories(request):
    """
    Get second-level categories for a specific first-level category
    """
    first_category = request.GET.get('first_category', '')

    # Validate input
    if not first_category:
        return JsonResponse({
            'state': 'error',
            'msg': 'First-level category cannot be empty',
            'data': []
        }, status=400)

    try:
        # Query all second-level categories under a specific first-level category
        second_categories = list(
            Types.objects.filter(firsts=first_category)
            .values_list('seconds', flat=True)
            .distinct()
        )

        return JsonResponse({
            'state': 'success',
            'msg': 'Retrieved second-level categories successfully',
            'data': second_categories
        })

    except Exception as e:
        # Log error
        return JsonResponse({
            'state': 'error',
            'msg': f'Failed to get second-level categories: {str(e)}',
            'data': []
        }, status=500)