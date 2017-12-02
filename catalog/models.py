from django.db import models
from django.contrib.auth import get_user_model

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
        return "%s %s" % (self.name, self.family_name)


class Publisher(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    about = models.TextField(blank=True, null=True, verbose_name='Об издателе')

    class Meta:
        verbose_name = 'издатель'
        verbose_name_plural = 'издатели'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


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

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name='Автор')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='books', blank=True, null=True,
                                  verbose_name='Издательство')
    categories = models.ManyToManyField(Category, related_name='books', verbose_name='Категории')

    class Meta:
        verbose_name = 'книга'
        verbose_name_plural = 'книги'

    def __str__(self):
        return self.title


class AbstractUserMark(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='%(class)ss', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        abstract = True


class AbstractUserBookMark(AbstractUserMark):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='%(class)ss', verbose_name='Книга')

    class Meta:
        abstract = True
        unique_together = ('book', 'user')

    def __str__(self):
        return str(self.book)


class AbstractRatingModel(models.Model):
    RATING_VERY_BAD = 0
    RATING_BAD = 1
    RATING_OK = 2
    RATING_GOOD = 3
    RATING_VERY_GOOD = 4

    RATING_CHOICES = (
        (RATING_VERY_BAD, 'Ужасно'),
        (RATING_BAD, 'Плохо'),
        (RATING_OK, 'Так себе'),
        (RATING_GOOD, 'Хорошо'),
        (RATING_VERY_GOOD, 'Отлично'),
    )

    @property
    def rating_human(self):
        for rating, rating_human in self.RATING_CHOICES:
            if rating_human == self.rating:
                return rating_human
        return None

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='Оценка')

    class Meta:
        abstract = True


class WishlistedBook(AbstractUserBookMark):
    pass


class Bookmark(AbstractUserBookMark):
    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Памятка')

    def __str__(self):
        if self.memo:
            return "%s (%s)" % (self.book, self.memo)
        return super().__str__()


class BookRating(AbstractUserBookMark, AbstractRatingModel):
    def __str__(self):
        return "%s (%s)" % (self.rating_human, self.book)
