from django.apps import AppConfig
from django.db.models.signals import m2m_changed


class DjangoDiscourseConnectorConfig(AppConfig):
    name = 'django_discourse_connector'
    verbose_name = 'discourse'
    url_slug = 'discourse'

    def ready(self):
        from .signals import user_group_change_sync_discourse_groups
        from django.contrib.auth.models import User
        m2m_changed.connect(
            user_group_change_sync_discourse_groups, sender=User.groups.through)
