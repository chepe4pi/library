from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.db.models.aggregates import Avg, Count, Sum
from django.db.models.expressions import F, Value
from django.db.models.functions import Cast, Coalesce

UserModel = get_user_model()


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    family_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Фамилия')
    about = models.TextField(blank=True, null=True, verbose_name='Об авторе')

    class Meta:
        verbose_name = 'автор'
        verbose_name_plural = 'авторы'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return "{} {}".format(self.name, self.family_name)


class Publisher(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    about = models.TextField(blank=True, null=True, verbose_name='Об издателе')

    class Meta:
        verbose_name = 'издатель'
        verbose_name_plural = 'издатели'

    def __str__(self):
        return self.name


class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            book_average_price=Avg(
                Cast(
                    F('books__price_original') - (F('books__price_original') * (
                        Coalesce('books__discount', Value(0)) +
                        Coalesce('books__discount_group__discount', Value(0))
                    ) / Value(100)),
                    models.DecimalField(max_digits=6, decimal_places=2)
                )
            ),
            book_count=Count('books')
        )


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    objects = CategoryManager()

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class DiscountGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    discount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Скидка в процентах')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'группа скидок'
        verbose_name_plural = 'группы скидок'

    def __str__(self):
        return self.name


class BookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            discount_total=Coalesce('discount', Value(0)) + Coalesce('discount_group__discount', Value(0)),
            price=Cast(
                F('price_original') - (F('price_original') * F('discount_total') / Value(100)),
                models.DecimalField(max_digits=6, decimal_places=2)
            )
        )


class Book(models.Model):
    COVER_TYPE_HARDBACK = 0
    COVER_TYPE_PAPERBACK = 1
    COVER_TYPE_CHOICES = [
        (COVER_TYPE_HARDBACK, 'Твердая обложка'),
        (COVER_TYPE_PAPERBACK, 'Мягкая обложка')
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    title_original = models.CharField(max_length=255, verbose_name='Оригинальное название')
    year_published = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Год выпуска')
    description = models.TextField(blank=True, null=True, verbose_name='Краткое описание')
    isbn = models.CharField(max_length=17, blank=True, null=True, verbose_name='ISBN')
    cover_type = models.PositiveSmallIntegerField(choices=COVER_TYPE_CHOICES, blank=True, null=True,
                                                  verbose_name='Тип обложки')
    price_original = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                         verbose_name='Цена без учета скидки')
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                   verbose_name='Скидка в процентах')

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name='Автор')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='books', blank=True, null=True,
                                  verbose_name='Издательство')
    categories = models.ManyToManyField(Category, blank=True, related_name='books', verbose_name='Категории')
    discount_group = models.ForeignKey(DiscountGroup, on_delete=models.SET_NULL, related_name='books', blank=True,
                                       null=True, verbose_name='Группа скидок')

    objects = BookManager()

    class Meta:
        verbose_name = 'книга'
        verbose_name_plural = 'книги'

    def __str__(self):
        return self.title


class UserBookRelation(models.Model):
    RATING_VERY_BAD = 1
    RATING_BAD = 2
    RATING_OK = 3
    RATING_GOOD = 4
    RATING_VERY_GOOD = 5

    RATING_CHOICES = (
        (RATING_VERY_BAD, 'Ужасно'),
        (RATING_BAD, 'Плохо'),
        (RATING_OK, 'Так себе'),
        (RATING_GOOD, 'Хорошо'),
        (RATING_VERY_GOOD, 'Отлично'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='%(class)ss',
                             verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='%(class)ss', verbose_name='Книга')
    in_bookmarks = models.BooleanField(default=False, verbose_name='В закладках')
    in_wishlist = models.BooleanField(default=False, verbose_name='В списке желаний')
    rating = models.PositiveSmallIntegerField(blank=True, null=True, choices=RATING_CHOICES, verbose_name='Рейтинг')

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return str(self.book)
