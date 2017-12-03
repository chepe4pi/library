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

    def get_in_bookmarks(self, book):
        if 'user_book_relations' not in self.context:
            raise NotImplemented('UserBookRelation model data not prefetched')
        for book_id, rel_type, rel_value in self.context['user_book_relations']:
            if book_id == book.id and rel_type == UserBookRelation.TYPE_BOOKMARK:
                return True
        return False

    def get_rating(self, book):
        if 'user_book_relations' not in self.context:
            raise NotImplemented('UserBookRelation model data not prefetched')
        for book_id, rel_type, rel_value in self.context['user_book_relations']:
            if book_id == book.id and rel_type == UserBookRelation.TYPE_RATING:
                rating_dict = {k: v for k, v in UserBookRelation.RATING_CHOICES}
                return rating_dict[rel_value]
        return None

    def get_in_wishlist(self, book):
        if 'user_book_relations' not in self.context:
            raise NotImplemented('UserBookRelation model data not prefetched')
        for book_id, rel_type, rel_value in self.context['user_book_relations']:
            if book_id == book.id and rel_type == UserBookRelation.TYPE_WISHLISTED:
                return True
        return False


class ExpandedBookSerializer(BookSerializer):
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)


class UserBookRelationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['type'] == UserBookRelation.TYPE_RATING:
            rating_values = (c[0] for c in UserBookRelation.RATING_CHOICES)
            if attrs['value'] not in rating_values:
                raise ValidationError({'value': 'Incorrect rating value'})
        return attrs

    class Meta:
        model = UserBookRelation
        fields = ('user', 'book', 'type', 'value', 'created_at')


class ExpandedUserBookRelationSerializer(UserBookRelationSerializer):
    book = BookSerializer(read_only=True)


class StaffBookRelationSerializer(UserBookRelationSerializer):
    user = serializers.PrimaryKeyRelatedField
