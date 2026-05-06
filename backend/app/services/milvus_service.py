"""Milvus vector database service (lazy-loaded for Docker)."""

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
        self._pymilvus = None

    def _import_pymilvus(self):
        if self._pymilvus is None:
            try:
                import pymilvus
                self._pymilvus = pymilvus
            except ImportError:
                raise RuntimeError(
                    "pymilvus is not installed. "
                    "Install with: pip install pymilvus"
                )

    def _ensure_connected(self):
        self._import_pymilvus()
        if not self._connected:
            self._pymilvus.connections.connect(
                alias="default", host=self.host, port=self.port,
            )
            self._connected = True

    def create_collection(self):
        self._import_pymilvus()
        self._ensure_connected()
        utility, Collection = self._pymilvus.utility, self._pymilvus.Collection
        CollectionSchema, FieldSchema = self._pymilvus.CollectionSchema, self._pymilvus.FieldSchema
        DataType = self._pymilvus.DataType

        if utility.has_collection(COLLECTION_NAME):
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields=fields, description="Article embeddings")
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        collection.create_index(field_name="vector", index_params={
            "index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128},
        })
        collection.load()

    def insert_vector(self, article_id: int, text: str, embedding: list[float]):
        self._import_pymilvus()
        self._ensure_connected()
        if not self._pymilvus.utility.has_collection(COLLECTION_NAME):
            self.create_collection()
        collection = self._pymilvus.Collection(COLLECTION_NAME)
        collection.insert([[article_id], [embedding], [text]])
        collection.flush()

    def search_similar(self, query_embedding: list[float], limit: int = 10) -> list[dict]:
        self._import_pymilvus()
        self._ensure_connected()
        collection = self._pymilvus.Collection(COLLECTION_NAME)
        collection.load()

        results = collection.search(
            data=[query_embedding], anns_field="vector",
            param={"metric_type": "L2", "params": {"nprobe": 16}},
            limit=limit, output_fields=["id", "text"],
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append({
                    "id": hit.entity.get("id"), "text": hit.entity.get("text"),
                    "distance": hit.distance,
                })
        return matches

    def drop_collection(self):
        self._import_pymilvus()
        self._ensure_connected()
        if self._pymilvus.utility.has_collection(COLLECTION_NAME):
            self._pymilvus.utility.drop_collection(COLLECTION_NAME)
