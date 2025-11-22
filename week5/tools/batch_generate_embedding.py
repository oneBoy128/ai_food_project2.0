from week5.tools.get_embedding import get_embedding

def batch_generate_embedding(
        chunks_list,
        tokenizer,
        model,
        device
):
    embeddings_list = []
    doc_ids_list = []
    metadatas_list = []
    print(f"开始批量处理，共{len(chunks_list)}个Document")
    for i, doc in enumerate(chunks_list):
        text = doc.page_content
        embedding = get_embedding(text, tokenizer, model, device)
        recipe_id = doc.metadata.get('RecipeId', f"unknown_{i}")
        doc_id = f"{recipe_id}_{i}"
        metadata = doc.metadata

        embeddings_list.append(embedding)
        doc_ids_list.append(doc_id)
        metadatas_list.append(metadata)

    return embeddings_list, doc_ids_list, metadatas_list