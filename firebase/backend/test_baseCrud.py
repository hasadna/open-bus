from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import call
from firebase_crud import BaseCrud, grouper


# noinspection PyTypeChecker
class TestBaseCrud(TestCase):

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
        expected_content = {}
        mock_conn = MagicMock()

        crud = BaseCrud(None, None)
        crud._create_document_ref = mock_conn

        # Expected
        expected_conn_call_list = call(doc_id=expected_doc_id).create(expected_content).call_list()

        # Act
        crud.create(content=expected_content, doc_id=expected_doc_id)

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
