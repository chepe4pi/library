from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from catalog.models import Book, Author, Category, UserBookRelation
from catalog.logic import in_bookmarks
from rest_framework.exceptions import ValidationError


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
    in_wishlist = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories', 'in_bookmarks',
            'rating', 'in_wishlist'
        )

    def get_relation(self, book):
        if 'user_book_relations' not in self.context:
            raise NotImplemented('UserBookRelation model data not prefetched')
        return self.context['user_book_relations'].filter(book__id=book.id).first()

    def get_in_bookmarks(self, book):
        return getattr(self.get_relation(book), 'in_bookmarks', False)

    def get_rating(self, book):
        return getattr(self.get_relation(book), 'in_bookmarks', None)

    def get_in_wishlist(self, book):
        return getattr(self.get_relation(book), 'in_bookmarks', False)


class ExpandedBookSerializer(BookSerializer):
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)


class UserBookRelationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserBookRelation
        fields = ('user', 'book', 'in_wishlist', 'in_bookmarks', 'rating')


class ExpandedUserBookRelationSerializer(UserBookRelationSerializer):
    book = BookSerializer(read_only=True)


class StaffBookRelationSerializer(UserBookRelationSerializer):
    user = serializers.PrimaryKeyRelatedField
