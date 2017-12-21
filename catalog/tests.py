from django.test import TestCase
from . import logic
from django.contrib.auth.models import AnonymousUser
from .models import Book, DiscountGroup, Category
from api.v1.tests import factories
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


# Create your tests here.
class LogicTestCase(TestCase):
    def setUp(self):
        factories.UserFactory.create()
        factories.UserFactory.create(is_staff=True)
        factories.AuthorFactory.create_batch(2)
        factories.CategoryFactory.create_batch(3)
        factories.BookFactory.create_batch(5)

    def test_in_bookmarks_anonymous(self):
        book = Book.objects.order_by('?').first()
        self.assertFalse(logic.in_bookmarks(book, AnonymousUser()))

    def test_in_bookmarks_logged_in(self):
        book = Book.objects.order_by('?').first()
        user = User.objects.order_by('?').first()
        relation = factories.UserBookRelationFactory.create(user=user, book=book)
        self.assertEqual(relation.in_bookmarks, logic.in_bookmarks(book, user))

    def test_in_bookmarks_no_user(self):
        book = Book.objects.order_by('?').first()
        self.assertFalse(logic.in_bookmarks(book, None))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_book_price_recalculation(self):
        book = factories.BookFactory.create(discount=10, price_original=1000)
        book = Book.objects.get(id=book.id)
        self.assertEqual(900, book.price)
        book.discount = 20
        book.save()
        book = Book.objects.get(id=book.id)
        self.assertEqual(800, book.price)
        discount_group = DiscountGroup.objects.create(name="DG1", discount=20)
        book.discount_group = discount_group
        book.save()
        book = Book.objects.get(id=book.id)
        self.assertEqual(600, book.price)
        discount_group.discount = 30
        discount_group.save()
        book = Book.objects.get(id=book.id)
        self.assertEqual(500, book.price)
        book.discount = 0
        book.save()
        book = Book.objects.get(id=book.id)
        self.assertEqual(700, book.price)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_category_book_stats(self):
        category = factories.CategoryFactory.create()
        factories.BookFactory.create(price_original=20, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=40, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=60, discount=0, categories=(category,))
        category = Category.objects.get(id=category.id)
        self.assertEqual(3, category.book_count)
        self.assertEqual(40, category.book_average_price)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_category_book_stats_with_none(self):
        category = factories.CategoryFactory.create()
        factories.BookFactory.create(price_original=None, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=100, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=50, discount=0, categories=(category,))
        category = Category.objects.get(id=category.id)
        self.assertEqual(3, category.book_count)
        self.assertEqual(75, category.book_average_price)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_category_book_stats_with_zero(self):
        category = factories.CategoryFactory.create()
        factories.BookFactory.create(price_original=0, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=100, discount=0, categories=(category,))
        factories.BookFactory.create(price_original=50, discount=0, categories=(category,))
        category = Category.objects.get(id=category.id)
        self.assertEqual(3, category.book_count)
        self.assertEqual(50, category.book_average_price)
