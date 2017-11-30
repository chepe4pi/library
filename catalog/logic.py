from django.contrib.auth.models import AnonymousUser


def in_bookmarks(book, user):
    if isinstance(user, AnonymousUser):
        return False
    return bool(book.bookmarks.filter(user=user).first())
