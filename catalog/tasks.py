from celery import shared_task
from .models import Book, Category
from django.db.models.aggregates import Avg, Count, Sum
from django.db.models.expressions import F, Value
from django.db.models.functions import Cast, Coalesce
from django.db.models import DecimalField


@shared_task
def update_book_aggregates(book_id):
    data = Book.objects.filter(id=book_id).select_related('discount_group').annotate(
        discount_total_new=Coalesce('discount', Value(0)) + Coalesce('discount_group__discount', Value(0)),
        price_new=Cast(
            F('price_original') - (F('price_original') * F('discount_total_new') / Value(100)),
            DecimalField(max_digits=6, decimal_places=2)
        )
    ).first()
    if data:
        Book.objects.filter(id=book_id).update(
            discount_total=data.discount_total_new,
            price=data.price_new,
        )
    return book_id


@shared_task
def update_book_categories(book_id, categories_ids):
    for category_id in categories_ids:
        update_book_category_aggregates.apply_async(args=(category_id,))
    return True


@shared_task
def update_book_category_aggregates(category_id):
    data = Category.objects.filter(id=category_id).annotate(
        book_average_price_new=Avg(
            Cast(
                F('books__price_original') - (F('books__price_original') * (
                    Coalesce('books__discount', Value(0)) +
                    Coalesce('books__discount_group__discount', Value(0))
                ) / Value(100)),
                DecimalField(max_digits=6, decimal_places=2)
            )
        ),
        book_count_new=Count('books')
    ).first()
    if data:
        Category.objects.filter(id=category_id).update(
            book_average_price=data.book_average_price_new,
            book_count=data.book_count_new,
        )
