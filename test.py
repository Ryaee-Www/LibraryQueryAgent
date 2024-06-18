import streamlit as st
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
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
st.session_state.view = 'home'
def home_view():
    st.write(st.session_state["authentication_status"])
    authenticator.login()
    authenticator.logout()
if st.session_state.view == 'home':
    home_view()