from celery import shared_task
from django.conf import settings
from .models import DiscourseUser, DiscourseGroup
from .request import DiscourseRequest
from http.client import responses
import logging

logger = logging.getLogger(__name__)




@shared_task
def sync_discourse_users():
    for discourse_user in DiscourseUser.objects.all():
        sync_discourse_user_groups.apply_async(
            args=[discourse_user.external_id])


@shared_task
def sync_discourse_groups():
    discourse_request = DiscourseRequest.get_instance()
    response = discourse_request.get_groups()

    if responses[response.status_code] != "OK":
        logger.error("Error calling Discourse API: %s" % response.json())
        return

    discourse_remote_groups = response.json()['groups']
    discourse_local_groups = DiscourseGroup.objects.all()

    discourse_remote_group_ids = set([group['id']
                                      for group in discourse_remote_groups])
    discourse_local_group_ids = set(DiscourseGroup.objects.all(
    ).values_list('external_id', flat=True))

    discourse_group_ids_to_add = discourse_remote_group_ids - discourse_local_group_ids
    discourse_group_ids_to_remove = discourse_local_group_ids - discourse_remote_group_ids

    for discourse_group in discourse_remote_groups:
        if discourse_group['id'] in discourse_group_ids_to_add:
            local_discourse_group = DiscourseGroup.objects.get_or_create(
                external_id=discourse_group['id'])[0]
            local_discourse_group.name = discourse_group['name']
            local_discourse_group.save()

    for discourse_group_id in discourse_group_ids_to_remove:
        DiscourseGroup.objects.get(external_id=discourse_group_id).delete()


@shared_task
def sync_discourse_user_groups(discourse_user_id):
    discourse_request = DiscourseRequest.get_instance()
    discourse_user = DiscourseUser.objects.get(external_id=discourse_user_id)
    response = discourse_request.get_discourse_user(discourse_user_id)

    if responses[response.status_code] != "OK":
        logger.error("Error calling Discourse API: %s" % response.json())

    discourse_remote_user_groups = response.json()['user']['groups']
    discourse_local_user_groups = discourse_user.groups.all()

    discourse_remote_user_group_ids = set([group['id']
                                           for group in discourse_remote_user_groups])

    discourse_local_user_group_ids = set(
        discourse_user.groups.all().values_list('external_id', flat=True))

    # test value DJANGO_DISCOURSE_REMOTE_PRIORITY in settings, but make it optional
    try:
        if settings.DJANGO_DISCOURSE_REMOTE_PRIORITY:
            remote_priority = True
        else:
            remote_priority = False
    except AttributeError:
        remote_priority = False

    # build lists based on priority
    if remote_priority:
        discourse_groups_to_add = discourse_remote_user_group_ids - \
            discourse_local_user_group_ids
        discourse_groups_to_remove = discourse_local_user_group_ids - \
            discourse_remote_user_group_ids
    else:
        discourse_groups_to_add = discourse_local_user_group_ids - \
            discourse_remote_user_group_ids
        discourse_groups_to_remove = discourse_remote_user_group_ids - \
            discourse_local_user_group_ids

    # action based on priority
    if remote_priority:
        for discourse_group_id in discourse_groups_to_add:
            discourse_group = DiscourseGroup.objects.get(
                external_id=discourse_group_id)
            discourse_user.groups.add(
                DiscourseGroup.get_or_create(external_id=discourse_group_id))
            if discourse_group.group and discourse_group.group not in discourse_user.user.groups.all():
                discourse_user.user.groups.add(discourse_group.group)
        for discourse_group_id in discourse_groups_to_remove:
            discourse_group = DiscourseGroup.objects.get(
                external_id=discourse_group_id)
            discourse_user.groups.remove(
                DiscourseGroup.get_or_create(external_id=discourse_group_id))
            if discourse_group.group and discourse_group.group in discourse_user.user.groups.all():
                discourse_user.user.groups.remove(discourse_group.group)
    else:
        for discourse_group_id in discourse_groups_to_add:
            add_discourse_group_to_discourse_user.apply_async(
                args=[discourse_group_id, discourse_user.external_id])
        for discourse_group_id in discourse_groups_to_remove:
            remove_discourse_group_from_discourse_user.apply_async(
                args=[discourse_group_id, discourse_user.external_id])


@shared_task
def add_discourse_group_to_discourse_user(discourse_group_id, discourse_user_id):
    discourse_request = DiscourseRequest.get_instance()
    discourse_user = DiscourseUser.objects.get(external_id=discourse_user_id)
    discourse_group = DiscourseGroup.objects.get_or_create(
        external_id=discourse_group_id)[0]
    response = discourse_request.add_group_to_discourse_user(
        discourse_group_id, discourse_user.username)

    if responses[response.status_code] == "OK":
        discourse_user.groups.add(discourse_group)
        if discourse_group.group and discourse_group.group not in discourse_user.user.groups.all():
            discourse_user.user.groups.add(discourse_group.group)
    elif responses[response.status_code] == "Too Many Requests":
        logger.warning(
            "Ratelimit calling Discourse API, retrying: %s" % response.json())
        add_discourse_group_to_discourse_user.apply_async(
            args=[discourse_group_id, discourse_user_id], countdown=600)
    else:
        logger.error("Failed to call Discourse API: %s" % response.json())


@shared_task
def remove_discourse_group_from_discourse_user(discourse_group_id, discourse_user_id):
    discourse_request = DiscourseRequest.get_instance()
    discourse_user = DiscourseUser.objects.get(external_id=discourse_user_id)
    discourse_group = DiscourseGroup.objects.get_or_create(
        external_id=discourse_group_id)[0]
    response = discourse_request.remove_group_from_discourse_user(
        discourse_group_id, discourse_user.username)

    if responses[response.status_code] == "OK":
        discourse_user.groups.remove(discourse_group)
        if discourse_group.group and discourse_group.group in discourse_user.user.groups.all():
            discourse_user.user.groups.remove(discourse_group.group)
    elif responses[response.status_code] == "Too Many Requests":
        logger.warning(
            "Ratelimit calling Discourse API, retrying: %s" % response.json())
        remove_discourse_group_from_discourse_user.apply_async(
            args=[discourse_group_id, discourse_user_id], countdown=600)
    else:
        logger.error("Failed to call Discourse API: %s" % response.json())
