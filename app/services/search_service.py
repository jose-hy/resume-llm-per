from typing import List, Tuple, Dict, Any
from pymilvus import Collection, connections
from ..core.config import settings, embedder, cohere_client

# Connect to Milvus
connections.connect("default", uri=settings.ZILLZ_URI, token=settings.ZILLZ_TOKEN)
collection = Collection("job_listings")

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

    bool_expr = " and ".join(bool_expr)
    
    search_results = collection.search(
        data=[query_vector],
        anns_field="job_description_vector",
        param=search_params,
        limit=count,
        expr=bool_expr,
        output_fields=["*"]
    )
    
    ids, distances, docs, metadatas = [], [], [], []
    for hit in search_results[0]:
        ids.append(hit.id)
        distances.append(hit.distance)
        docs.append(hit.entity.get("job_description_raw"))
        metadata = {
            "info": hit.entity.get('info'),
            "degree": hit.entity.get('degree'),
            "remote": hit.entity.get('remote'),
            "location_state": hit.entity.get('location_state'),
            "employment_type": hit.entity.get('employment_type'),
            "citizen": hit.entity.get('citizenship'),
            "link": hit.entity.get('job_apply_link'),
            "job_post_date": hit.entity.get('job_posted_at_datetime_utc'),
        }
        metadatas.append(metadata)

    return ids, distances, docs, metadatas

def rerank_results(query: str, docs: List[str], n: int = 3) -> Any:
    """
    Rerank search results using Cohere
    """
    if not docs:
        print("No documents available for reranking.")
        return None
    
    return cohere_client.rerank(
        model='rerank-english-v2.0',
        query=query,
        documents=docs,
        top_n=n
    ) 