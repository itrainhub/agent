"""
综合数据分析智能体
@File       demo05_综合数据分析智能体.py
@Author     小明
@Date       2025/9/19 14:20
@Version    V0.0.1
"""
import json

import openpyxl
import streamlit as st
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent

from utils import get_model

# 关于数据分析提示词前缀
PROMPT_PREFIX = """你是一位数据分析助手，你的回应内容取决于用户的请求内容，请按照下面的步骤处理用户请求：

1. 思考阶段 (Thought) ：先分析用户请求类型（文字回答/表格/图表），并验证数据类型是否匹配。
2. 行动阶段 (Action) ：根据分析结果选择以下严格对应的格式。
   - 纯文字回答: 
     {"answer": "不超过50个字符的明确答案"}

   - 表格数据：  
     {"table":{"columns":["列名1", "列名2", ...], "data":[["第一行值1", "值2", ...], ["第二行值1", "值2", ...]]}}

   - 柱状图 
     {"bar":{"columns": ["A", "B", "C", ...], "data":[35, 42, 29, ...]}}

   - 折线图 
     {"line":{"columns": ["A", "B", "C", ...], "data": [35, 42, 29, ...]}}

3. 格式校验要求
   - 字符串值必须使用英文双引号
   - 数值类型不得添加引号
   - 确保数组闭合无遗漏

4. 关于多种不同格式的数据
   - 如果需要返回生成多种不同格式的数据，将它们合并，如：
     {"answer":"不超过50个字符的明确答案", "bar":{"columns": ["A", "B", "C", ...], "data":[35, 42, 29, ...]}}

   错误案例：{'columns':['Product', 'Sales'], data:[[A001, 200]]}  
   正确案例：{"columns":["product", "sales"], "data":[["A001", 200]]}

注意：除生成的数据本身外，响应输出不要有任何其它无关文本，响应数据的"output"中不要有换行符、制表符以及其他格式符号。

当前用户请求内容："""

def qa_agent(_df, _question):
    """智能体"""
    agent = create_pandas_dataframe_agent(
        llm=get_model(), # 模型
        df=_df, # DataFrame 数据集
        verbose=True, # 显示中间处理过程
        allow_dangerous_code=True, # 允许执行危险代码
        max_iterations=10, # 最大迭代次数
        agent_executor_kwargs={
            'handle_parsing_errors': True, # 有解析错误时将错误发回llm处理
        }
    )
    result = agent.invoke({'input': PROMPT_PREFIX + _question})
    return result['output']


st.title('数据分析智能体')
file_type_option = st.radio('上传文件的类型', ['CSV', 'EXCEL'], horizontal=True)
file_type = 'csv' if file_type_option == 'CSV' else 'xlsx'
file = st.file_uploader('选择上传文件', type=file_type)

# 根据选择的文件，读取文件数据
if file:
    if file_type == 'xlsx': # 如果读取的 excel 文件
        # 加载工作簿
        wb = openpyxl.load_workbook(file)
        # 获取工作簿中的工作表
        sheets = wb.sheetnames
        # 利用 pandas 读取excel指定工作表的数据
        sheet_name_option = st.radio('工作表', sheets, horizontal=True)
        st.session_state.df = pd.read_excel(file, sheet_name=sheet_name_option)
    else: # 读取 csv 文件
        st.session_state.df = pd.read_csv(file)
    with st.expander('原始数据:'):
        st.dataframe(st.session_state.df)

question = st.text_area('问题', placeholder='参照上传文件内容进行提问')
btn = st.button('分析')

# 有选择文件与填写提问问题，点击“分析”按钮进行处理
if file and question and btn:
    with st.spinner('思考中...'):
        answer = qa_agent(st.session_state.df, question)
        st.write(answer)
    # 获取到输出数据后，解析为 python 字典，并进行后续业务处理
    data = json.loads(answer)
    # 如果是普通的文本答案，则直接显示
    if 'answer' in data:
        st.write(data['answer'])
    # 如果是表格数据，则在页面渲染表格
    if 'table' in data:
        # 将返回的表格数据转换为 pandas 中 DataFrame 对象
        df = pd.DataFrame(data=data['table']['data'], columns=data['table']['columns'])
        # 渲染表格
        st.dataframe(df)
    # 如果是图表数据，则在页面绘制可视化图表
    if 'bar' in data:
        # 将返回的图表数据转换为 pandas 中 DataFrame 对象
        df = pd.DataFrame(data=data['bar']['data'], columns=data['bar']['columns'])
        # 绘制柱状图
        st.bar_chart(df)
    if 'line' in data:
        # 将返回的图表数据转换为 pandas 中 DataFrame 对象
        df = pd.DataFrame(data=data['line']['data'], columns=data['line']['columns'])
        # 绘制折线图
        st.line_chart(df)

