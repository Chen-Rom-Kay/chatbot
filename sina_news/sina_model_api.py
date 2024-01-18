from langchain.llms.base import LLM
from fastapi import FastAPI
from typing import Dict, List, Any, Optional
import torch,sys,os
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import HuggingFaceEmbeddings
from requests_html import HTMLSession
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationBufferMemory
from transformers import AutoModelForCausalLM,AutoModel,AutoTokenizer
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import (CONDENSE_QUESTION_PROMPT,QA_PROMPT)
from langchain import FewShotPromptTemplate, PromptTemplate, LLMChain
import uvicorn

app = FastAPI()

class GLM(LLM):
  max_token: int = 4096
  temperature: float = 0.8
  top_p = 0.9
  tokenizer: object = None
  model: object = None
  history_len: int = 1024
    
  def __init__(self, model_name_or_path):
    super().__init__()
    self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path,device_map='auto',trust_remote_code=True)
    self.model = AutoModel.from_pretrained(model_name_or_path,device_map='auto', trust_remote_code=True).half().cuda()
    self.model.eval()

  @property
  def _llm_type(self) -> str:
    return "GLM"

  def _call(self, prompt:str, history:List[str]=[], stop:Optional[List[str]]=None):
    response, _ = self.model.chat(
        self.tokenizer,
        prompt,
        history=history[-self.history_len:] if self.history_len > 0 else [],
        max_length=self.max_token,
        temperature=self.temperature,
        top_p=self.top_p)
    return response

def spilt_docs(docs):
    documents = []
    for doc in docs.itertuples(index=False):
        documents.append(Document(page_content=doc[0], metadata={'source':doc[1]}))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs_splitter = text_splitter.split_documents(documents)
    return docs_splitter
    # print(f'分割前文档数目：{len(documents)}, 分割后文档数目：{len(docs_splitter)}')
    
@app.get("/qa")
async def get_chain(question):
    response = qa.invoke({"question": question})
    print(response)
    answer = response['answer']
    sources = ""
    for documents in response['source_documents']:
        sources = sources + documents.page_content[:50]+"...---"+documents.metadata['source'] + "\n\n"   
    msg = answer + "\n\nsources:\n\n" + sources
    chat_history = response['chat_history']
    return {'msg':msg,'chat_history':chat_history,"answer":answer}

@app.get("/ClearMemory")
async def clear_memory():
    memory.clear()

@app.get("/cs")
async def cs():
    return "这是测试"

@app.get("/GetFaiss")
async def get_faiss():
    try:
        docs = pd.read_csv('./data/sina_docs.csv')
        docs_splitter = spilt_docs(docs)
        db = FAISS.from_documents(docs_splitter, embeddings)
        db.save_local(db_save_path)
        return "构建Faiss检索成功"
    except Exception as e:
        return e

if __name__ == '__main__':
    llm = GLM('./chatglm3-6b')
    model_kwargs = {'device':'cuda'}
    embeddings = HuggingFaceEmbeddings(model_name="./multilingual-MiniLM-L12-v2", model_kwargs=model_kwargs)
    db_save_path = "./faiss_sina"
    
    if os.path.exists(db_save_path):
        db = FAISS.load_local(db_save_path, embeddings)
    else:
        docs = pd.read_csv('./data/sina_docs.csv')
        docs_splitter = spilt_docs(docs)
        db = FAISS.from_documents(docs_splitter, embeddings)
        db.save_local(db_save_path)
        
    retriever  = db.as_retriever(search_kwargs={"k": 3})
    memory = ConversationBufferWindowMemory(
        k=5,
        return_messages=True,
        memory_key="chat_history",
        output_key='answer'
    )
    template = '''给定以下对话和后续问题，将后续问题以中文改写为独立问题。

    聊天历史记录：
    {chat_history}
    后续输入：{question}
    独立问题：
    '''

    prompt = PromptTemplate(input_variables=['chat_history', 'question'], template=template)

    question_generator = LLMChain(llm=llm, prompt=prompt)

    doc_chain = load_qa_chain(llm=llm, chain_type="stuff")

    qa = ConversationalRetrievalChain(
        retriever=retriever,
        question_generator=question_generator,
        combine_docs_chain=doc_chain,
        verbose=True,
        memory = memory,
        return_source_documents=True

    )
    uvicorn.run(app=app, host="0.0.0.0", port=6006)