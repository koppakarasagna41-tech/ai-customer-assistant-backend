import json
import os

modified_paths = ["/app/applet/app/api/v1/rag.py"]
new_paths = [
    "/app/applet/app/schemas/document.py",
    "/app/applet/app/schemas/chunk.py",
    "/app/applet/app/schemas/retrieval.py",
    "/app/applet/app/schemas/rag_response.py",
    "/app/applet/app/prompts/rag_prompt.txt",
    "/app/applet/app/prompts/query_rewrite.txt",
    "/app/applet/app/prompts/context_compression.txt",
    "/app/applet/app/services/document_loader.py",
    "/app/applet/app/services/chunker.py",
    "/app/applet/app/services/embedding_service.py",
    "/app/applet/app/services/vector_store.py",
    "/app/applet/app/services/query_rewriter.py",
    "/app/applet/app/services/query_classifier.py",
    "/app/applet/app/services/metadata_filter.py",
    "/app/applet/app/services/retrieval_cache.py",
    "/app/applet/app/services/reranker.py",
    "/app/applet/app/services/context_builder.py",
    "/app/applet/app/services/citation_builder.py",
    "/app/applet/app/services/retriever.py",
    "/app/applet/app/services/document_indexer.py",
    "/app/applet/app/services/rag_service.py",
    "/app/applet/app/routers/rag.py"
]

res = {
    "modified_files": [],
    "new_files": []
}

for path in modified_paths:
    with open(path, "r") as f:
        code = f.read()
    res["modified_files"].append({
        "path": path.replace("/app/applet/app", "/app"),
        "reason": "Overwrote placeholder search endpoint to support full query, search, indexing and listing.",
        "code": code
    })

for path in new_paths:
    with open(path, "r") as f:
        code = f.read()
    
    if "schemas" in path:
        purpose = "Data transfer schema defining types for requests and responses."
    elif "prompts" in path:
        purpose = "Prompt template optimized for model alignment and security boundaries."
    else:
        purpose = "Service module orchestrating core business logic of the Enterprise RAG Pipeline."

    res["new_files"].append({
        "path": path.replace("/app/applet/app", "/app"),
        "purpose": purpose,
        "code": code
    })

# Output JSON back to workspace
with open("/app/applet/app/output.json", "w") as f:
    json.dump(res, f, indent=2)

print("JSON generation successful")
