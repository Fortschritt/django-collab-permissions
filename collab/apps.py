from django.apps import AppConfig


class DjangoCollabConfig(AppConfig):
    name = 'collab'

    def ready(self):
        # register our signals
        from . import signals
        # activate activity streams for Spaces
        from actstream import registry
        from spaces.models import Space
        registry.register(Space)