from django.contrib.auth.models import AnonymousUser
from catalog.models import Book
from decimal import Decimal


def in_bookmarks(book, user):
    if isinstance(user, AnonymousUser):
        return False
    return bool(book.bookmarks.filter(user=user).first())


def book_total_discount(book: Book):
    total_discount = book.discount
    if book.discount_group:
        total_discount += book.discount_group.discount
    return min(total_discount, Decimal(100))


def book_price_with_discount(book: Book):
    return Decimal(book.price * (100 - book_total_discount(book))) / 100
