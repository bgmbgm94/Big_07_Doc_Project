# from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어 추가

# from generate_chatbot_response import generate_chatbot_response
# from chatbot.custom_logging import logger
# import os
# import sys
# import datetime
# import pytz
# # import random

# # 한국 시간대 설정
# KST = pytz.timezone('Asia/Seoul')


# # 현재 파일의 디렉토리 경로를 가져와서 필요한 디렉토리 경로를 추가
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)

# app = FastAPI()

# # CORS 설정 추가
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 모든 도메인 허용 (특정 도메인만 허용하려면 ["http://example.com"] 형식으로 변경)
#     allow_credentials=True,
#     allow_methods=["*"],  # 모든 HTTP 메서드 허용
#     allow_headers=["*"],  # 모든 HTTP 헤더 허용
# )

# # 절대 경로 설정
# frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

# # Static files
# app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")

# # Templates
# templates = Jinja2Templates(directory=os.path.join(frontend_dir, "templates"))

# # Middleware to disable caching for all responses
# @app.middleware("http")
# async def no_cache_middleware(request, call_next):
#     response = await call_next(request)
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response

# @app.get("/")
# async def get(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/favicon.ico", include_in_schema=False)
# async def favicon():
#     return FileResponse(os.path.join(frontend_dir, "static/favicon.ico"))

# @app.get("/api")
# def read_api():
#     return {"message": "Hello, API"}


# # 피드백 처리 엔드포인트
# class Feedback(BaseModel):
#     feedback: int

# @app.post("/feedback")
# async def receive_feedback(feedback: Feedback):
#     feedback_value = feedback.feedback
#     print(f"Received feedback: {feedback_value}")  # 콘솔 로그 출력
#     # 이 부분에서 피드백 값을 데이터베이스에 저장하거나 다른 처리를 수행할 수 있습니다.
#     return {"message": "Feedback received", "feedback": feedback_value}


# # 질문을 받고 처리하는 데이터 모델
# class Question(BaseModel):
#     question: str
#     client_id: str  # client_id 추가

# # 질문 처리 엔드포인트
# @app.post("/ask")
# async def ask_question(question: Question):
#     try:
#         question_text = question.question
#         user_id = question.client_id
#         # 질문이 들어온 시간 기록
#         question_received_time = datetime.datetime.now(KST).isoformat()
#         logger.info(f"Question received at {question_received_time}")

#         result = generate_chatbot_response(question_text, user_id)
#         if result is not None and 'answer' in result:
#             return {"question": question_text, "answer": result['answer']}
#         else:
#             return {"error": "The response does not contain an answer."}
#     except Exception as e:
#         logger.error(f"Error in ask_question endpoint: {str(e)}")
#         return {"error": str(e)}

# # WebSocket 엔드포인트 추가
# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await websocket.accept()
#     try:

#         while True:
#             data = await websocket.receive_text()
#             result = generate_chatbot_response(data, client_id)
            
#             if result is not None and 'answer' in result:
#                 await websocket.send_text(result['answer'])
#             else:
#                 await websocket.send_text("The response does not contain an answer.")
#     except WebSocketDisconnect:
#         logger.info("Client disconnected")
#     except Exception as e:
#         logger.error(f"Error in websocket_endpoint: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8888)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI

from generate_chatbot_response import generate_chatbot_response
from chatbot.custom_logging import logger

import datetime
import pytz
KST = pytz.timezone('Asia/Seoul')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (특정 도메인만 허용하려면 ["http://example.com"] 형식으로 변경)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)
# Middleware to disable caching for all responses
@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# 질문을 받고 처리하는 데이터 모델
class Question(BaseModel):
    question: str
    client_id: str  # client_id 추가

# 질문 처리 엔드포인트
@app.post("/ask")
async def ask_question(question: Question):
    try:
        question_text = question.question
        client_id = question.client_id
        # 질문이 들어온 시간 기록
        question_received_time = datetime.datetime.now(KST).isoformat()
        logger.info(f"Question received at {question_received_time}")

        result = generate_chatbot_response(question_text, client_id)
        if result is not None and 'answer' in result:
            return {"question": question_text, "answer": result['answer']}
        else:
            return {"error": "The response does not contain an answer."}
    except Exception as e:
        logger.error(f"Error in ask_question endpoint: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234)