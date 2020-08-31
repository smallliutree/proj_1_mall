from django.core.files.storage import Storage

class MyStorage(Storage):

    pass

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_lenth=None):
        pass

    def url(self, name):

        return 'http://192.168.180.136:8888/' + name

