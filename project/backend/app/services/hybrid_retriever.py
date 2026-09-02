# from app.services.weaviate_client import get_collection

# def reciprocal_rank_fusion(results: list, k: int = 60) -> list:
#     scores = {}
#     for rank_list in results:
#         for rank, item in enumerate(rank_list):
#             doc_id = item.uuid
#             if doc_id not in scores:
#                 scores[doc_id] = 0
#             scores[doc_id] += 1 / (k + rank + 1)
#     sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#     return [item[0] for item in sorted_items]

# async def hybrid_search(query: str, top_k: int = 5) -> list:
#     collection = get_collection()
#     dense_results = collection.query.near_text(
#         query=query,
#         limit=top_k * 2,
#         return_metadata=["distance"]
#     )
#     sparse_results = collection.query.bm25(
#         query=query,
#         limit=top_k * 2,
#         properties=["content"]
#     )
#     fused_ids = reciprocal_rank_fusion([dense_results.objects, sparse_results.objects])
#     final_objects = []
#     for obj_id in fused_ids[:top_k]:
#         obj = collection.query.fetch_object_by_id(obj_id)
#         final_objects.append(obj)
#     return final_objects

from app.services.weaviate_client import near_text_search, bm25_search

def reciprocal_rank_fusion(results: list, k: int = 60) -> list:
    scores = {}
    for rank_list in results:
        for rank, item in enumerate(rank_list):
            doc_id = item.get("_additional", {}).get("id")
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items]

async def hybrid_search(query: str, top_k: int = 5) -> list:
    dense_results = near_text_search(query, limit=top_k * 2)
    sparse_results = bm25_search(query, limit=top_k * 2)
    
    fused_ids = reciprocal_rank_fusion([dense_results, sparse_results])
    # Tạo map id -> object
    obj_map = {}
    for obj in dense_results + sparse_results:
        obj_id = obj.get("_additional", {}).get("id")
        if obj_id:
            obj_map[obj_id] = obj
    
    final_objects = [obj_map[oid] for oid in fused_ids[:top_k] if oid in obj_map]
    return final_objects