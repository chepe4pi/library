from rest_framework.test import APITestCase
from catalog.models import Author, Book, Category, UserBookRelation
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()
client = APIClient()


class BooksEndpointTestCase(APITestCase):
    def setUp(self):
        admin = User.objects.create_superuser(username='admin', password='123123qwe', email='test@test.ru')
        user = User.objects.create_user(username='user1', password='123123qwe')
        category1 = Category.objects.create(name='Category1')
        category2 = Category.objects.create(name='Category2')
        category3 = Category.objects.create(name='Category3')
        author1 = Author.objects.create(name='Author1', family_name='Author1FamilyName')
        author2 = Author.objects.create(name='Author2', about='Author2About')
        book1 = Book.objects.create(title='Book1', title_original='Book1Original', author=author1)
        book1.categories.add(category1, category2)
        book1.save()
        book2 = Book.objects.create(title='Book2', title_original='Book2Original', author=author2)
        book2.categories.add(category2, category3)
        book2.save()

        UserBookRelation.objects.create(user=admin, book=book2, in_bookmarks=True, in_wishlist=True,
                                        rating=UserBookRelation.RATING_GOOD)
        UserBookRelation.objects.create(user=user, book=book2, in_bookmarks=True, in_wishlist=True,
                                        rating=UserBookRelation.RATING_GOOD)

    def tearDown(self):
        pass

    def test_book_list_load(self):
        response = client.get(reverse('api:v1:book-list'))
        self.assertEqual(response.status_code, 200, "Book list failed to load")

    def test_book_detail_load(self):
        response = client.get(reverse('api:v1:book-detail', args=(1,)))
        self.assertEqual(response.status_code, 200, "Book detail failed to load")

    def test_book_create_user_unauthorized(self):
        response = client.post(reverse('api:v1:book-list'), {
            'title': 'Book4',
            'title_original': "Book4",
            'author': 1,
            'categories': (1, 2)
        })
        self.assertEqual(
            response.status_code, 403, "Attempting to create a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_create_user_regular(self):
        client.login(username='user1', password='123123qwe')
        response = client.post(reverse('api:v1:book-list'), {
            'title': 'Book4',
            'title_original': "Book4",
            'author': 1,
            'categories': (1, 2)
        })
        self.assertEqual(
            response.status_code, 403, "Attempting to create a book as regular user should return 403 Forbidden"
        )

    def test_book_create_user_admin(self):
        client.login(username='admin', password='123123qwe')
        response = client.post(reverse('api:v1:book-list'), {
            'title': 'Book4',
            'title_original': "Book4",
            'author': 1,
            'categories': (1, 2)
        })
        self.assertEqual(
            response.status_code, 201, "Attempting to create a book as admin should return 201 Created"
        )
        new_id = response.json()['id']
        response = client.get(reverse('api:v1:book-detail', args=(new_id,)))
        self.assertEqual(response.status_code, 200, "Failed to access newly created book")

    def test_book_delete_user_unauthorized(self):
        response = client.delete(reverse('api:v1:book-detail', args=(1,)))
        self.assertEqual(
            response.status_code, 403, "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_delete_user_regular(self):
        client.login(username='user1', password='123123qwe')
        response = client.delete(reverse('api:v1:book-detail', args=(1,)))
        self.assertEqual(
            response.status_code, 403, "Attempting to delete a book as regular user should return 403 Forbidden"
        )

    def test_book_delete_user_admin(self):
        client.login(username='admin', password='123123qwe')
        response = client.delete(reverse('api:v1:book-detail', args=(1,)))
        self.assertIn(
            response.status_code, (200, 202, 204), "Attempting to delete a book as admin should return 200, 202 or 204"
        )
        response = client.get(reverse('api:v1:book-detail', args=(1,)))
        self.assertEqual(response.status_code, 404, "Failed to properly delete a book")

    def test_book_update_user_unauthorized(self):
        response = client.patch(reverse('api:v1:book-detail', args=(1,)), {
            'title': 'TitleModified'
        })
        self.assertEqual(
            response.status_code, 403, "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_update_user_regular(self):
        client.login(username='user1', password='123123qwe')
        response = client.patch(reverse('api:v1:book-detail', args=(1,)), {
            'title': 'TitleModified'
        })
        self.assertEqual(
            response.status_code, 403, "Attempting to delete a book as unauthorized user should return 403 Forbidden"
        )

    def test_book_update_user_admin(self):
        client.login(username='admin', password='123123qwe')
        response = client.patch(reverse('api:v1:book-detail', args=(1,)), {
            'title': 'TitleModified'
        })
        self.assertIn(
            response.status_code, (200, 202, 204), "Attempting to update a book as admin should return 200, 202 or 204"
        )
        response = client.get(reverse('api:v1:book-detail', args=(1,)))
        self.assertEqual(response.json()['title'], 'TitleModified', "Failed to properly modify resource")
