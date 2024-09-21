import sys
import os
import time
from chatbot.custom_logging import logger
from chatbot.opensearch_client import OpenSearchClient
from chatbot.IndexManager import IndexManager
from chatbot.TextEmbeddingManager import TextEmbeddingManager
from chatbot.models import Models
from chatbot.PromptManager import system_prompt_chatbot_answer
from chatbot.answer import generate_answer
from settings import *
import requests

# 초기화 변수 설정
user_indices = {}  # CID별 TID를 저장하는 딕셔너리

# TextEmbeddingManager 인스턴스 생성
embedding_manager = TextEmbeddingManager(api_key=OPENAI_API_KEY, client=requests, EMBEDDING_MODEL=EMBEDDING_MODEL)

# OpenSearch 클라이언트 초기화
opensearch_client = OpenSearchClient(host=OPENSEARCH_URL, port=PORT, auth=(USERID, PASSWORD), embedding_manager=embedding_manager)

# chathistory 인덱스 매니저 초기화
chathistory_index_manager = IndexManager(client=opensearch_client.client, index_name='gpt_4o_mini_history')

# 모델 선택 부분(claude / gpt)
model_name = 'gpt'

# Models 클래스 초기화
models = Models(
    bedrock_region=bedrock_region,
    bedrock_model_id=Bedrock_model_id,
    gpt_api_key=OPENAI_API_KEY,
    gpt_model_id=gpt_model_id,
    claude_api_key=ANTHROPIC_API_KEY,
    claude_model_id=claude_model_id
)

def generate_chatbot_response(question, CID, TID=None):
    """
    질문 쿼리를 받아 답변을 생성하고 인덱싱하는 함수입니다.

    Parameters:
    - question: 사용자 질문
    - CID: 대화의 고유 식별자
    - TID: (선택적) 대화 ID로서 정렬에 사용됩니다.

    Returns:
    - {'answer': answer} 또는 {'error': str(e)}
    """
    try:
        start_time = time.time()

        # 이전 대화 기록 가져오기
        previous_history = opensearch_client.get_previous_chathistory(CID, TID)
        logger.info(f"Previous history for CID : {CID}") #  {previous_history}

        # generate_answer 함수 호출 (문맥 포함)
        answer, documents = generate_answer(question, opensearch_client, models, system_prompt_chatbot_answer, model_name, previous_history=previous_history)
        # logger.info(f"Generated answer: {answer}")

        # chathistory에 저장
        if question and answer:
            save_start_time = time.time()
            query_embedding = opensearch_client.embedding_manager.get_embedding(question)

            # TID 결정
            if TID is None:
                # TID가 None인 경우, 최대 TID 값을 가져와 +1
                max_tid = max(user_indices.get(CID, []), default=0)
                TID = max_tid + 1
            # 데이터 저장
            chathistory_index_manager.qna_insert_document(
                TID=TID,
                CID=CID,
                query=question,
                answer=answer,
                query_embedding=query_embedding,
                docs=documents,
                feedback=0  # 예시: 피드백 (0은 기본값으로 설정)
            )
            
            # TID 추가
            if CID not in user_indices:
                user_indices[CID] = []
            user_indices[CID].append(TID)

            save_end_time = time.time()
            logger.info(f"Chathistory save time: {save_end_time - save_start_time:.2f} seconds")

        end_time = time.time()
        logger.info(f"Total time: {end_time - start_time:.2f} seconds")
        return {"answer": answer}

    except Exception as e:
        logger.error(f"An error occurred(generate_chatbot_response): {str(e)}")
        return {"error": str(e)}