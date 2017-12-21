from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import tasks
from .models import Book, Category, DiscountGroup


@receiver(post_save, sender=Book)
def book_post_save(sender, instance, **kwargs):
    categories_ids = [c.id for c in instance.categories.all()]
    tasks.update_book_aggregates.apply_async(
        args=(instance.id,),
        link=tasks.update_book_categories.s(categories_ids)
    )


@receiver(post_delete, sender=Book)
def book_post_delete(sender, instance, **kwargs):
    categories_ids = [c.id for c in instance.categories.all()]
    tasks.update_book_categories.apply_async(
        args=(instance.id, categories_ids),
    )


@receiver(post_save, sender=Category)
def category_post_save(sender, instance, **kwargs):
    tasks.update_book_category_aggregates.apply_async(
        args=(instance.id,),
    )


@receiver([post_save, post_delete], sender=DiscountGroup)
def discount_group_change(sender, instance, **kwargs):
    for book in instance.books.all():
        tasks.update_book_aggregates.apply_async(
            args=(book.id,),
        )
