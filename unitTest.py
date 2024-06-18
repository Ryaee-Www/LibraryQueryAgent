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

from Create_Agent import *
from Query_Agent import *

async def testDataType():
    #with st.chat_message("assistant"):
        #message_placeholder = st.empty()
    data = None
    try:
        data = await dataBaseTypeLayer("我想创建一个数据库，其中有2两种数据，车辆种类，车辆数量")
    except Exception as e:
        pass
    assert data == "any"
    try:
        data = await dataBaseTypeLayer("我想创建一个sqlite数据库，其中有2两种数据，车辆种类，车辆数量")
    except Exception as e:
        pass
    assert data == "sqlite"

def testSchema():
    schema = getSchema()
    print(schema)
async def testTableSelect():
    table = getSchema()
    data = None
    try:
        data = await dataTableSelector("我想知道在当前数据库中，哪些自行车是2015年产的？",table)
    except Exception as e:
        pass
    print(data)
    assert data == "bikes"
    try:
        data = await dataTableSelector("我想知道在当前数据库中，哪些汽车是2015年产的？",table)
    except Exception as e:
        pass
    print(data)
    assert data == "cars"
async def TestSQLGenerator():
    user_input = "2015年产的自行车有哪些？"
    tables = getSchema()
    selection = None
    try:
        selection = await dataTableSelector(user_input,tables)
    except Exception as e:
        pass
    print(selection)
    #assert selection == "cars"
    sql = await SQLGenerator(user_input, selection)
    print("sql:", sql)
async def testSqlExtract():
    user_input = "2015年产的自行车有哪些？"
    tables = getSchema()
    selection = None
    try:
        selection = await dataTableSelector(user_input, tables)
    except Exception as e:
        pass
    print(selection)
    # assert selection == "cars"
    sql = await SQLGenerator(user_input, selection)
    print("sql:", sql)
    sqlE = extractSQL(sql)
    print(sqlE)

def testFetch():
    result = fetchFromDB("SELECT * FROM bikes WHERE YEAR = 2020;")
    print(result)

if __name__ == "__main__":
    testFetch()
    '''
    loop = asyncio.get_event_loop()

    loop.run_until_complete(testSqlExtract())
    '''
