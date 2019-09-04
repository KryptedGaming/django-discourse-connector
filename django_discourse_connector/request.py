import json
import requests


class DiscourseRequest():
    def __init__(self, forum_url=None, api_key=None, api_username=None, sso_secret=None, settings=None):
        if settings:
            self.forum_url = str(settings['forum_url'])
            self.api_key = str(settings['api_key'])
            self.api_username = str(settings['api_username'])
            self.sso_secret = str(settings['sso_secret'])
        else:
            self.forum_url = forum_url
            self.api_key = api_key
            self.api_username = api_username
            self.sso_secret = sso_secret

    @staticmethod
    def get_instance():
        from .models import DiscourseClient
        return DiscourseRequest(settings=DiscourseClient.get_instance().serialize())

    def get_discourse_user(self, discourse_user_id):
        url = "%s/u/by-external/%s.json" % (self.forum_url,
                                            str(discourse_user_id))
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
        }
        response = requests.get(
            url=url,
            data=data
        )
        return response

    def get_groups(self):
        url = self.forum_url + "/groups.json"
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
        }
        response = requests.get(url=url, data=data)
        return response

    def add_group_to_discourse_user(self, group_id, username):
        url = self.forum_url + \
            "/groups/" + str(group_id) + "/members.json"
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
            'usernames': username.replace(" ", "_")
        }
        response = requests.put(url=url, data=data)
        return response

    def remove_group_from_discourse_user(self, group_id, username):
        url = self.forum_url + \
            "/groups/" + str(group_id) + "/members.json"
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
            'username': username
        }
        response = requests.delete(url=url, data=data)
        return response

    def add_group_to_discourse_server(self, group_name):
        url = self.forum_url + "/admin/groups"
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
            'group[name]': group_name
        }
        response = requests.post(url=url, data=data)
        return response

    def remove_group_from_discourse_server(self, group_external_id):
        url = self.forum_url + \
            "/admin/groups/" + str(group_external_id) + ".json"
        data = {
            'api_key': self.api_key,
            'api_username': self.api_username,
        }
        response = requests.delete(url=url, data=data)
        return response
