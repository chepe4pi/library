from rest_framework import serializers
from catalog.models import Book, Author, Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'family_name', 'full_name', 'about')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class BookSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields_data = super().get_fields()
        if self.context['request'].GET.get('expand', False):
            fields_data['author'] = AuthorSerializer(read_only=True)
            fields_data['categories'] = CategorySerializer(many=True, read_only=True)
        return fields_data

    class Meta:
        model = Book
        fields = ('id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories')
