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


async def dataBaseTypeLayer(user_input):
    """第一层模型，判断sql数据库类型"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个专业的数据库分析助手",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请根据用户输入的内容进以及对话历史行回答进行如下选择，
    注意，你只需要直接回答问题，不需要输出任何解释。
    [输入内容]：
    {user_input}\n
    [输出]：请从用户输入的问题以及对话历史中分辨用户是希望与哪类数据库交互，比如mysql, sqlite之类的。如果用户没有明确数据库类型，请回复“any”。请直接回答问题，千万不要作出任何解释！"""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

async def createPreLayer(user_input):
    """第二层嵌入模型，分类用户输入，明确数据库需要哪些列"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个专业的数据库条目分析助手",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请根据历史对话记录和用户输入内容判断用户想要创建的数据库中需要哪些条目
    注意，你只需要直接回答问题，不需要输出任何解释。
    [输入内容]：
    {user_input}\n
    [输出要求]：你需要输出的是一个列表，应该形同[(条目名称，条目数据类型)]。千万不能输出该列表以外的结果"""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

async def createPostLayer(user_input, data, dbStsandard = "sqlite"):
    """第三层嵌入模型，汇总并输出sql代码"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个专业的数据库工程师",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请根据需求列表中提供的数据以及用户的输入内容，返回相应的数据库代码。需求列表会以列表形式告诉你数据名和其数据结构。
    注意，你只需要直接回答问题，不需要输出任何解释。
    [需求列表]：
    {data}\n
    [输入内容]：
    {user_input}\n
    [输出]：你要输出的是标准的{dbStsandard}代码"""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    question = "我想创建一个数据库，其中有2两种数据，车辆种类，车辆数量"
    dbType = loop.run_until_complete(dataBaseTypeLayer(question))
    print("dbType:", dbType)
    if dbType == "any":
        dbType = "sqlite"
    data = loop.run_until_complete(createPreLayer(question))

    print("data:", data)
    response = loop.run_until_complete(createPostLayer(question, data,dbType))
    print("final:", response)







