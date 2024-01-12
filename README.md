# 关于聊天机器人的自学习和创建
## 163music--网易云情感歌曲推荐助手
    1、爬取--selenium
    2、模型--chatglm3-6b + langchian
    3、网页--treamlit
    使用selenium对网易云歌曲的播放链接、歌曲名、歌词等进行爬取，再通过prompt之后的chatglm模型对每首歌曲的歌词进行4-8种情感总结。
    当用户输入一段话，chatglm对该话语进行情感总结并使用faiss对歌曲的情感进行相似度匹配来推荐相关的歌曲
