from fastapi import FastAPI
import pandas as pd
from typing import Dict, List, Any, Optional
from langchain.llms.base import LLM
import torch,sys,os
from transformers import AutoTokenizer,AutoModel
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate,FewShotPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import CommaSeparatedListOutputParser
import uvicorn

app = FastAPI()

class GLM(LLM):
  max_token: int = 2048
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

@app.get("/chain")
async def get_chain(text):
  text1 = chain.run(text)
  text2 = chain_kd.run(text)
  return {"text1":text1,"text2":text2}

@app.get("/cs")
async def cs():
  return "这是测试"

@app.get("/searchs")
async def searchs(text):
  result = db.similarity_search_with_score(text, distance_metric="cos", k=5)
  result_list = []
  for i in result:
    data = {
      "name":i[0].metadata['name'],
      "url":i[0].metadata['url'],
      "play_url":i[0].metadata['play_url']
    }
    result_list.append(data)
  return result_list

@app.get("/GetFaiss")
async def get_faiss():
    docs = pd.read_csv('./data/songs.csv')
    docs.drop(docs[docs['texts']=='\n'].index,inplace=True)
    
    output_parser = CommaSeparatedListOutputParser()
    format_instructions = output_parser.get_format_instructions()
    
    template = """
    我正在构建一个歌曲检索系统。对以下歌词：

    {song}

    您的任务是列出最少4种，最多8种的情绪列表，每一种情绪请以逗号分隔，只输出情绪列表，不要输出其他内容，稍后我将用它来检索歌曲
    """
    prompt = PromptTemplate(
        input_variables=["song"],
        template=template,
        partial_variables={"format_instructions": format_instructions},
    )
    chain = LLMChain(llm=llm,prompt=prompt,output_parser=output_parser)
    
    documents = []
    for doc in tqdm(docs.itertuples(index=False)):
        response = chain.run(doc[4])[0]
        documents.append(Document(page_content=response, metadata={'play_url':doc[1],'url':doc[2],'name':doc[3],'text':doc[4]}))
    db = FAISS.from_documents(documents, embeddings)
    db.save_local("./faiss_music")
    return "构建Faiss检索成功"

if __name__ == '__main__':
    llm = GLM('./chatglm3-6b')
    model_kwargs = {'device':'cuda'}
    embeddings = HuggingFaceEmbeddings(model_name="./multilingual-MiniLM-L12-v2", model_kwargs=model_kwargs)
    output_parser = CommaSeparatedListOutputParser()
    examples = [
        {
            "input": "我度过了愉快的一天！",
            "answer": "喜悦"
        }, {
            "input": "我今天很累，感觉不舒服。",
            "answer": "疲惫、不适、疲劳"
        },{
            "input": "我恋爱了。",
            "answer": "开心、爱"
        }
    ]
    example_template="""
    User: {input}
    AI: {answer}
    """
    example_prompt = PromptTemplate(input_variables=['input','answer'], template=example_template)

    prefix = """我们有一个简单的歌曲检索系统。它接受八种情绪。您的任务是建议 1 到 4 种情绪来匹配用户的感受。注意请只输出答案即可,其他无关的信息不要输出。
    对于较长的句子建议更多的情感，对于小句子建议一两种情感，试图浓缩输入的中心主题。以下是您过去执行此操作的一些示例：
    """

    suffix = """
    User: {input}
    """

    few_shot_prompt_template = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=['input'],
        example_separator="\n"
    )
    template = """你是一个人生开导大师，请对以下输入，说一句鼓励的话语:
    {text}
    """
    prompt = PromptTemplate(
        input_variables=["text"],
        template=template
    )
    chain_kd = LLMChain(llm=llm,prompt=prompt)
    chain = LLMChain(llm=llm,prompt=few_shot_prompt_template)
    db_save_path = "./faiss_music"
    db = FAISS.load_local(db_save_path, embeddings)
    uvicorn.run(app=app, host="0.0.0.0", port=6006)
         
         
    