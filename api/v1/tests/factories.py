from factory.django import DjangoModelFactory
import factory
from catalog.models import Book, Author, Category, UserBookRelation
from factory import Faker
import random
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    username = Faker('name')
    password = Faker('password')
    email = Faker('email')

    class Meta:
        model = User


class AuthorFactory(DjangoModelFactory):
    name = Faker('word')
    family_name = Faker('word')
    about = Faker('paragraph')

    class Meta:
        model = Author


class CategoryFactory(DjangoModelFactory):
    name = Faker('word')
    description = Faker('paragraph')

    class Meta:
        model = Category


class BookFactory(DjangoModelFactory):
    title = Faker('word')
    title_original = Faker('word')
    author = factory.Iterator(Author.objects.all())

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.categories.add(extracted)
            return

        categories = Category.objects.all()
        n = random.choice(range(categories.count()))
        for i in range(n):
            self.categories.add(random.choice(categories))

    class Meta:
        model = Book


class UserBookRelationFactory(DjangoModelFactory):
    book = factory.Iterator(Book.objects.all())
    user = factory.Iterator(User.objects.all())
    in_bookmarks = Faker('pybool')
    in_wishlist = Faker('pybool')
    rating = random.choice(UserBookRelation.RATING_CHOICES)[0]

    class Meta:
        model = UserBookRelation
