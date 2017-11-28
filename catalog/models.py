from django.db import models


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
