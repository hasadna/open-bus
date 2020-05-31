import itertools
from google.cloud import firestore
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
from typing import Iterator

from firebase_documents import FirebaseDocument

# make sure you have GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to service account credentials file
# export GOOGLE_APPLICATION_CREDENTIALS="path/to/file"


class BaseCrud:
    NUMBER_OF_ITEMS_IN_SEQUENTIAL_BATCH = 500
    NUMBER_OF_ITEMS_IN_PARALLEL_BATCH = 200

    def __init__(self, connection: firestore.Client, collection_name: str):
        self.connection = connection
        self.collection_name = collection_name

    def _create_document_ref(self, doc_id=None):
        return self.connection.collection(self.collection_name).document(document_id=doc_id)

    def create(self, content: FirebaseDocument, doc_id=None):
        doc_id = doc_id if doc_id else content.get_firebase_id()

        self._create_document_ref(doc_id=doc_id).create(content.to_firebase_dict())

    def read(self, doc_id):
        return self._create_document_ref(doc_id).get()

    def create_multi(self, contents: Iterator[FirebaseDocument], parallel=False):
        if parallel:
            self._create_multi_parallel(contents, num_threads=cpu_count())
        else:
            self._create_multi_sequential(contents)

    def _batch_commit(self, chunk: Iterator[FirebaseDocument]):
        batch = self.connection.batch()
        coll = self.connection.collection(self.collection_name)

        for itm in chunk:
            batch.create(coll.document(itm.get_firebase_id()), itm.to_firebase_dict())
        batch.commit()

    def _create_multi_sequential(self, contents: Iterator[FirebaseDocument]):
        for chunk_of_rides in grouper(self.NUMBER_OF_ITEMS_IN_SEQUENTIAL_BATCH, contents):
            self._batch_commit(chunk_of_rides)

    # 187 sec for creating 12,000 documents with size of a SiriRide doc
    def _create_multi_parallel(self, contents: Iterator[FirebaseDocument], num_threads):
        pool = ThreadPool(num_threads)
        pool.map(self._batch_commit, grouper(self.NUMBER_OF_ITEMS_IN_PARALLEL_BATCH, contents))
        pool.close()
        pool.join()


def grouper(n, iterable: Iterator):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
