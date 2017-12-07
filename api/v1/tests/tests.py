from rest_framework.test import APITestCase
from catalog.models import Book
from django.contrib.auth import get_user_model
from django.urls import reverse
from .factories import UserFactory, BookFactory, UserBookRelationFactory, AuthorFactory, CategoryFactory
from ..mixins.views import PrefetchUserData
from api.v1.serializers import BookSerializer
import status, pdb, random

User = get_user_model()


class BooksEndpointTestCase(APITestCase):
    def setUp(self):
        self.admin = UserFactory.create(is_superuser=True)
        self.user = UserFactory.create(is_superuser=False)

        self.authors = AuthorFactory.create_batch(2)
        self.categories = CategoryFactory.create_batch(5)
        self.books = BookFactory.create_batch(5)
        [UserBookRelationFactory(user=user, book=book) for book in self.books for user in (self.user, self.admin)]

    def tearDown(self):
        pass

    def get_serializer(self, data, user=None, **kwargs):
        kwargs.setdefault('context', {})
        kwargs["context"].update(PrefetchUserData.get_extra_context(user))
        return BookSerializer(data, **kwargs)

    def test_book_list_load(self):
        response = self.client.get(reverse('api:v1:book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Book list failed to load")
        self.assertEqual(
            response.json()['results'], self.get_serializer(self.books, many=True).data,
            "Data mismatch in book list"
        )

    def test_book_detail_load(self):
        book = random.choice(self.books)
        response = self.client.get(reverse('api:v1:book-detail', args=(book.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Book detail failed to load")
        self.assertEqual(
            response.json(), self.get_serializer(book).data,
            "Data mismatch in book detail"
        )

    def test_book_create_user_unauthorized(self):
        new_book = BookFactory.build()
        response = self.client.post(reverse('api:v1:book-list'), self.get_serializer(new_book).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_create_user_regular(self):
        self.client.force_authenticate(user=self.user)
        new_book = BookFactory.build()
        response = self.client.post(reverse('api:v1:book-list'), self.get_serializer(new_book, self.user).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a book as regular user should return 403 Forbidden"
        )

    def test_book_create_user_admin(self):
        self.client.force_authenticate(user=self.admin)
        book_data = self.get_serializer(BookFactory.build(), self.admin).data
        response = self.client.post(reverse('api:v1:book-list'), book_data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create a book as admin should return 201 Created"
        )
        new_id = response.json()['id']
        expected_data = self.get_serializer(Book.objects.get(id=new_id), self.admin).data
        expected_data['id'] = None
        self.assertEqual(
            book_data, expected_data,
            "Data mismatch in newly created book"
        )

    def test_book_delete_user_unauthorized(self):
        book = random.choice(self.books)
        response = self.client.delete(reverse('api:v1:book-detail', args=(book.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_delete_user_regular(self):
        self.client.force_authenticate(self.user)
        book = random.choice(self.books)
        response = self.client.delete(reverse('api:v1:book-detail', args=(book.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a book as regular user should return 403 Forbidden"
        )

    def test_book_delete_user_admin(self):
        self.client.force_authenticate(self.admin)
        book = random.choice(self.books)
        response = self.client.delete(reverse('api:v1:book-detail', args=(book.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete a book as admin should return 204 No Content"
        )
        self.assertFalse(Book.objects.filter(id=book.id).exists(), "Failed to properly delete a book")

    def test_book_update_user_unauthorized(self):
        book = random.choice(self.books)
        response = self.client.patch(reverse('api:v1:book-detail', args=(book.id,)), {
            'title': 'TitleModified'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_update_user_regular(self):
        self.client.force_authenticate(self.user)
        book = random.choice(self.books)
        response = self.client.patch(reverse('api:v1:book-detail', args=(book.id,)), {
            'title': 'TitleModified'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_update_user_admin(self):
        self.client.force_authenticate(self.admin)
        book = random.choice(self.books)
        response = self.client.patch(reverse('api:v1:book-detail', args=(book.id,)), {
            'title': 'TitleModified'
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update a book as admin should return 200 OK"
        )
        updated_book = Book.objects.get(id=book.id)
        self.assertEqual(updated_book.title, 'TitleModified', "Failed to properly modify resource")
