from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from .models import DiscourseUser, DiscourseGroup
from .tasks import add_discourse_group_to_discourse_user, remove_discourse_group_from_discourse_user

import logging
logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def user_group_change_sync_discourse_groups(sender, **kwargs):
    django_user = kwargs.get('instance')
    action = str(kwargs.get('action'))

    try:
        discourse_user = DiscourseUser.objects.get(user=django_user)
    except DiscourseUser.DoesNotExist:
        logger.info(
            "DiscourseUser not found for %s, skipping group sync" % django_user)
        return

    group_ids = [pk for pk in kwargs.get('pk_set')]

    if action == "post_remove":
        for group_id in group_ids:
            try:
                discourse_group = DiscourseGroup.objects.get(
                    group__id=group_id)
                remove_discourse_group_from_discourse_user.apply_async(
                    args=[discourse_group.external_id, discourse_user.external_id])
            except DiscourseGroup.DoesNotExist:
                logger.info(
                    "DiscourseGroup not found for %s, skipping group sync" % group_id)
    elif action == "post_add":
        for group_id in group_ids:
            try:
                discourse_group = DiscourseGroup.objects.get(
                    group__id=group_id)
                add_discourse_group_to_discourse_user.apply_async(
                    args=[discourse_group.external_id, discourse_user.external_id])
            except DiscourseGroup.DoesNotExist:
                logger.info(
                    "DiscourseGroup not found for %s, skipping group sync" % group_id)
