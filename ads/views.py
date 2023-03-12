import json

from django.core.serializers import serialize
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

import ads
from ads.models import Category, Ads, Selection
from ads.permissions import IsOwner, IsStaff
from ads.serializers import AdsSerializer, AdsDetailSerializer, AdsListSerializer, SelectionSerializer, \
    SelectionCreateSerializer


# def ok(request):
#     return JsonResponse({"status":"ok"})

class CategoryListView(generic.ListView):
    model = Category
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        categories = self.queryset
        categories_list = serialize(Category, categories)
        return JsonResponse(categories_list, safe=False)
#
class CategoryDetailView(generic.DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        try:
            category = Category.objects.get(pk=kwargs['pk'])
        except Category.DoesNotExist as e:
            return JsonResponse({'detail': e.args[0]}, status=400)
        res = serialize(Category, category)
        return JsonResponse(res, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(generic.CreateView):
    model = Category
    fields = ['name']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.create(**data)
        result = serialize(Category, category)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(generic.UpdateView):
    model = Category
    fields = ['name']

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.get(id=kwargs['pk'])
        category.name = data['name']
        category.save()
        result = serialize(Category, category)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(generic.DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({"status": "ok"}, status=200)

# class AdsListView(generic.ListView):
#     model = Ads
#     queryset = Ads.objects.all()
#
#     def get(self, request, *args, **kwargs):
#         super().get(request, *args, **kwargs)
#
#         self.object_list.select_related('author_id').order_by('-price')
#         paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#         ads = serialize(Ads, page_obj)
#
#         response = {
#             'items': ads,
#             'num_pages': page_obj.paginator.num_pages,
#             'total': page_obj.paginator.count,
#         }
#
#         return JsonResponse(response, safe=False)
class AdsViewSet(ModelViewSet):
    default_serizalizer = AdsSerializer
    queryset = Ads.objects.order_by('-price')
    serializers = {'retrieve': AdsDetailSerializer,
                   'list': AdsListSerializer
                   }
    default_permission = [AllowAny]
    permissions = {"retrieve": [IsAuthenticated],
                   'update': [IsAuthenticated, IsOwner|IsStaff],
                   'partial_update': [IsAuthenticated, IsOwner|IsStaff],
                   'destroy': [IsAuthenticated, IsOwner|IsStaff]
                   }

    def get_permissions(self):
        return [permission() for permission in self.permissions.get(self.action, self.default_permission)]
    #то есть получаем список из словаря, если есть на это action, сработает, если нет - возьмется дефортный
    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serizalizer)


    def list(self, request, *args, **kwargs):
        categories = request.GET.getlist('cat')
        if categories:
            self.queryset = self.queryset.filter(category_id__in=categories)  #переопределяем queryset

        text = request.GET.get('text')
        if text:
            self.queryset = self.queryset.filter(name__icontains=text)  #переопределяем queryset

        location = request.GET.get('location')
        if location:
            self.queryset = self.queryset.filter(author_id__location__name__icontains=location)  # переопределяем queryset

        price_from = request.GET.get('price_from')
        if price_from:
            self.queryset = self.queryset.filter(price__gte=price_from)  # переопределяем queryset

        price_to = request.GET.get('price_to')
        if price_to:
            self.queryset = self.queryset.filter(price__lte=price_to)  # переопределяем queryset

        return super().list(request, *args, **kwargs)

class SelectionViewSet(ModelViewSet):
    serializer_class = SelectionSerializer
    queryset = Selection.objects.all()
    default_permission = [AllowAny]
    permissions = {"create":[IsAuthenticated],
                   "update": [IsAuthenticated, IsOwner],
                   "partial_update":[IsAuthenticated, IsOwner],
                   "destroy": [IsAuthenticated, IsOwner]}

    default_serializer = SelectionSerializer
    serializers = {"create": SelectionCreateSerializer,
                   }

    def get_permissions(self):
        return [permission() for permission in self.permissions.get(self.action, self.default_permission)]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer)







@method_decorator(csrf_exempt, name='dispatch')
class AdsCreateView(generic.CreateView):
    model = Ads
    fields = ["name", "author_id", "price", "description", "is_published", "category_id"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ads = Ads.objects.create(**data)
        result = serialize(Ads, ads)
        return JsonResponse(result, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class AdsUpdateView(generic.UpdateView):
    model = Ads
    fields = ["name", "author_id", "price", "description", "is_published", "category_id"]

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ads = Ads.objects.get(id=kwargs['pk'])
        ads.name = data['name']
        ads.price = data['price']
        ads.description = data['description']
        ads.save()
        result = serialize(Ads, ads)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsDeleteView(generic.DeleteView):
    model = Ads
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({"status": "ok"}, status=200)


# fields = ['name', 'price', 'description', 'address', 'is_published' ]

class AdsDetailView(generic.DetailView):
    model = Ads

    def get(self, request, *args, **kwargs):
        ads = self.get_object()

        try:
            ads = Ads.objects.get(pk=kwargs['pk'])
        except Ads.DoesNotExist as e:
            return JsonResponse({'detail': e.args[0]}, status=400)

        res = serialize(Ads, ads)
        return JsonResponse(res, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsUploadImageView(generic.UpdateView):
    model = Ads
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES.get('image')
        self.object.save()

        result = serialize(self.model, self.object)
        return JsonResponse(result, safe=False)


def serialize(model, values):  # model:<class 'ads.models.Category>' values:Class
    if isinstance(values, model):
        values = [values]
    else:
        list(values)

    result = []
    for value in values:  # value: Category object (1)
        data = {}
        for field in model._meta.get_fields():
            if field.is_relation:
                continue
            if field.name == 'image':
                data[field.name] = getattr(value.image, 'url', None)
            else:
                data[field.name] = getattr(value, field.name)
        result.append(data)

    return result






