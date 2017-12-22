from rest_framework import serializers
from catalog.models import Book, Author, Category, UserBookRelation
from catalog import logic as catalog_logic


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'family_name', 'full_name', 'about')


class CategorySerializer(serializers.ModelSerializer):
    book_average_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'book_average_price', 'book_count')


class BookSerializer(serializers.ModelSerializer):
    in_bookmarks = serializers.SerializerMethodField()
    in_wishlist = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    discount_total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'title_original', 'year_published', 'description', 'author', 'categories', 'in_bookmarks',
            'rating', 'in_wishlist', 'price', 'discount', 'discount_total', 'price_original'
        )

    def get_relation(self, book):
        if 'user_book_relations' not in self.context:
            raise NotImplementedError('User data relation not prefetched; prefetch data to avoid N+1 problem')
        for relation in self.context['user_book_relations']:
            if relation['book__id'] == book.id:
                return relation

    def get_in_bookmarks(self, book):
        relation = self.get_relation(book)
        return relation['in_bookmarks'] if relation else False

    def get_rating(self, book):
        relation = self.get_relation(book)
        return relation['rating'] if relation else None

    def get_in_wishlist(self, book):
        relation = self.get_relation(book)
        return relation['in_wishlist'] if relation else False


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

    class Meta:
        model = UserBookRelation
        fields = ('id', 'user', 'book', 'in_wishlist', 'in_bookmarks', 'rating')
