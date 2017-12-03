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
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories', 'in_bookmarks',
            'rating'
        )

    def get_in_bookmarks(self, book):
        # TODO: rework!
        if 'bookmarked_books' in self.context:
            return book.id in self.context['bookmarked_books']
        return in_bookmarks(book, self.context['request'].user)

    def get_rating(self, book):
        # TODO: rework!
        if 'rated_books' in self.context:
            for book_id, rating in self.context['rated_books']:
                if book_id == book.id:
                    return rating
            return None
        book_rating = book.bookratings.filter(user=self.context['request'].user)
        return book_rating.rating if book_rating else None


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
