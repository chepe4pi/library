from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from catalog.models import Book, Author, Category, Bookmark
from catalog.logic import in_bookmarks


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'family_name', 'full_name', 'about')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class BookSerializer(serializers.ModelSerializer):
    in_bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories', 'in_bookmarks'
        )

    def get_in_bookmarks(self, book):
        if 'bookmarked_books' in self.context:
            return book in self.context['bookmarked_books']
        return in_bookmarks(book, self.context['request'].user)


class ExpandedBookSerializer(BookSerializer):
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Bookmark
        fields = ('id', 'book', 'user', 'memo', 'created_at')
        validators = [
            UniqueTogetherValidator(queryset=Bookmark.objects.all(), fields=('book', 'user'))
        ]


class ExpandedBookmarkSerializer(BookmarkSerializer):
    book = ExpandedBookSerializer(read_only=True)


class StaffBookmarkSerializer(ExpandedBookmarkSerializer):
    user = serializers.PrimaryKeyRelatedField
