from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import tasks
from .models import Book


@receiver(post_save, sender=Book)
def update_book_aggregates(sender, instance, **kwargs):
    tasks.update_book_aggregates.apply_async(
        args=(instance.id,),
        link=tasks.update_book_categories.s()
    )
