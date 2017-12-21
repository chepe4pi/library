from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import tasks
from .models import Book


@receiver(post_save, sender=Book)
def update_book_aggregates(sender, instance, **kwargs):
    categories_ids = [c.id for c in instance.categories.all()]
    tasks.update_book_aggregates.apply_async(
        args=(instance.id,),
        link=tasks.update_book_categories.s(categories_ids)
    )


@receiver(post_delete, sender=Book)
def update_category_aggregated(sender, instance, **kwargs):
    categories_ids = [c.id for c in instance.categories.all()]
    tasks.update_book_categories.apply_async(
        args=(instance.id, categories_ids),
    )
