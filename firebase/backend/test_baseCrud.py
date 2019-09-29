import unittest
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import call
from firebase_crud import BaseCrud, grouper

from firebase_documents import Point


# noinspection PyTypeChecker,PyUnresolvedReferences
class TestBaseCrud(TestCase):

    def setUp(self):
        pass

    def test__collection_ref(self):
        # Arrange

        expected_doc_id = 'foo'
        expected_collection_name = 'bar'
        mock_conn = MagicMock()

        crud = BaseCrud(mock_conn, collection_name=expected_collection_name)

        # Act
        crud._create_document_ref(doc_id=expected_doc_id)

        # Assert
        expected_conn_call_list = call.collection(expected_collection_name).document(document_id=expected_doc_id)\
            .call_list()

        self.assertEqual(expected_conn_call_list, mock_conn.mock_calls)

    def test_create(self):
        # Arrange
        expected_doc_id = 'foo'
        expected_content = Point(1.1, 2.2)
        mock_conn = MagicMock()

        crud = BaseCrud(None, None)
        crud._create_document_ref = mock_conn

        # Expected
        expected_conn_call_list = call(doc_id=expected_doc_id).create(expected_content.to_firebase_dict()).call_list()

        # Act
        crud.create(content=expected_content, doc_id=expected_doc_id)

        # Assert
        self.assertEqual(expected_conn_call_list, mock_conn.mock_calls)

    def test_create_use_get_firebase_id(self):
        # Arrange
        expected_doc_id = 'foo'
        expected_content = Point(1.1, 2.2)
        expected_content.get_firebase_id = lambda: expected_doc_id
        mock_conn = MagicMock()

        crud = BaseCrud(None, None)
        crud._create_document_ref = mock_conn

        # Expected
        expected_conn_call_list = call(doc_id=expected_doc_id).create(expected_content.to_firebase_dict()).call_list()

        # Act
        crud.create(content=expected_content)

        # Assert
        self.assertEqual(expected_conn_call_list, mock_conn.mock_calls)

    def test_read(self):
        # Arrange
        doc_id = 'foo'
        crud = BaseCrud(None, None)
        crud._create_document_ref = MagicMock()

        # Expect
        expected_conn_call_list = call(doc_id).get().call_list()

        # Act
        crud.read(doc_id=doc_id)

        # Assert
        self.assertEqual(expected_conn_call_list, crud._create_document_ref.mock_calls)

    def test_grouper(self):
        # Expect
        expected = [(0, 1), (2,)]

        # Act
        actual = [i for i in grouper(2, range(3))]

        # Assert
        self.assertEqual(expected, actual)

    def test_create_multi_calls__create_multi_sequential(self):
        # Arrange
        crud = BaseCrud(None, None)
        crud._create_multi_sequential = MagicMock()

        # Act
        crud.create_multi([{}], parallel=False)

        # Assert
        self.assertTrue(crud._create_multi_sequential.called)

    def test_create_multi_calls__create_multi_sequential_as_default(self):
        # Arrange
        crud = BaseCrud(None, None)
        crud._create_multi_sequential = MagicMock()

        # Act
        crud.create_multi([{}])

        # Assert
        self.assertTrue(crud._create_multi_sequential.called)

    def test_create_multi_calls__create_multi_parallel(self):
        # Arrange
        crud = BaseCrud(None, None)
        crud._create_multi_parallel = MagicMock()

        # Act
        crud.create_multi([{}], parallel=True)

        # Assert
        self.assertTrue(crud._create_multi_parallel.called)

    def test__batch_commit_calls_to_conn_batch(self):
        # Arrange
        # mock conn.collection
        collection_ref = MagicMock()
        collection_ref.document = lambda x: ('doc_ref', x)
        conn = MagicMock()
        conn.collection = lambda x: collection_ref
        # mock conn.batch
        batch_session = MagicMock()
        batch_session_create_method = MagicMock()
        batch_session.create = batch_session_create_method
        conn.batch = lambda: batch_session

        crud = BaseCrud(conn, None)

        doc = Point(1.2, 2.1)
        doc.to_firebase_dict = lambda: dict(foo='bar')
        expected_doc_ref = ('doc_ref', doc.get_firebase_id())

        # Act

        crud._batch_commit([doc])

        # Assert
        batch_session_create_method.assert_called_with(expected_doc_ref, doc.to_firebase_dict())

    def test_create_multi_sequential__calls_to__batch_commit(self):
        # Arrange
        crud = BaseCrud(None, None)
        _batch_commit_method = MagicMock()
        crud._batch_commit = _batch_commit_method
        expected_calls = 8
        docs = [Point(1.1, 1.1) for _ in range(crud.NUMBER_OF_ITEMS_IN_SEQUENTIAL_BATCH * expected_calls)]
        # Act
        crud._create_multi_sequential(docs)

        self.assertEqual(expected_calls, _batch_commit_method.call_count)

    def test_create_multi_parallel__calls_to__batch_commit(self):
        # Arrange
        crud = BaseCrud(None, None)
        _batch_commit_method = MagicMock()
        crud._batch_commit = _batch_commit_method
        expected_calls = 8
        docs = [Point(1.1, 1.1) for _ in range(crud.NUMBER_OF_ITEMS_IN_PARALLEL_BATCH * expected_calls)]
        # Act
        crud._create_multi_parallel(docs, 4)

        self.assertEqual(expected_calls, _batch_commit_method.call_count)


if __name__ == '__main__':
    unittest.main()
