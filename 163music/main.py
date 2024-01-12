import requests
from play_songs import PlaySong
from song import Song
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import json
def get_songs(song,key_play):
    with stylable_container(key="container_with_border",
                            css_styles="""
                            {
                                border: 1px solid rgba(49, 51, 63, 0.2);
                                border-radius: 0.5rem;
                                padding: calc(1em - 1px);
                                border-color:#606060;
                                background-color:#606060 ;
                            }
                            """,
                            ):
            col1, col2, col3 = st.columns(spec=[0.6,0.6,0.1])
            with col1:
                st.markdown(song.get_name())
            with col3:
                if st.button(label=":headphones:",key=key_play):
                        with col2:
                            # placeholder1 = st.empty()
                            st.audio(song.get_play_url(),format="audio/mp3")
                            # st.write(':arrow_forward:')

def show_songs(songs):
    key = 0
    for song in songs:
        key_play = "start" + str(key)
        get_songs(song, key_play)
        key += 1

if __name__ == '__main__':
    model_url = 'http://region-3.seetacloud.com:61138/chain?text='
    db_url = 'http://region-3.seetacloud.com:61138/searchs?text='
    if 'play_song' in st.session_state:
        st.session_state.play_song.stop()
    if 'songs' not in st.session_state:
        st.session_state.songs = []
    if 'play_song' not in st.session_state:
        st.session_state.play_song = PlaySong()
    if 'emotions' not in st.session_state:
        st.session_state.emotions = None
    if 'discourse' not in st.session_state:
        st.session_state.discourse = None
    st.session_state.play_song.stop()
    st.title("💬 这里是网易云音乐情感推荐")
    st.chat_message("ai").write('请输入一段话让我来分析你此刻的心情吧！:eye:')
    human_inputs = st.text_input(':tiger:在下方输入：')
    if st.button("开始分析"):
        print(f"用户输入：{human_inputs}")
        response = json.loads(requests.get(model_url+human_inputs).text)
        st.session_state.emotions = response['text1']
        st.session_state.discourse = response['text2']
        st.chat_message("ai").markdown(f"您的心情是：{st.session_state.emotions}")
        st.chat_message("ai").write(f":sun_with_face:{st.session_state.discourse}")
        st.write('🐯请查收您的心情音乐推送：')
        searchs = json.loads(requests.get(db_url+response['text1']).text)
        st.session_state.songs = []
        for i in searchs:
            print(i['name'],i['url'], i['play_url'])
            song = Song(i['name'],i['url'], i['play_url'])
            st.session_state.songs.append(song)
        show_songs(st.session_state.songs)

    else:
        if len(st.session_state.songs) != 0:
            st.chat_message("ai").markdown(f"您的心情是：{st.session_state.emotions}")
            st.chat_message("ai").write(f":sun_with_face:{st.session_state.discourse}")
            st.write("🐯您的心情音乐推送：")
            show_songs(st.session_state.songs)