import urlparse
from s3_folder_storage.s3 import DefaultStorage, StaticStorage
from django.conf import settings


def domain(url):
    return urlparse.urlparse(url).hostname


class StaticFilesStorage(StaticStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        super(StaticFilesStorage, self).__init__(*args, **kwargs)
