from django.db import models
from django.contrib.auth.models import User, Group
from .request import DiscourseRequest


class DiscourseClient(models.Model):
    forum_url = models.URLField()
    callback_url = models.URLField()
    api_key = models.CharField(max_length=255)
    api_username = models.CharField(max_length=255, default="system")
    sso_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.forum_url

    @staticmethod
    def get_instance():
        if not DiscourseClient.objects.all().count() >= 1:
            raise Exception(
                "Must create a DiscourseClient object before using Discourse Connector")
        return DiscourseClient.objects.all()[0]

    def serialize(self):
        settings = {}
        settings['forum_url'] = self.forum_url
        settings['api_key'] = self.api_key
        settings['api_username'] = self.api_username
        settings['sso_secret'] = self.sso_secret

        return settings


class DiscourseUser(models.Model):
    external_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="discourse_user")
    groups = models.ManyToManyField("DiscourseGroup", blank=True)

    def save(self, *args, **kwargs):
        self.username = DiscourseRequest.get_instance().get_discourse_user(
            self.external_id).json()['user']['username']
        super(DiscourseUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class DiscourseGroup(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.BigIntegerField(unique=True)
    group = models.ForeignKey(
        Group, null=True, on_delete=models.SET_NULL, related_name="discourse_group")

    def __str__(self):
        if self.group:
            return "<%s:%s>" % (self.name, self.group.name)
        return "<%s>" % self.name
