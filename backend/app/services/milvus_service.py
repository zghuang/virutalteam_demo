from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

COLLECTION_NAME = "article_embeddings"
DIMENSION = 384
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530


class MilvusService:
    """Service for interacting with Milvus vector database."""

    def __init__(self, host: str = MILVUS_HOST, port: int = MILVUS_PORT):
        self.host = host
        self.port = port
        self._connected = False

    def _ensure_connected(self):
        """Ensure a connection to Milvus is established."""
        if not self._connected:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
            )
            self._connected = True

    def create_collection(self):
        """Create the article_embeddings collection with id, vector, and text fields."""
        self._ensure_connected()

        if utility.has_collection(COLLECTION_NAME):
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields=fields, description="Article embeddings for semantic search")
        collection = Collection(name=COLLECTION_NAME, schema=schema)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()

    def insert_vector(self, article_id: int, text: str, embedding: list[float]):
        """Insert a single vector with its id and original text into the collection."""
        self._ensure_connected()

        if not utility.has_collection(COLLECTION_NAME):
            self.create_collection()

        collection = Collection(COLLECTION_NAME)
        entities = [
            [article_id],
            [embedding],
            [text],
        ]
        collection.insert(entities)
        collection.flush()

    def search_similar(self, query_embedding: list[float], limit: int = 10) -> list[dict]:
        """Search for the closest matching vectors and return results with id, text, and distance."""
        self._ensure_connected()

        collection = Collection(COLLECTION_NAME)
        collection.load()

        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 16},
        }
        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=limit,
            output_fields=["id", "text"],
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append({
                    "id": hit.entity.get("id"),
                    "text": hit.entity.get("text"),
                    "distance": hit.distance,
                })

        return matches

    def drop_collection(self):
        """Drop the article_embeddings collection."""
        self._ensure_connected()

        if utility.has_collection(COLLECTION_NAME):
            utility.drop_collection(COLLECTION_NAME)
