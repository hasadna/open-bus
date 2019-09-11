from google.cloud import firestore

# make sure you have GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to service account credentials file
# export GOOGLE_APPLICATION_CREDENTIALS="path/to/file"

class BaseCrud:
    def __init__(self, connection: firestore.Client, collection_name: str):
        self.connection = connection
        self.collection_name = collection_name

    def create(self, content, doc_id=None):
        self.connection.collection(self.collection_name).document(document_id=doc_id).create(content)


class SiriRideCrud(BaseCrud):

    def __init__(self, connection):
        super().__init__(connection, collection_name='test')

    def create(self, siri_ride, doc_id=None):
        super().create(siri_ride, doc_id=doc_id)


SiriRideCrud(firestore.Client(project='openbus')).create({'foo': 23, 'bar': 45})

