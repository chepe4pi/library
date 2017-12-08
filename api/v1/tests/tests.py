from rest_framework.test import APITestCase
from catalog.models import Book, UserBookRelation
from django.contrib.auth import get_user_model
from django.urls import reverse
from .factories import UserFactory, BookFactory, UserBookRelationFactory, AuthorFactory, CategoryFactory
from ..mixins.views import PrefetchUserData
from api.v1.serializers import BookSerializer, UserBookRelationSerializer, StaffBookRelationSerializer
import status, pdb, random

User = get_user_model()


class BooksEndpointTestCase(APITestCase):
    def setUp(self):
        self.admin = UserFactory.create(is_superuser=True, is_staff=True)
        self.user = UserFactory.create(is_superuser=False, is_staff=False)

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


class UserBookRelationsEndpointTestCase(APITestCase):
    def setUp(self):
        self.admin = UserFactory.create(is_superuser=True, is_staff=True)
        self.user = UserFactory.create(is_superuser=False, is_staff=False)

        self.authors = AuthorFactory.create_batch(2)
        self.categories = CategoryFactory.create_batch(5)
        self.books = BookFactory.create_batch(5)
        self.relations = [UserBookRelationFactory(user=user, book=book) for book in self.books for user in
                          (self.user, self.admin)]

    def tearDown(self):
        pass

    def get_serializer(self, data, user=None, **kwargs):
        if user and user.is_staff:
            return StaffBookRelationSerializer(data, **kwargs)
        return UserBookRelationSerializer(data, **kwargs)

    def test_relations_list_unauthorized_load(self):
        response = self.client.get(reverse('api:v1:userbookrelation-list'))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to access a book relations list unauthorized should return 403 Forbidden"
        )

    def test_relations_list_user_load(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('api:v1:userbookrelation-list'))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access a book relations list as user should return 200 OK"
        )
        relations = UserBookRelation.objects.filter(user=self.user).all()
        self.assertEqual(
            response.json()['results'], self.get_serializer(relations, user=self.user, many=True).data,
            "Data mismatch for user book relations list"
        )

    def test_relations_list_admin_load(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('api:v1:userbookrelation-list'))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access a book relations list as admin should return 200 OK"
        )
        relations = UserBookRelation.objects.all()
        self.assertEqual(
            response.json()['results'], self.get_serializer(relations, user=self.admin, many=True).data,
            "Data mismatch for user book relations list"
        )

    def test_relations_detail_unauthorized_load(self):
        relation = random.choice(self.relations)
        response = self.client.get(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to access a book relations detail unauthorized should return 403 Forbidden"
        )

    def test_relations_detail_user_own_load(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.get(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access own relations detail as user should return 200 OK"
        )
        self.assertEqual(
            response.json(), self.get_serializer(relation, user=self.user).data,
            "Data mismatch for relation detail"
        )

    def test_relations_detail_user_other_load(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.get(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "Attempting to access other user's relations detail should return 404 Not Found"
        )

    def test_relations_detail_admin_own_load(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.get(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access own relation detail as admin should return 200 OK"
        )
        self.assertEqual(
            response.json(), self.get_serializer(relation, user=self.admin).data,
            "Data mismatch for relation detail"
        )

    def test_relations_detail_admin_other(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.get(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access other user's relation detail as admin should return 200 OK"
        )
        self.assertEqual(
            response.json(), self.get_serializer(relation, user=self.admin).data,
            "Data mismatch for relation detail"
        )

    def test_relations_create_user_unauthorized(self):
        response = self.client.post(reverse('api:v1:userbookrelation-list'), {})
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a book relation as unauthorized user should return 403 Forbidden"
        )

    def test_relations_create_user_own(self):
        self.client.force_authenticate(user=self.user)
        new_book = BookFactory.create()
        new_relation = UserBookRelationFactory.build(user=self.user, book=new_book)
        response = self.client.post(reverse('api:v1:userbookrelation-list'), self.get_serializer(new_relation).data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create an own book relation as regular user should return 201 Created"
        )
        self.assertEqual(
            response.json(), self.get_serializer(new_relation, user=self.user).data,
            "Data mismatch for newly created book relation"
        )

    def test_relations_create_user_other(self):
        self.client.force_authenticate(user=self.user)
        new_book = BookFactory.create()
        new_relation = UserBookRelationFactory.build(user=self.admin, book=new_book)
        response = self.client.post(reverse('api:v1:book-list'), self.get_serializer(new_relation).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a book as regular user should return 403 Forbidden"
        )

    def test_relations_create_admin_own(self):
        self.client.force_authenticate(user=self.admin)
        new_book = BookFactory.create()
        new_relation = UserBookRelationFactory.build(user=self.admin, book=new_book)
        response = self.client.post(
            reverse('api:v1:userbookrelation-list'),
            self.get_serializer(new_relation, user=self.admin).data
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create an own book relation as admin should return 201 Created"
        )
        self.assertEqual(
            response.json(), self.get_serializer(new_relation, user=self.admin).data,
            "Data mismatch for newly created book relation"
        )

    def test_relations_create_admin_other(self):
        self.client.force_authenticate(user=self.admin)
        new_book = BookFactory.create()
        new_relation = UserBookRelationFactory.build(user=self.user, book=new_book)
        response = self.client.post(
            reverse('api:v1:userbookrelation-list'),
            self.get_serializer(new_relation, user=self.admin).data
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create an other user's relation as admin should return 201 Created"
        )
        self.assertEqual(
            response.json(), self.get_serializer(new_relation, user=self.admin).data,
            "Data mismatch for newly created book relation"
        )

    def test_relations_delete_unauthorized(self):
        relation = random.choice(self.relations)
        response = self.client.delete(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a relation as unauthorized user should return 403 Forbidden"
        )

    def test_relation_delete_user_own(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.delete(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete own relation as regular user should return 204 No Content"
        )
        self.assertFalse(
            UserBookRelation.objects.filter(id=relation.id).exists(), "Failed to properly delete a relation"
        )

    def test_relation_delete_user_other(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.delete(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "Attempting to delete other user's relation as regular user should return 404 Not Found"
        )

    def test_relation_delete_admin_own(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.delete(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete a relation as admin should return 204 No Content"
        )
        self.assertFalse(
            UserBookRelation.objects.filter(id=relation.id).exists(), "Failed to properly delete a relation"
        )

    def test_relation_delete_admin_other(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.delete(reverse('api:v1:userbookrelation-detail', args=(relation.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete other user's relation as admin should return 204 No Content"
        )
        self.assertFalse(
            UserBookRelation.objects.filter(id=relation.id).exists(), "Failed to properly delete a relation"
        )

    def test_relation_update_user_unauthorized(self):
        relation = random.choice(self.relations)
        response = self.client.patch(reverse('api:v1:userbookrelation-detail', args=(relation.id,)), {
            'in_bookmarks': not relation.in_bookmarks
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to update a relation as unauthorized user should return 403 Forbidden"
        )

    def test_relation_update_user_own(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.patch(reverse('api:v1:userbookrelation-detail', args=(relation.id,)), {
            'in_bookmarks': not relation.in_bookmarks
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update own relation as user should return 200 OK"
        )
        updated_relation = UserBookRelation.objects.get(id=relation.id)
        self.assertNotEqual(updated_relation.in_bookmarks, relation.in_bookmarks, "Failed to properly modify resource")

    def test_relation_update_user_other(self):
        self.client.force_authenticate(self.user)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.patch(reverse('api:v1:userbookrelation-detail', args=(relation.id,)), {
            'in_bookmarks': not relation.in_bookmarks
        })
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "Attempting to update other user's relation as user should return 404 Not Found"
        )

    def test_relation_update_admin_own(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.admin).first()
        response = self.client.patch(reverse('api:v1:userbookrelation-detail', args=(relation.id,)), {
            'in_bookmarks': not relation.in_bookmarks
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update own relation as admin should return 200 OK"
        )
        updated_relation = UserBookRelation.objects.get(id=relation.id)
        self.assertNotEqual(updated_relation.in_bookmarks, relation.in_bookmarks, "Failed to properly modify resource")

    def test_relation_update_admin_other(self):
        self.client.force_authenticate(self.admin)
        relation = UserBookRelation.objects.filter(user=self.user).first()
        response = self.client.patch(reverse('api:v1:userbookrelation-detail', args=(relation.id,)), {
            'in_bookmarks': not relation.in_bookmarks
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update other user's relation as admin should return 200 OK"
        )
        updated_relation = UserBookRelation.objects.get(id=relation.id)
        self.assertNotEqual(updated_relation.in_bookmarks, relation.in_bookmarks, "Failed to properly modify resource")
