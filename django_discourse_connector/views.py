from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.apps import apps
from django.contrib.auth.decorators import login_required
from urllib import parse as urlparse
from .models import DiscourseClient, DiscourseUser
import logging
import base64
import hmac
import hashlib
logger = logging.getLogger(__name__)


@login_required
def sso_callback(request):
    """
    I'd like to thank James Potter for the heavy lifting on the SSO example for Django.
    https://meta.discourse.org/t/sso-example-for-django/14258
    """
    discourse_client = DiscourseClient.get_instance()

    payload = request.GET.get('sso')
    signature = request.GET.get('sig')

    if None in [payload, signature]:
        return HttpResponseBadRequest('No SSO payload or signature. Please contact support if this problem persists.')

    # Validate the payload
    try:
        payload = bytes(urlparse.unquote(payload), encoding='utf-8')
        decoded = base64.decodestring(payload).decode('utf-8')
        assert 'nonce' in decoded
        assert len(payload) > 0
    except AssertionError:
        return HttpResponseBadRequest('1 Invalid payload. Please contact support if this problem persists.')

    key = bytes(discourse_client.sso_secret,
                encoding='utf-8')  # must not be unicode
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if this_signature != signature:
        return HttpResponseBadRequest('Signature: %s || Signature: %s' % (this_signature, signature))

    # Build the return payload
    qs = urlparse.parse_qs(decoded)
    params = {
        'nonce': qs['nonce'][0],
        'email': request.user.email,
        'external_id': request.user.pk,
        'username': request.user.username,
        'require_activation': 'false',
    }

    return_payload = base64.encodestring(
        bytes(urlparse.urlencode(params), 'utf-8'))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
    query_string = urlparse.urlencode(
        {'sso': return_payload, 'sig': h.hexdigest()})

    DiscourseUser.objects.get_or_create(
        user=request.user, username=request.user.username, external_id=request.user.pk)

    url = '%s/session/sso_login' % discourse_client.forum_url
    return HttpResponseRedirect('%s?%s' % (url, query_string))
