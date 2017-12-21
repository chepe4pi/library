from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'
    verbose_name = 'Каталог книг'

    def ready(self):
        from . import signals
