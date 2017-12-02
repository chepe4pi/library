from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from catalog.models import Book, Author, Category, Bookmark, BookRating, WishlistedBook
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
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories', 'in_bookmarks',
            'rating'
        )

    def get_in_bookmarks(self, book):
        if 'bookmarked_books' in self.context:
            return book.id in self.context['bookmarked_books']
        return in_bookmarks(book, self.context['request'].user)

    def get_rating(self, book):
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


class BookRatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BookRating
        fields = ('id', 'book', 'user', 'rating')


class ExpandedBookRatingSerializer(BookRatingSerializer):
    book = ExpandedBookSerializer(read_only=True)


class StaffBookRatingSerializer(BookRatingSerializer):
    user = serializers.PrimaryKeyRelatedField
