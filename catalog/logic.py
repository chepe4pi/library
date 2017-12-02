from django.contrib.auth.models import AnonymousUser


def in_bookmarks(book, user):
    if isinstance(user, AnonymousUser):
        return False
    return bool(book.bookmarks.filter(user=user).first())


def rating_human(model):
    for rating, rating_human in model.RATING_CHOICES:
        if rating == model.rating:
            return rating_human
