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
import sqlite3

'''Work Flow:
Get Database List -> Select Appropriate Table -> generate Query -> return result

'''
def getSchema():
    """连接数据库，返回数据库列表格式"""
    conn = sqlite3.connect("D:/baiduPaddle/SQLTest/new_database.db")
    cursor = conn.cursor()

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema_info[table_name] = [{"column_name": col[1], "data_type": col[2]} for col in columns]

    conn.close()
    return schema_info

async def dataTableSelector(user_input,tables):
    """第一次模型，输出SQL数据库名"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个专业的数据库检索助手",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请根据用户输入的内容进以及对话历史，从当前数据库列表中选择合适的列表进行回复。注意你只需要回复相应的列表名，不需要回复用户的问题！
    请直接回答问题，千万不要作出任何解释！
    [当前数据库列表]：
    {tables}\n
    [用户输入]：
    {user_input}\n
    [输出]："""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

async def SQLGenerator(user_input, table_name):
    """第二次模型，输出SQL数据库代码"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个专业的数据库分析助手",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请从指定的数据库表单中，生成可以完成用户要求的标准sqlite语句
    注意，你只需要直接回答问题，不需要输出任何解释。
    [指定表单]：
    {table_name}
    [用户输入]：
    {user_input}\n
    [输出]：直接输出sqlite语句，千万不要作出任何解释！"""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

def extractSQL(sql):
    sql_pattern = r'```sql\n(.*?)\n```'
    match = re.search(sql_pattern, sql, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None

def fetchFromDB(sql):
    """连接数据库，返回数据库列表格式"""
    if(sql):
        conn = sqlite3.connect("D:/baiduPaddle/SQLTest/new_database.db")
        cursor = conn.cursor()

        # Get table names
        cursor.execute(sql)
        result = cursor.fetchall()

        conn.close()
        return result
    else:
        return "没有数据，请正常回复用户"

async def responseLayer(user_input, data):
    """输出层模型，输出检索结果"""
    model = ERNIEBot(model='ernie-3.5', temperature=0.3, system="你是一个客服人员，请以可爱的语气回答我的问题",access_token = "585d46aaf3f2493175e427e951c2e83d02bc6f4c")
    messages = []
    prompt = f"""请结合上下文对话历史，仅使用给定的数据库数据，回复用户的问题。
    
    [数据库数据]：
    {data}
    [用户输入]：
    {user_input}\n
    [输出]："""
    messages.append(HumanMessage(content=prompt))
    ai_message = await model.chat(messages=messages)
    messages.append(ai_message)
    #print("回答结果：", ai_message.content, '\n')
    return ai_message.content

async def __askAgent__(question):
    tables = getSchema()
    selection = await dataTableSelector(question, tables)

    sql = await SQLGenerator(question, selection)
    sqlE = extractSQL(sql)
    data = fetchFromDB(sqlE)
    response = await responseLayer(question, data)
    return response
def askAgent(question):
    return asyncio.run(__askAgent__(question))
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    question = "请向我提供前三个数据库中的自行车，以年份排序最新的。"
    tables = getSchema()
    selection = None
    try:
        selection = loop.run_until_complete(dataTableSelector(question, tables))
    except Exception as e:
        pass
    print(selection)
    # assert selection == "cars"
    sql = loop.run_until_complete(SQLGenerator(question, selection))
    print("sql:", sql)
    sqlE = extractSQL(sql)
    print(sqlE)
    data = fetchFromDB(sqlE)
    print(data)
    response = loop.run_until_complete(responseLayer(question, data))
    print("response: ", response)

