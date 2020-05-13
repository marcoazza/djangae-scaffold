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
