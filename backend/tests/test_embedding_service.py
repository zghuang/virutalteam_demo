import unittest
from unittest.mock import patch, MagicMock
from backend.app.services.embedding_service import get_embedding, get_embeddings


class TestEmbeddingService(unittest.TestCase):

    @patch("backend.app.services.embedding_service._model")
    def test_get_embedding_returns_list(self, mock_model):
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        result = get_embedding("test text")
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_model.encode.assert_called_once_with("test text")

    @patch("backend.app.services.embedding_service._model")
    def test_get_embeddings_returns_list_of_lists(self, mock_model):
        mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        result = get_embeddings(["text1", "text2"])
        self.assertEqual(result, [[0.1, 0.2], [0.3, 0.4]])
        mock_model.encode.assert_called_once_with(["text1", "text2"])

    @patch("backend.app.services.embedding_service._model")
    def test_get_embedding_with_empty_string(self, mock_model):
        mock_model.encode.return_value = [0.0] * 384
        result = get_embedding("")
        self.assertIsInstance(result, list)

    @patch("backend.app.services.embedding_service._model")
    def test_get_embeddings_with_empty_list(self, mock_model):
        mock_model.encode.return_value = []
        result = get_embeddings([])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
