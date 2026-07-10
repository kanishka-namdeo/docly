import logging

logger = logging.getLogger(__name__)

try:
    from gptcache import cache
    from gptcache.adapter import openai as gptcache_openai
    from gptcache.embedding import Onnx
    from gptcache.manager import CacheBase, VectorBase, manager_factory
    from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
    from app.config import settings

    class GPTCacheWrapper:
        def __init__(self):
            # Initialize cache with SQLite backend
            self.data_manager = manager_factory(
                sql_conflict_resolution="replace",
                sqlite_path=str(settings.cache_path),
            )
            
            # Initialize embedding model
            self.embedding = Onnx()
            
            # Initialize cache
            cache.init(
                embedding_func=self.embedding.to_embeddings,
                data_manager=self.data_manager,
                similarity_evaluation=SearchDistanceEvaluation(),
            )
        
        def get_cache(self):
            """Get the cache instance for use with LLM clients."""
            return cache

except ImportError:
    logger.warning("gptcache not installed. GPTCacheWrapper is a stub.")

    class GPTCacheWrapper:
        def __init__(self):
            logger.warning("GPTCacheWrapper initialized in stub mode - no caching available")
        
        def get_cache(self):
            """Get the cache instance for use with LLM clients."""
            logger.warning("GPTCache stub: get_cache called but gptcache not installed")
            return None
