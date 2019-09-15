import itertools
from google.cloud import firestore
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count

# Max 500
NUMBER_OF_ITEMS_IN_ITERABLE_BATCH = 500
NUMBER_OF_ITEMS_IN_PARALLEL_BATCH = 200

# make sure you have GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to service account credentials file
# export GOOGLE_APPLICATION_CREDENTIALS="path/to/file"

class BaseCrud:
    def __init__(self, connection: firestore.Client, collection_name: str):
        self.connection = connection
        self.collection_name = collection_name

    def _collection_ref(self, doc_id=None):
        return self.connection.collection(self.collection_name).document(document_id=doc_id)

    def create(self, content, doc_id=None):
        self._collection_ref(doc_id=doc_id).create(content)

    def read(self, doc_id):
        return self._collection_ref(doc_id).get()

    def create_multi(self, contents, parallel=False):
        if not parallel:
            for chunk_of_rides in grouper(NUMBER_OF_ITEMS_IN_ITERABLE_BATCH, contents):
                self._batch_commit(chunk_of_rides)
            return
        self._create_multi_parallel(contents, num_threads=cpu_count())

    def _batch_commit(self, chunk):
        batch = self.connection.batch()
        coll = self.connection.collection(self.collection_name)
        for itm in chunk:
            batch.create(coll.document(), itm)
        batch.commit()

    # 187 sec for creating 12,000 documents with size of a SiriRide doc
    def _create_multi_parallel(self, contents, num_threads):
        pool = ThreadPool(num_threads)
        pool.map(self._batch_commit, grouper(NUMBER_OF_ITEMS_IN_PARALLEL_BATCH, contents))
        pool.close()
        pool.join()


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
