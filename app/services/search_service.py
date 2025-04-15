from typing import List, Tuple, Dict, Any
from pymilvus import Collection, connections, utility
from ..core.config import settings, embedder, cohere_client
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Connect to Milvus
try:
    connections.connect("default", uri=settings.ZILLZ_URI, token=settings.ZILLZ_TOKEN)
    logger.info("Connected to Milvus successfully")
except Exception as e:
    logger.error(f"Failed to connect to Milvus: {str(e)}")
    raise

# Get collection
collection_name = "job_listings1"  # Make sure this matches the name used in data ingestion
try:
    # Check if collection exists
    if collection_name not in utility.list_collections():
        logger.error(f"Collection '{collection_name}' does not exist in Milvus")
        raise ValueError(f"Collection '{collection_name}' does not exist in Milvus")
    
    collection = Collection(collection_name)
    logger.info(f"Collection '{collection_name}' retrieved successfully")
    
    # Load collection into memory
    collection.load()
    logger.info(f"Collection '{collection_name}' loaded into memory")
except Exception as e:
    logger.error(f"Failed to load collection: {str(e)}")
    raise

def get_relevant_ids(
    query: str,
    collection: Collection,
    count: int = 10,
    offset: int = 10,
    exclude_citizen_only: bool = False,
    degree: List[str] = None,
    remote: bool = None,
    location_state: List[str] = None,
    employment_type: List[str] = None
) -> Tuple[List[str], List[float], List[str], List[Dict[str, Any]]]:
    """
    Find relevant job listings based on query and filters
    """
    try:
        # Ensure collection is loaded
        if not collection.is_empty and not collection.has_index():
            logger.warning("Collection has no index. Creating index on job_description_vector field")
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="job_description_vector", index_params=index_params)
            logger.info("Index created successfully")
        
        query_vector = embedder.encode(query).tolist()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
            "offset": offset,
        }
        
        bool_expr = []

        if exclude_citizen_only:
            bool_expr.append(f"citizenship == False")
        if degree:
            bool_expr.append(f"degree in {degree}")
        if remote is not None:
            bool_expr.append(f"remote == {remote}")
        if location_state and 'All' not in location_state:
            bool_expr.append(f"location_state in {location_state}")
        if employment_type:
            if 'Full-time' in employment_type or 'Part-time' in employment_type:
                bool_expr.append(f"employment_type in {employment_type + ['Full-time and Part-time']}")
            else:
                bool_expr.append(f"employment_type in {employment_type}")

        bool_expr = " and ".join(bool_expr) if bool_expr else ""
        
        search_results = collection.search(
            data=[query_vector],
            anns_field="job_description_vector",
            param=search_params,
            limit=count,
            expr=bool_expr,
            output_fields=["*"],
            consistency_level="Strong"
        )
        
        ids, distances, docs, metadatas = [], [], [], []
        for hit in search_results[0]:
            ids.append(hit.id)
            distances.append(hit.distance)
            docs.append(hit.entity.get("job_description_raw"))
            # raw_info = hit.entity.get('info').split("|")
            job_title = hit.entity.get('job_title')
            job_location = hit.entity.get('job_location')
            company = hit.entity.get('employer_name')

            metadata = {
                "job_title": job_title,
                "job_location": job_location,
                "company": company,
                "degree": hit.entity.get('degree'),
                "remote": hit.entity.get('remote'),
                "location_state": hit.entity.get('location_state'),
                "employment_type": hit.entity.get('employment_type'),
                "citizen": hit.entity.get('citizenship'),
                "link": hit.entity.get('job_apply_link'),
                "job_post_date": hit.entity.get('job_posted_at_datetime'),
                "job_posted_at": hit.entity.get('job_posted_at')
            }
            metadatas.append(metadata)

        return ids, distances, docs, metadatas
    except Exception as e:
        logger.error(f"Error in get_relevant_ids: {str(e)}")
        raise

def rerank_results(query: str, docs: List[str], n: int = 3) -> Any:
    """
    Rerank search results using Cohere
    """
    if not docs:
        logger.warning("No documents available for reranking.")
        return None
    
    try:
        return cohere_client.rerank(
            model='rerank-english-v2.0',
            query=query,
            documents=docs,
            top_n=n
        )
    except Exception as e:
        logger.error(f"Error in rerank_results: {str(e)}")
        return None

def get_latest_jobs(collection: Collection, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the latest job listings without any filtering, sorted by posting date
    """
    try:
        # Ensure collection is loaded
        if not collection.is_empty:
            # Query the collection and sort by job posting timestamp in descending order
            results = collection.query(
                expr="",
                output_fields=["*"],
                limit=limit,
                consistency_level="Strong",
                sort_fields=["job_posted_at"],
                sort_orders=["DESC"]
            )
            
            # Format the results
            jobs = []
            for result in results:
                job_title = result.get("job_title", "")
                job_location = result.get("job_location", "")
                company = result.get("employer_name", "")
                
                job = {
                    "job_id": result.get("job_id"),
                    "job_title": job_title,
                    "job_location": job_location,
                    "company": company,
                    "description": result.get("job_description_raw"),
                    "score": 1.0,  # Default score since we're not doing similarity search
                    "degree": result.get("degree"),
                    "remote": result.get("remote"),
                    "location_state": result.get("location_state"),
                    "employment_type": result.get("employment_type"),
                    "citizen": result.get("citizenship"),
                    "link": result.get("job_apply_link"),
                    "job_post_date": result.get("job_posted_at_datetime"),  # Use the human-readable datetime
                    "job_posted_at": result.get("job_posted_at")
                }
                jobs.append(job)
            
            return jobs
        else:
            logger.warning("Collection is empty")
            return []
    except Exception as e:
        logger.error(f"Error in get_latest_jobs: {str(e)}")
        return [] 