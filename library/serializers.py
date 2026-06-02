from rest_framework import serializers
from .models import Book, Loan, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
    )
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'description',
            'available_copies',
            'category',
            'category_id',
            'cover_image_url',
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True,
    )

    class Meta:
        model = Loan
        fields = [
            'id',
            'user',
            'book',
            'book_id',
            'borrowed_date',
            'return_date',
            'returned',
        ]

    def create(self, validated_data):
        return Loan.objects.create(user=self.context['request'].user, **validated_data)
