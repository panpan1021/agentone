from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import get_model_by_name

class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever= self.vector_store.get_retriever()
        self.prompt_text=load_rag_prompts()
        self.prompt_template=PromptTemplate.from_template(self.prompt_text)
        # RAG总结使用默认模型
        self.model=get_model_by_name()
        self.chain=self._init_chain()


    def _init_chain(self):
        chain=self.prompt_template |self.model|StrOutputParser()
        return chain
    def retriever_docs(self,query:str)->list[Document]:
        return self.retriever.invoke(query)
#在向量库中检索出来的document列表进行遍历,喂给chain(chain里面的提示词模版就是用prompt文件来创造的)
    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        # RAG 质量评估
        quality_warning = ""
        if not context_docs:
            quality_warning = "【未检索到相关知识库信息，以下回答可能不准确】\n"
        else:
            total_len = sum(len(doc.page_content) for doc in context_docs)
            if total_len < 50:
                quality_warning = "【检索到的相关资料较少，以下回答可能不够全面】\n"
            elif len(context_docs) < 2:
                quality_warning = "【参考资料有限，建议结合实际情况判断】\n"

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]:资料:{doc.page_content}|参考源数据:{doc.metadata}\n"
        answer = self.chain.invoke({
            "input": query,
            "context": context,
        })

        return quality_warning + answer
