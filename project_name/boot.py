import sys
from os.path import dirname, abspath, join, exists

PROJECT_DIR = dirname(dirname(abspath(__file__)))
SITEPACKAGES_DIR = join(PROJECT_DIR, "sitepackages")
DEV_SITEPACKAGES_DIR = join(SITEPACKAGES_DIR, "dev")
PROD_SITEPACKAGES_DIR = join(SITEPACKAGES_DIR, "prod")
APPENGINE_DIR = join(DEV_SITEPACKAGES_DIR, "google_appengine")



def fix_path(include_dev_libs_path=False):
    """ Insert libs folder(s) and SDK into sys.path. The one(s) inserted last take priority. """
    if include_dev_libs_path:
        if exists(APPENGINE_DIR) and APPENGINE_DIR not in sys.path:
            sys.path.insert(1, APPENGINE_DIR)

        if DEV_SITEPACKAGES_DIR not in sys.path:
            sys.path.insert(1, DEV_SITEPACKAGES_DIR)

    if SITEPACKAGES_DIR not in sys.path:
        sys.path.insert(1, PROD_SITEPACKAGES_DIR)


def register_custom_checks():
    from . import checks
    from django.core.checks import register, Tags
    register(checks.check_csp_sources_not_unsafe, Tags.security, deploy=True)
    register(checks.check_session_csrf_enabled, Tags.security)
    register(checks.check_csp_is_not_report_only, Tags.security)
    register(checks.check_cached_template_loader_used, Tags.caches, deploy=True)


def get_app_config(db):
    """Returns the application configuration, creating it if necessary."""
    from django.utils.crypto import get_random_string
    from google.auth.credentials import AnonymousCredentials
    from google.cloud import datastore
    from google.cloud.exceptions import Unauthorized
    import os
    import requests
    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

    gclient = datastore.Client(
        namespace=db.get("NAMESPACE"),
        project=db["PROJECT"],
        credentials=AnonymousCredentials(),
        _http=requests.Session if os.environ.get('GCD_HOST') else None,
    )
    try:
        with gclient.transaction():
            conf_key = gclient.key('Conf', 'conf')
            entity = gclient.get(conf_key)
            if not entity.get('secret_key'):
                entity = datastore.Entity(key=conf_key)
                entity.update({
                    'secret_key': get_random_string(50, allowed_chars)
                })
                gclient.put(entity)
            return entity
    except Unauthorized:
        # datastore might not be started yet
        pass
