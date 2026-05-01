import unittest
from unittest.mock import patch, MagicMock
from backend.app.services.milvus_service import (
    MilvusService,
    COLLECTION_NAME,
    DIMENSION,
)


class TestMilvusService(unittest.TestCase):

    def setUp(self):
        self.service = MilvusService()

    @patch("backend.app.services.milvus_service.connections")
    def test_ensure_connected(self, mock_connections):
        self.service._ensure_connected()
        mock_connections.connect.assert_called_once_with(
            alias="default",
            host="localhost",
            port=19530,
        )
        self.assertTrue(self.service._connected)

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.Collection")
    @patch("backend.app.services.milvus_service.connections")
    def test_create_collection_new(self, mock_connections, mock_collection_cls, mock_utility):
        mock_utility.has_collection.return_value = False
        mock_collection = MagicMock()
        mock_collection_cls.return_value = mock_collection

        self.service.create_collection()

        mock_collection_cls.assert_called_once()
        mock_collection.create_index.assert_called_once()
        mock_collection.load.assert_called_once()

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.connections")
    def test_create_collection_already_exists(self, mock_connections, mock_utility):
        mock_utility.has_collection.return_value = True

        self.service.create_collection()

        mock_utility.has_collection.assert_called_once_with(COLLECTION_NAME)

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.Collection")
    @patch("backend.app.services.milvus_service.connections")
    def test_insert_vector(self, mock_connections, mock_collection_cls, mock_utility):
        mock_utility.has_collection.return_value = True
        mock_collection = MagicMock()
        mock_collection_cls.return_value = mock_collection

        self.service.insert_vector(1, "sample text", [0.1] * DIMENSION)

        mock_collection.insert.assert_called_once()
        mock_collection.flush.assert_called_once()

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.Collection")
    @patch("backend.app.services.milvus_service.connections")
    def test_insert_vector_creates_collection_if_missing(self, mock_connections, mock_collection_cls, mock_utility):
        mock_utility.has_collection.side_effect = [False, True]
        mock_collection = MagicMock()
        mock_collection_cls.return_value = mock_collection

        self.service.insert_vector(1, "sample text", [0.1] * DIMENSION)

        self.assertEqual(mock_utility.has_collection.call_count, 2)

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.Collection")
    @patch("backend.app.services.milvus_service.connections")
    def test_search_similar(self, mock_connections, mock_collection_cls, mock_utility):
        mock_utility.has_collection.return_value = True
        mock_hit = MagicMock()
        mock_hit.entity.get.side_effect = lambda key: {"id": 1, "text": "sample text"}[key]
        mock_hit.distance = 0.5

        mock_hits = MagicMock()
        mock_hits.__iter__ = MagicMock(return_value=iter([mock_hit]))

        mock_collection = MagicMock()
        mock_collection.search.return_value = [mock_hits]
        mock_collection_cls.return_value = mock_collection

        results = self.service.search_similar([0.1] * DIMENSION, limit=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["text"], "sample text")
        self.assertEqual(results[0]["distance"], 0.5)

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.connections")
    def test_drop_collection(self, mock_connections, mock_utility):
        mock_utility.has_collection.return_value = True

        self.service.drop_collection()

        mock_utility.drop_collection.assert_called_once_with(COLLECTION_NAME)

    @patch("backend.app.services.milvus_service.utility")
    @patch("backend.app.services.milvus_service.connections")
    def test_drop_collection_when_missing(self, mock_connections, mock_utility):
        mock_utility.has_collection.return_value = False

        self.service.drop_collection()

        mock_utility.drop_collection.assert_not_called()

    def test_constants(self):
        self.assertEqual(COLLECTION_NAME, "article_embeddings")
        self.assertEqual(DIMENSION, 384)


if __name__ == "__main__":
    unittest.main()
