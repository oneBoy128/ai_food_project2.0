import logging

from week5.tools.batch_generate_embedding import batch_generate_embedding

def batch_store_to_chroma(
    collection,  # 第一步初始化的Chroma集合对象
    chunks_list: list,  # 你的Document列表（create_chunks生成的）
    tokenizer, model, device,
    batch_size: int = 2000  # 每批存入数量（内存够可改2000）
):
    """
    批量将Embedding+ID+元数据存入Chroma，支持断点续跑
    :param collection: Chroma集合对象
    :param chunks_list: Document列表
    :param tokenizer/model/device: 初始化好的模型组件（复用，避免重复加载）
    :param batch_size: 每批处理数量
    """
    total_docs = len(chunks_list)
    total_batches = (total_docs // batch_size) + 1  # 总批数
    logging.info(f"开始存入Chroma：共{total_docs}个Document，分{total_batches}批处理")
    print(f"开始存入Chroma：共{total_docs}个Document，分{total_batches}批处理")

    # 遍历每批数据
    for batch_idx in range(total_batches):
        # 1. 计算当前批的起止索引
        start = batch_idx * batch_size
        end = min((batch_idx + 1) * batch_size, total_docs)  # 最后一批避免越界
        current_batch = chunks_list[start:end]
        current_batch_size = len(current_batch)

        if current_batch_size == 0:
            logging.info(f"⚠️  第{batch_idx+1}批无数据，跳过")
            continue

        try:
            # 2. 调用你的函数生成当前批的Embedding+ID+元数据
            embeddings, doc_ids, metadatas = batch_generate_embedding(
                chunks_list=current_batch,
                tokenizer=tokenizer,
                model=model,
                device=device
            )

            doc_texts = [doc.page_content for doc in current_batch]  # 关键：提取每个Document的文本
            # 3. 存入Chroma（核心API）
            collection.add(
                embeddings=embeddings,  # 384维向量列表
                ids=doc_ids,            # 唯一ID列表（RecipeId_索引，不重复）
                metadatas=metadatas,    # 元数据列表（食谱信息，用于筛选）
                documents=doc_texts     # 新增：存入文本，检索时才能返回
            )

            # 5. 记录进度
            processed_docs = end  # 已处理的总数量
            progress = (processed_docs / total_docs) * 100  # 进度百分比
            logging.info(f"✅ 第{batch_idx+1}/{total_batches}批存入成功！")
            logging.info(f"  - 处理范围：{start+1}-{end}/{total_docs}")
            logging.info(f"  - 当前进度：{round(progress, 2)}%")
            logging.info(f"  - 集合累计向量数：{collection.count()}")
            print(f"第{batch_idx+1}/{total_batches}批存入成功！进度：{round(progress, 2)}%，累计向量数：{collection.count()}")

        except Exception as e:
            # 异常捕获：某批出错不中断，记录错误后继续下一批
            error_msg = f"❌ 第{batch_idx+1}批存入失败！范围：{start+1}-{end}，错误：{str(e)}"
            logging.error(error_msg)
            print(error_msg)
            # 打印详细错误栈（方便定位问题，如ID重复、向量维度错）
            import traceback
            traceback.print_exc()
            continue

    # 全部完成后记录最终状态
    final_count = collection.count()
    logging.info(f"🎉 该批次处理完成！")
    logging.info(f"  - 总输入Document数：{total_docs}")
    logging.info(f"  - Chroma最终向量数：{final_count}")
    logging.info(f"  - 存入成功率：{round((final_count / total_docs) * 100, 2)}%")
    print(f"\n🎉 该批次处理完成！")
    print(f"  - 总输入Document数：{total_docs}")
    print(f"  - Chroma最终向量数：{final_count}")
    print(f"  - 存入成功率：{round((final_count / total_docs) * 100, 2)}%")
