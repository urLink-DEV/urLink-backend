from django.conf import settings
from django.db import models
from django_filters import rest_framework as rest_framework_filters
from rest_framework import serializers

from server.exceptions import ServerException

DEFAULT_URL_INFO = {
    'path': 'https://docs.google.com/forms/u/2/d/1Th2nvY2v0mkqPTzJ6tCes0GTMJozZvAV5DzqkgIbrME/edit',
    'title': '서비스 개선에 참여해주세요',
    'description': '유어링크를 사용하면서 불편하거나\n개선할 점이 있다면 의견을 남겨주세요.',
    'favicon_path': 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/favicon.png',
    'image_path': 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/service-improvement.png',
    'user': None,
    'category': None
}


class Url(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='urls', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', related_name='urls', on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    favicon_path = models.CharField(max_length=500)
    image_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        ordering = ["-is_favorited", "-created_at"]


class UrlSerializer(serializers.ModelSerializer):
    has_alarms = serializers.SerializerMethodField()

    class Meta:
        model = Url
        fields = '__all__'

    def get_has_alarms(self, url):  # 아직 안울린 알람이 있는지 확인
        for alarm in url.alarms.all():
            if not alarm.has_been_sent:
                return True
        return False

    def update(self, instance, validated_data):
        if validated_data.get('path'):
            raise ServerException('URL은 수정할 수 없습니다.')
        return super().update(instance, validated_data)


class UrlFilter(rest_framework_filters.FilterSet):
    path = rest_framework_filters.CharFilter(field_name='path', lookup_expr='contains')
    title = rest_framework_filters.CharFilter(field_name='title', lookup_expr='contains')

    class Meta:
        model = Url
        fields = ['path', 'title']


def add_default_url(user, category):
    DEFAULT_URL_INFO['user'] = user
    DEFAULT_URL_INFO['category'] = category
    Url.objects.create(**DEFAULT_URL_INFO)
