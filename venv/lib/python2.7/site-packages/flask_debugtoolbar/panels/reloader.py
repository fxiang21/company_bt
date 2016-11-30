import collections
import json
import sys
import traceback
import uuid
from jinja2.exceptions import TemplateSyntaxError

from flask import template_rendered, request, g, render_template_string, Response, current_app, abort, url_for
from flask_debugtoolbar import module
from flask_debugtoolbar.panels import DebugPanel

_ = lambda x: x


token = str(uuid.uuid4())


class ReloaderPanel(DebugPanel):
    """
    """
    name = 'AutoReload'
    has_content = False
    user_activate = True

    def process_request(self, request):
        # TODO put uuid in cookie, or how to send it with response?
        # also need to make sure that it only refreshes on a GET, not POST
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Auto-reload')

    def nav_subtitle(self):
        return 'Reload on code changes'

    def title(self):
        return _('Auto-reload')

    def url(self):
        return ''

    def content(self):
        return ''


@module.route('/reloader/token')
def reloader_token():
    return token
