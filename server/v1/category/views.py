from django.db.models import F
from rest_framework import generics
from rest_framework import permissions

from server.models.category import Category, CategorySerializer
from server.models.url import Url
from server.permissions import IsOwner


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    """
        카테고리 리스트 or 등록 API

        ---
        ## Headers
            - Content type : application/json
            - Authorization : JWT <토큰>
        ## Body
            - name : 카테고리 이름

    """
    serializer_class = CategorySerializer
    DEFAULT_URL_INFO = {'path': 'https://docs.google.com/forms/u/2/d/1Th2nvY2v0mkqPTzJ6tCes0GTMJozZvAV5DzqkgIbrME/edit',
                        'title': '서비스 개선에 참여해주세요',
                        'description': '유어링크를 사용하면서 불편하거나\n개선할 점이 있다면 의견을 남겨주세요.',
                        'favicon_path': 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/favicon.png',
                        'image_path': 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/service-improvement.png',
                        'user': None,
                        'category': None
                        }

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(user=user)
        return queryset

    def get_my_last_order(self):
        return Category.objects.get_my_last_order(self.request.user)

    def post(self, request, *args, **kwargs):
        user = self.request.user.pk
        request.data['order'] = self.get_my_last_order() + 1
        request.data['user'] = user
        response = self.create(request, *args, **kwargs)
        self.add_default_url(self.request.user, Category.objects.get(id=response.data['id']))
        return response

    def add_default_url(self, user, category):
        self.DEFAULT_URL_INFO['user'] = user
        self.DEFAULT_URL_INFO['category'] = category
        Url.objects.create(**self.DEFAULT_URL_INFO)


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
        카테고리 조회 & 수정 & 삭제 API

        ---
        ## Headers
            - Content type : application/json
            - Authorization : JWT <토큰>
        ## Path Params
            - id : 카테고리 id
        ## Body
            - name : 카테고리 이름
            - order : 순서
            - is_favorited : 즐겨찾기

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_destroy(self, instance):
        instance_order = instance.order
        Category.objects.filter(user=self.request.user, order__gt=instance_order).update(order=F('order') - 1)
        instance.delete()

    def update(self, request, *args, **kwargs):
        user = self.request.user.pk
        request.data['user'] = user
        return super().update(request, *args, **kwargs)

    # TODO 1) db 실행계획, 인덱스 확인하기
