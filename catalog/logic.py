from django.contrib.auth.models import AnonymousUser
from decimal import Decimal


def in_bookmarks(book, user):
    if isinstance(user, AnonymousUser):
        return False
    return bool(book.bookmarks.filter(user=user).first())


def book_total_discount(book):
    total_discount = book.discount or 0
    if book.discount_group:
        total_discount += book.discount_group.discount
    return min(total_discount, Decimal(100))


def book_price_with_discount(book):
    if book.price_original is None:
        return None
    return Decimal(book.price_original * (100 - book_total_discount(book))) / 100
