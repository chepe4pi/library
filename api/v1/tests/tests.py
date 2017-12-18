from rest_framework.test import APITestCase
from django.test.testcases import TestCase
from catalog.models import Book, UserBookRelation, Author, Category
from django.contrib.auth import get_user_model
from django.urls import reverse
from .factories import UserFactory, BookFactory, UserBookRelationFactory, AuthorFactory, CategoryFactory
from ..mixins.views import PrefetchUserData
from api.v1.serializers import BookSerializer, UserBookRelationSerializer, StaffBookRelationSerializer, \
    AuthorSerializer, CategorySerializer, ExpandedUserBookRelationSerializer, ExpandedBookSerializer
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

    def test_book_prefetch_user_data(self):
        books = Book.objects.all()
        with self.assertRaises(NotImplementedError) as cm:
            data = BookSerializer(books, many=True).data

    def test_book_list_load(self):
        response = self.client.get(reverse('api:v1:book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Book list failed to load")
        self.assertEqual(
            response.json()['results'], self.get_serializer(Book.objects.all(), many=True).data,
            "Data mismatch in book list"
        )

    def test_book_detail_load(self):
        book = Book.objects.first()
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
        new_book = BookFactory.build(price_original=1000, discount=25)
        new_book.price = 750
        new_book.discount_total = 25
        book_data = self.get_serializer(new_book, self.admin).data
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
            "Attempting to delete a book as regular user should return 403 Forbidden"
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

    def test_expanded(self):
        books = Book.objects.all()
        expected_data = ExpandedBookSerializer(
            books, many=True, context=PrefetchUserData.get_extra_context()
        ).data
        response = self.client.get(reverse('api:v1:book-list'), {'expand': True})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access expanded books list should return 200 OK"
        )
        actual_data = response.json()['results']
        self.assertEqual(
            actual_data, expected_data,
            "Data mismatch for expanded list"
        )


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
        actual_data = response.json()
        relation_saved = UserBookRelation.objects.get(id=actual_data['id'])
        self.assertEqual(
            actual_data, self.get_serializer(data=relation_saved, user=self.admin).data,
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
        actual_data = response.json()
        relation_created = UserBookRelation.objects.get(id=actual_data['id'])
        self.assertEqual(
            response.json(), self.get_serializer(relation_created, user=self.admin).data,
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

    def test_filter(self):
        self.client.force_authenticate(self.user)
        book = random.choice(self.books)
        relations = UserBookRelation.objects.filter(user=self.user, book=book)
        expected_data = UserBookRelationSerializer(
            relations, many=True, context=PrefetchUserData.get_extra_context(self.user)
        ).data
        response = self.client.get(reverse('api:v1:userbookrelation-list'), {'book': book.id})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access filtered relations list should return 200 OK"
        )
        self.assertEqual(
            expected_data, response.json()['results'],
            "Data mismatch for filtered list"
        )

    def test_expanded(self):
        self.client.force_authenticate(self.user)
        relations = UserBookRelation.objects.filter(user=self.user)
        expected_data = ExpandedUserBookRelationSerializer(
            relations, many=True, context=PrefetchUserData.get_extra_context(self.user)
        ).data
        response = self.client.get(reverse('api:v1:userbookrelation-list'), {'expand': True})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to access expanded relations list should return 200 OK"
        )
        self.assertEqual(
            expected_data, response.json()['results'],
            "Data mismatch for expanded list"
        )


class AuthorsEndpointTestCase(APITestCase):
    def setUp(self):
        self.admin = UserFactory.create(is_superuser=True, is_staff=True)
        self.user = UserFactory.create(is_superuser=False, is_staff=False)

        self.authors = AuthorFactory.create_batch(5)

    def tearDown(self):
        pass

    def get_serializer(self, data, **kwargs):
        return AuthorSerializer(data, **kwargs)

    def test_author_list_load(self):
        response = self.client.get(reverse('api:v1:author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Author list failed to load")
        self.assertEqual(
            response.json()['results'], self.get_serializer(self.authors, many=True).data,
            "Data mismatch in author list"
        )

    def test_author_detail_load(self):
        author = random.choice(self.authors)
        response = self.client.get(reverse('api:v1:author-detail', args=(author.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Book detail failed to load")
        self.assertEqual(
            response.json(), self.get_serializer(author).data,
            "Data mismatch in author detail"
        )

    def test_author_create_user_unauthorized(self):
        new_author = AuthorFactory.build()
        response = self.client.post(reverse('api:v1:author-list'), self.get_serializer(new_author).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create an author as unauthorized user should return 403 Forbidden"
        )

    def test_author_create_user_regular(self):
        self.client.force_authenticate(user=self.user)
        new_author = AuthorFactory.build()
        response = self.client.post(reverse('api:v1:author-list'), self.get_serializer(new_author).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create an author as regular user should return 403 Forbidden"
        )

    def test_author_create_user_admin(self):
        self.client.force_authenticate(user=self.admin)
        new_author = AuthorFactory.build()
        author_data = self.get_serializer(new_author).data
        response = self.client.post(reverse('api:v1:author-list'), author_data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create an author as admin should return 201 Created"
        )
        new_id = response.json()['id']
        expected_data = self.get_serializer(Author.objects.get(id=new_id)).data
        expected_data['id'] = None
        self.assertEqual(
            author_data, expected_data,
            "Data mismatch in newly created author"
        )

    def test_author_delete_user_unauthorized(self):
        author = random.choice(self.authors)
        response = self.client.delete(reverse('api:v1:author-detail', args=(author.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete an author as unauthorized user should return 403 Forbidden"
        )

    def test_author_delete_user_regular(self):
        self.client.force_authenticate(self.user)
        author = random.choice(self.authors)
        response = self.client.delete(reverse('api:v1:author-detail', args=(author.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete an author as regular user should return 403 Forbidden"
        )

    def test_author_delete_user_admin(self):
        self.client.force_authenticate(self.admin)
        author = random.choice(self.authors)
        response = self.client.delete(reverse('api:v1:author-detail', args=(author.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete an author as admin should return 204 No Content"
        )
        self.assertFalse(Book.objects.filter(id=author.id).exists(), "Failed to properly delete an author")

    def test_author_update_user_unauthorized(self):
        author = random.choice(self.authors)
        response = self.client.patch(reverse('api:v1:author-detail', args=(author.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete an author as unauthorized user should return 403 Forbidden"
        )

    def test_author_update_user_regular(self):
        self.client.force_authenticate(self.user)
        author = random.choice(self.authors)
        response = self.client.patch(reverse('api:v1:author-detail', args=(author.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete an author as regular user should return 403 Forbidden"
        )

    def test_author_update_user_admin(self):
        self.client.force_authenticate(self.admin)
        author = random.choice(self.authors)
        response = self.client.patch(reverse('api:v1:author-detail', args=(author.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update an author as admin should return 200 OK"
        )
        updated_author = Author.objects.get(id=author.id)
        self.assertEqual(updated_author.name, 'NewName', "Failed to properly modify resource")


class CategoriesEndpointTestCase(APITestCase):
    def setUp(self):
        self.admin = UserFactory.create(is_superuser=True, is_staff=True)
        self.user = UserFactory.create(is_superuser=False, is_staff=False)

        self.categories = CategoryFactory.create_batch(5)

    def tearDown(self):
        pass

    def get_serializer(self, data, **kwargs):
        return CategorySerializer(data, **kwargs)

    def test_category_list_load(self):
        response = self.client.get(reverse('api:v1:category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Category list failed to load")
        self.assertEqual(
            response.json()['results'], self.get_serializer(Category.objects.all(), many=True).data,
            "Data mismatch in category list"
        )

    def test_category_detail_load(self):
        category = Category.objects.order_by('?').first()
        response = self.client.get(reverse('api:v1:category-detail', args=(category.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Book detail failed to load")
        self.assertEqual(
            response.json(), self.get_serializer(category).data,
            "Data mismatch in category detail"
        )

    def test_category_create_user_unauthorized(self):
        new_category = CategoryFactory.build()
        response = self.client.post(reverse('api:v1:category-list'), self.get_serializer(new_category).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a category as unauthorized user should return 403 Forbidden"
        )

    def test_category_create_user_regular(self):
        self.client.force_authenticate(user=self.user)
        new_category = CategoryFactory.build()
        response = self.client.post(reverse('api:v1:category-list'), self.get_serializer(new_category).data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to create a category as regular user should return 403 Forbidden"
        )

    def test_category_create_user_admin(self):
        self.client.force_authenticate(user=self.admin)
        new_category = CategoryFactory.build()
        category_data = self.get_serializer(new_category).data
        category_data['book_average_price'] = None
        category_data['book_count'] = 0
        response = self.client.post(reverse('api:v1:category-list'), category_data)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Attempting to create a category as admin should return 201 Created"
        )
        new_id = response.json()['id']
        expected_data = self.get_serializer(Category.objects.get(id=new_id)).data
        expected_data['id'] = None
        self.assertEqual(
            category_data, expected_data,
            "Data mismatch in newly created category"
        )

    def test_category_delete_user_unauthorized(self):
        category = random.choice(self.categories)
        response = self.client.delete(reverse('api:v1:category-detail', args=(category.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a category as unauthorized user should return 403 Forbidden"
        )

    def test_category_delete_user_regular(self):
        self.client.force_authenticate(self.user)
        category = random.choice(self.categories)
        response = self.client.delete(reverse('api:v1:category-detail', args=(category.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a category as regular user should return 403 Forbidden"
        )

    def test_category_delete_user_admin(self):
        self.client.force_authenticate(self.admin)
        category = random.choice(self.categories)
        response = self.client.delete(reverse('api:v1:category-detail', args=(category.id,)))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Attempting to delete a category as admin should return 204 No Content"
        )
        self.assertFalse(Book.objects.filter(id=category.id).exists(), "Failed to properly delete a category")

    def test_category_update_user_unauthorized(self):
        category = random.choice(self.categories)
        response = self.client.patch(reverse('api:v1:category-detail', args=(category.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a category as unauthorized user should return 403 Forbidden"
        )

    def test_category_update_user_regular(self):
        self.client.force_authenticate(self.user)
        category = random.choice(self.categories)
        response = self.client.patch(reverse('api:v1:category-detail', args=(category.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            "Attempting to delete a category as user should return 403 Forbidden"
        )

    def test_category_update_user_admin(self):
        self.client.force_authenticate(self.admin)
        category = random.choice(self.categories)
        response = self.client.patch(reverse('api:v1:category-detail', args=(category.id,)), {
            'name': 'NewName'
        })
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Attempting to update a category as admin should return 200 OK"
        )
        updated_category = Category.objects.get(id=category.id)
        self.assertEqual(updated_category.name, 'NewName', "Failed to properly modify resource")


class SerializersTestCase(TestCase):
    def test_book_serializer(self):
        CategoryFactory.create_batch(3)
        AuthorFactory.create()
        user = UserFactory.create()
        book = BookFactory.create()
        book = Book.objects.get(id=book.id)
        relation = UserBookRelationFactory.create(user=user, book=book)
        expected_data = {
            'id': book.id,
            'title': book.title,
            'title_original': book.title_original,
            'year_published': book.year_published,
            'description': book.description,
            'author': book.author_id,
            'categories': [c.id for c in book.categories.all()],
            'in_bookmarks': relation.in_bookmarks,
            'in_wishlist': relation.in_wishlist,
            'rating': relation.rating,
            'price_original': "{:.2f}".format(book.price_original),
            'price': "{:.2f}".format(book.price),
            'discount': "{:.2f}".format(book.discount),
            'discount_total': "{:.2f}".format(book.discount_total),
        }
        actual_data = BookSerializer(book, context=PrefetchUserData.get_extra_context(user)).data
        self.assertEqual(expected_data, actual_data)

    def test_expanded_book_serializer(self):
        CategoryFactory.create_batch(3)
        author = AuthorFactory.create()
        user = UserFactory.create()
        book = BookFactory.create(author=author)
        book = Book.objects.get(id=book.id)
        relation = UserBookRelationFactory.create(user=user, book=book)
        expected_data = {
            'id': book.id,
            'title': book.title,
            'title_original': book.title_original,
            'year_published': book.year_published,
            'description': book.description,
            'author': AuthorSerializer(author).data,
            'categories': CategorySerializer(book.categories.all(), many=True).data,
            'in_bookmarks': relation.in_bookmarks,
            'in_wishlist': relation.in_wishlist,
            'rating': relation.rating,
            'price_original': "{:.2f}".format(book.price_original),
            'price': "{:.2f}".format(book.price),
            'discount': "{:.2f}".format(book.discount),
            'discount_total': "{:.2f}".format(book.discount_total),
        }
        actual_data = ExpandedBookSerializer(book, context=PrefetchUserData.get_extra_context(user)).data
        self.assertEqual(expected_data, actual_data)

    def test_author_serializer(self):
        author = AuthorFactory.create()
        expected_data = {
            'id': author.id,
            'name': author.name,
            'family_name': author.family_name,
            'full_name': author.full_name,
            'about': author.about
        }
        actual_data = AuthorSerializer(author).data
        self.assertEqual(expected_data, actual_data)

    def test_category_serializer(self):
        category = CategoryFactory.create()
        expected_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'book_average_price': category.book_average_price,
            'book_count': category.book_count,
        }
        actual_data = CategorySerializer(category).data
        self.assertEqual(expected_data, actual_data)

    def test_user_book_relation_serializer(self):
        CategoryFactory.create_batch(3)
        AuthorFactory.create()
        book = BookFactory.create()
        user = UserFactory.create()
        relation = UserBookRelationFactory.create(user=user, book=book)

        expected_data = {
            'book': book.id,
            'in_bookmarks': relation.in_bookmarks,
            'in_wishlist': relation.in_wishlist,
            'rating': relation.rating,
        }
        actual_data = UserBookRelationSerializer(relation).data
        self.assertEqual(expected_data, actual_data)

    def test_staff_user_book_relation_serializer(self):
        CategoryFactory.create_batch(3)
        AuthorFactory.create()
        book = BookFactory.create()
        user = UserFactory.create(is_staff=True)
        relation = UserBookRelationFactory.create(user=user, book=book)

        expected_data = {
            'id': relation.id,
            'user': user.id,
            'book': book.id,
            'in_bookmarks': relation.in_bookmarks,
            'in_wishlist': relation.in_wishlist,
            'rating': relation.rating,
        }
        actual_data = StaffBookRelationSerializer(relation).data
        self.assertEqual(expected_data, actual_data)

    def test_expanded_user_book_relation_serializer(self):
        CategoryFactory.create_batch(3)
        AuthorFactory.create()
        book = BookFactory.create()
        user = UserFactory.create(is_staff=True)
        relation = UserBookRelationFactory.create(user=user, book=book)

        expected_data = {
            'book': BookSerializer(book, context=PrefetchUserData.get_extra_context(user)).data,
            'in_bookmarks': relation.in_bookmarks,
            'in_wishlist': relation.in_wishlist,
            'rating': relation.rating,
        }
        actual_data = ExpandedUserBookRelationSerializer(relation,
                                                         context=PrefetchUserData.get_extra_context(user)).data
        self.assertEqual(expected_data, actual_data)
