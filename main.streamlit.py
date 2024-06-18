import os
import re
import json
import datetime
import glob
import streamlit as st
import asyncio
import pdfplumber
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.memory import HumanMessage
from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
import numpy as np
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import yaml
import extra_streamlit_components as stx
from Query_Agent import askAgent

print("RE")
# Initialize session state
print(f"this {'init' in st.session_state}" )
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

#print('init' in st.session_state)
if 'initiate' not in st.session_state:
    st.session_state['initiate'] = True
    st.session_state.view = 'home'
    st.session_state["authentication_status"] = None
    st.session_state["loggedIn"] = False
    st.session_state["showSide"] = False
    #authenticator.login()


def home_view():#TODO CANNOT JUMP ANYWHERE
    st.title("Welcome")
    st.write("login: ",st.session_state["loggedIn"])
    if st.button("continue as visitor"):
        st.session_state.view = 'visitor'
        st.experimental_rerun()
    if st.button("login as user"):
        st.session_state["showSide"] = True
    if st.session_state["showSide"]:
        with (st.sidebar):
            if st.session_state["loggedIn"] is False:
                authenticator.login()
                if st.session_state["authentication_status"] and not st.session_state["loggedIn"]:
                    st.session_state["loggedIn"] = True
                    st.session_state.view = 'loggedIn'
                    #st.experimental_rerun()
                elif st.session_state["authentication_status"] is False:
                    st.error('Username/password is incorrect')
                elif st.session_state["authentication_status"] is None:
                    st.warning('Please enter your username and password')
            if st.session_state["loggedIn"]:
                st.session_state.view = f'loggedIn as {st.session_state["name"]}'




# Function to display the first view


# Function to display the second view


def loggedInPage():

    payload()
    

def visitorPage():
    payload()



def payload():
    with st.sidebar:
        if st.session_state["loggedIn"] == True:
            st.write("loggedIN: ",st.session_state["loggedIn"])
            st.markdown(f"logged in as {st.session_state['name']}")
            authenticator.logout()
        else:
            st.write("loggedIN: ",st.session_state["loggedIn"])
            st.write(st.session_state["authentication_status"])
            st.title("Existing user Login")
            authenticator.login()
            if st.session_state["authentication_status"]:
                st.session_state.view = 'loggedIn'
                st.experimental_rerun()
            elif st.session_state["authentication_status"] is False:
                st.error('Username/password is incorrect')
            elif st.session_state["authentication_status"] is None:
                st.warning('Please enter your username and password')

            if st.session_state["authentication_status"] == True:
                st.session_state["loggedIn"] = True
                st.session_state.view = 'loggedIn'
                #st.rerun()
        BackToHome()
    st.title('图书咨询系统')
    #st.markdown("如果有需要帮助，可以加入我们的Q&A微信群：")
    #image_path = 'RAG_WeChat.jpg'
    #if os.path.exists(image_path):
        #st.image(image_path, width=400)
    #else:
        #st.error('图片文件不存在，请检查文件路径是否正确。')

    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.markdown("请直接在聊天框输入问题，例如：")
    st.markdown("“3月7号的日活跃用户是多少”")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请输入聊天内容"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("bot"):
            message_placeholder = st.empty()
            response = askAgent(prompt)
            message_placeholder.markdown(response)
            #TODO utilize Query_Agent


def BackToHome():
    if st.button("back to homepage"):
        st.session_state.view = 'home'
        st.experimental_rerun()


# Control logic to display the appropriate view
if st.session_state.view == 'home':
    home_view()
elif st.session_state.view == 'visitor':
    visitorPage()
elif st.session_state.view == 'loggedIn':
    loggedInPage()
elif st.session_state.view == 'blank':
    pass

