# 关于聊天机器人的学习
以下项目统一使用chatglm3-6b、LangChain、fastapi、streamlit搭建
## 163music--网易云情感歌曲推荐助手
    1、爬取--selenium
    使用selenium对网易云歌曲的播放链接、歌曲名、歌词等进行爬取，再通过prompt之后的chatglm模型对每首歌曲的歌词进行4-8种情感总结。
    当用户输入一段话，chatglm对该话语进行情感总结并使用faiss对歌曲的情感进行相似度匹配来推荐相关的歌       
 ![Video_2024-01-13_004327](https://github.com/Chen-Rom-Kay/chatbot/assets/48251374/8536159d-5bdf-42ee-b6e7-19270bc99060)
 ## sina--新浪网新闻问答助手
    1、爬取--requests_html包
    对新浪网站的新闻进行爬取，并进行文档分割和文本向量embedding。使用retriever+chatglm来对用户的输入依据相关新闻进行回复    
![01-18_230130](https://github.com/Chen-Rom-Kay/chatbot/assets/48251374/b8b785fb-5924-4a57-affb-b03b5cb3a312)

