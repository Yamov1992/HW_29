from rest_framework.fields import SerializerMethodField, BooleanField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from ads.models import Ads, Category, Selection
from ads.validators import not_true
from users.models import User


class AdsSerializer(ModelSerializer):
    is_published = BooleanField(validators=[not_true], required=False)

    class Meta:
        model = Ads
        fields = "__all__"


class AdsDetailSerializer(ModelSerializer):
    author_id = SlugRelatedField(slug_field="username", queryset=User.objects.all())
    category_id = SlugRelatedField(slug_field="name", queryset=Category.objects.all())

    class Meta:
            model = Ads
            fields = "__all__"


class AdsListSerializer(ModelSerializer):
    author_id = SlugRelatedField(slug_field="username", queryset=User.objects.all())
    category_id = SlugRelatedField(slug_field="name", queryset=Category.objects.all())
    address = SerializerMethodField()

    def get_address(self, ads):
        return [loc.name for loc in ads.author_id.location.all()]

    class Meta:
        model = Ads
        fields = "__all__"


class SelectionSerializer(ModelSerializer):

    class Meta:
        model = Selection
        fields = "__all__"


class SelectionCreateSerializer(ModelSerializer):
    owner = SlugRelatedField(slug_field="username", read_only = True)

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["owner"] =request.user_id
        return super().create(validated_data)

    class Meta:
        model = Selection
        fields = "__all__"


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
