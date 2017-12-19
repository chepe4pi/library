from django.contrib.auth.models import AnonymousUser
from decimal import Decimal


def in_bookmarks(book, user):
    if isinstance(user, AnonymousUser):
        return False
    relation = book.userbookrelations.filter(user=user).first()
    return getattr(relation, 'in_bookmarks', False)
