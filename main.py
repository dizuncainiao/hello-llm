from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import re

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

# 修改: 定义新的响应模型
class ChatResponse(BaseModel):
    code: int
    msg: str
    data: dict

def chat_with_llm(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "模型名称",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(
        "http://127.0.0.1:1234/v1/chat/completions",
        headers=headers,
        json=data
    )
    raw_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')

    # 清理返回的文本，移除 <think> 标签及其内容
    cleaned_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL)

    return cleaned_response.strip()

# 修改: 使用新的 ChatResponse 作为返回值类型，并调整返回值结构
@app.get("/chat/", response_model=ChatResponse)
async def chat(prompt: str):
    try:
        response = chat_with_llm(prompt)
        return ChatResponse(code=200, msg='请求成功', data={'content': response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))