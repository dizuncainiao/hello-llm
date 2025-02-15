from fastapi import FastAPI, HTTPException, Query, status
from chat_service import chat_with_llm, ChatResponse
import asyncio

app = FastAPI()


@app.post("/chat/", response_model=ChatResponse)
async def chat(
        prompt: str = Query(..., min_length=1, max_length=1000, description="用户输入的问题")
):
    try:
        # 假设 chat_with_llm 是同步函数
        response = await asyncio.to_thread(chat_with_llm, prompt)
        return ChatResponse(code=200, msg='请求成功', data={'content': response})
    except ValueError as e:  # 特定业务异常
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的请求参数"
        )
    except Exception as e:
        # 记录原始错误日志（实际项目需添加日志记录）
        print(f"Internal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )
