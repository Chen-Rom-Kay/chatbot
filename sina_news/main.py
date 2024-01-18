from re import escape
import requests
import json
import streamlit as st
from langchain.memory import ConversationBufferWindowMemory

url = 'http://region-3.seetacloud.com:61138/qa?'
clear_memory = 'http://region-3.seetacloud.com:61138/ClearMemory?'
# question = "有关于美国的新闻"

st.title("🌊 新浪网新闻检索问答")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "这里是新浪新闻检索聊天机器人:full_moon_with_face:"}]

if "memory" not in st.session_state:    
    st.session_state["memory"] = True
    response = requests.get(clear_memory)
    print("clear_memory:",response)


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
   
    parame = f"question={prompt}"
    response = requests.get(url+parame)
    if response.status_code==200:
        response = json.loads(response.text)
        msg = response['msg']
        chat_history = response['chat_history']
        answer = response['answer']
        print(f"msg:{msg}")
        print(f"chat_history:{chat_history}")
        st.session_state.messages.append({"role": "ai", "content": msg})
        st.chat_message("ai").write(msg)
    
    else:
        st.error('嗷~~ 服务器响应错误', icon="🚨")
