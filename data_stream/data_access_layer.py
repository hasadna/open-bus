from typing import Dict
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from data_stream.base_classes import SiriRide


class FilterError(ValueError):
    pass


class AlreadyExist(ValueError):
    pass


class MongoCrud:
    """
    implementation of CRUD (create, read, update, and delete) operation for mongo-db
    """
    def __init__(self, mongo_client: MongoClient, database_name: str):
        self.mongo_client = mongo_client
        self.database_name = database_name

    def _get_collection(self, collection_name: str) -> Collection:
        return self.mongo_client.get_database(self.database_name).get_collection(collection_name)

    def create(self, collection_name: str, doc: Dict) -> ObjectId:
        """
        Create new document in given collection.
        :param collection_name: The name of the collection - a string.
        :param doc: The document to insert. Must be a mutable mapping type.
                    If the document does not have an _id field one will be added automatically
        :return: A MongoDB ObjectId.
        """
        return self._get_collection(collection_name).insert_one(doc).inserted_id

    def update(self, collection_name: str, doc_filter: Dict, doc: Dict) -> None:
        """
        Update a single document matching the filter.
        :param collection_name: The name of the collection - a string.
        :param doc_filter: A query that matches the document to update.
        :param doc: The modifications to apply.
        raise FilterError in case document is not exist in database
        """
        if not self._get_collection(collection_name).update_one(doc_filter, {'$set': doc}).matched_count:
            raise FilterError('using given filter found no document to update')

    def read(self, collection_name: str, doc_filter) -> Dict:
        """
        Get a single document from the database.
        :param collection_name: The name of the collection - a string.
        :param doc_filter: a dictionary specifying the query to be performed OR any other type to be used as the value
                            for a query for ``"_id"``.
        :return: Returns a single document, or raise ``FilterError`` if no matching document is found.
        """
        res = self._get_collection(collection_name).find_one(doc_filter)
        if res is None:
            raise FilterError('using given filter found no document to fetch')
        return res

    def find(self, collection_name: str,  *args, **kwargs):
        res = self._get_collection(collection_name).find(*args, **kwargs)
        return res


class SiriRideMongoCrud:

    COLLECTION_NAME = 'siri_rides'
    DOC_ID_KEY = 'id'
    DB_ID_KEY = '_id'

    def __init__(self, mongo_crud: MongoCrud):
        """
        High level implementation of CRUD (create, read, update, and delete) above ``MongoCrud``
        :param mongo_crud: implementation of CRUD (create, read, update, and delete) operation for mongo-db
        """
        self.mongo_crud = mongo_crud

    def create(self, siri_ride: SiriRide) -> ObjectId:
        """
        Create new ``SiriRide`` representation in database.
        :param siri_ride: SiriRide object that represent one ride
        :return: A MongoDB ObjectId.
        :raises: AlreadyExist in case `siri_ride` has db doc_id
        """
        if siri_ride.doc_id is not None:
            raise AlreadyExist("Document is already exist in Database. please use update instead")
        doc = siri_ride.to_json()
        doc.pop(self.DOC_ID_KEY)
        res = self.mongo_crud.create(self.COLLECTION_NAME, doc)
        siri_ride.doc_id = res
        return res

    def update(self, siri_ride: SiriRide) -> None:
        """
        update exist SiriRide record in database
        :param siri_ride: Exist SiriRide object that should switch the record in database
        raise FilterError in case document is not exists in database
        """
        doc = siri_ride.to_json()
        doc.pop(self.DOC_ID_KEY)
        self.mongo_crud.update(self.COLLECTION_NAME, {self.DB_ID_KEY: siri_ride.doc_id}, doc)

    def read(self, doc_id) -> SiriRide:
        """
        Get a SiriRide instance from the database.
        :param doc_id: represent document id in database.
        :return: SiriRide instance with requested id
        :raise: FilterError in case no SiriRide record with given doc_id
        """
        res = self.mongo_crud.read(self.COLLECTION_NAME, doc_id)
        res[self.DOC_ID_KEY] = res.pop(self.DB_ID_KEY)
        return SiriRide.from_json(res)

    def find(self,  *args, **kwargs):
        """
        provide generator over rides that matched the given parameter
        :param args: ``Collection.find``
        :param kwargs: ``Collection.find``
        """
        for doc in self.mongo_crud.find(self.COLLECTION_NAME, *args, **kwargs):
            doc[self.DOC_ID_KEY] = doc.pop(self.DB_ID_KEY)
            yield SiriRide.from_json(doc)
