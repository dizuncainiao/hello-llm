from pydantic import BaseModel
import requests
import re

# 预编译正则表达式
CLEAN_PATTERN = re.compile(r'<think>.*?</think>', flags=re.DOTALL)

# 常量配置
API_ENDPOINT = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_TIMEOUT = 10.0
MODEL_NAME = "DeepSeek-R1-Distill-Qwen-7B"


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    code: int
    msg: str
    data: dict


# 创建可复用的Session对象
_session = requests.Session()


def chat_with_llm(prompt: str) -> str:
    """
    与LLM进行对话的封装函数

    Args:
        prompt: 用户输入的提示文本

    Returns:
        清理后的响应文本，已移除<thought>标签内容

    Raises:
        requests.exceptions.RequestException: 网络请求相关异常
        ValueError: JSON解析失败时抛出
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = _session.post(
            API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()

        # 安全解析响应内容
        response_data = response.json()

        choices = response_data.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            raw_content = message.get('content', '')
        else:
            raw_content = ''

        # 清理文本内容
        cleaned_content = CLEAN_PATTERN.sub('', raw_content).strip()
        return cleaned_content

    except requests.exceptions.JSONDecodeError as e:
        raise ValueError(f"Failed to parse response JSON: {str(e)}")
