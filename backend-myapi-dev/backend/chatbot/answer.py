import sys, random, os, time

# 현재 파일의 디렉토리 경로를 가져와서 backend 디렉토리 경로를 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', '..')
sys.path.append(backend_dir)

from chatbot.settings import OPENSEARCH_SEARCH_SIZE, INDEXNAME
from chatbot.models import BedrockManager
from settings import bedrock_region, Bedrock_model_id
import re
# 로거 설정
from chatbot.custom_logging import logger

# BedrockManager 객체를 전역으로 초기화 (성능 개선)
bedrock_manager = BedrockManager(region=bedrock_region, model_id=Bedrock_model_id)

def add_paragraph_breaks(answer):
    """
    한글 뒤에 오는 점에 개행 문자를 추가합니다.
    숫자 뒤의 점은 개행 문자가 추가되지 않도록 처리합니다.
    """
    # 한글 뒤에 오는 점에 개행 문자를 추가
    formatted_answer = re.sub(r'(?<=[가-힣])\.\s*(?=\S)', '.\n', answer)
    return formatted_answer

def format_answer(answer):
    return f"{answer} \n 추가적인 문의사항이 있으시면 언제든 이야기해 주세요😊."

def generate_answer(query, opensearch_client, model_manager, system_prompt, model_name, previous_history=None):
    """
    질문 쿼리를 받아 답변을 생성하고 인덱싱하는 함수
    """
    try:
        documents = []  # 검색된 문서 내용을 저장할 리스트

        # FAQ 인덱스에서 유사 문서 검색
        faq_documents = opensearch_client.chat_his_search_similar_documents(query, k=1, index_name='faq', similarity_threshold=0.7)
        
        if faq_documents:
            # FAQ에서 유사 문서를 찾은 경우 해당 문서를 포맷팅하여 반환
            faq_answer = faq_documents[0]['text']  # 첫 번째 문서의 텍스트 추출
            formatted_answer = format_answer(faq_answer)
            breaks_format_answer = add_paragraph_breaks(formatted_answer)
            return breaks_format_answer, [faq_answer]
            # faq_answer = bedrock_manager.faq_answers(query, system_prompt_no_llm)
            # return faq_answer, documents
  
        # 유사 문서 검색 및 검색 결과에서 컨텍스트 추출
        start_time = time.time()
    # try:
    #     # 질문 분류 (임시로 닫아둔 상태)
    #     classification = bedrock_manager.question_classification(query, system_prompt_text_filter)
    #     question_category = bedrock_manager.classify_response(classification)
    #     question_category = "question"
    #     logger.info(f"question_category: {question_category}")
    #     documents = []  # 검색된 문서 내용을 저장할 리스트

    #     if question_category == "question":
    #         # 유사 문서 검색 및 검색 결과에서 컨텍스트 추출
    #         start_time = time.time()
            
            # chathistory 인덱스에서 이전 답변 검색
        #     previous_answers = opensearch_client.chat_his_search_similar_documents(query, k=3, index_name='faq')
        #     context = ""
        # if question_category == "question":
        #     # 유사 문서 검색 및 검색 결과에서 컨텍스트 추출
            # start_time = time.time()
            
            # # chathistory 인덱스에서 이전 답변 검색
            # previous_answers = opensearch_client.chat_his_search_similar_documents(query, k=3, index_name='faq')
            # context = ""        
            
        # chathistory 인덱스에서 이전 답변 검색
        previous_answers = opensearch_client.chat_his_search_similar_documents(query, k=3, index_name='faq', similarity_threshold=0.2)
        context = ""

        if previous_answers:
            previous = [doc['text'] for doc in previous_answers]
            documents.extend(previous)
            context += " ".join(previous) + " "

        search_results = opensearch_client.search_similar_documents(query, OPENSEARCH_SEARCH_SIZE, INDEXNAME)

        if search_results:
            new_documents = [doc['text'] for doc in search_results]
            documents.extend(new_documents)
            context += " ".join(new_documents)
        else:
            logger.warning("No relevant documents found.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"search_documents_time: {elapsed_time:.2f} seconds")

        # 모델 매니저를 통해 답변 생성
        start_time = time.time()

        if previous_history:
            # 이전 대화 기록이 있는 경우
            result = model_manager.ModelSelector(query, context, system_prompt, model_name, previous_history)
        else:
            # 이전 대화 기록이 없는 경우
            result = model_manager.ModelSelector(query, context, system_prompt, model_name, [])

        # 반환값 체크
        if isinstance(result, tuple) and len(result) == 2:
            answer, _ = result
        else:
            logger.error("ModelSelector returned an unexpected number of values.")
            return "An error occurred during answer generation.", None

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"LLM_answer_time: {elapsed_time:.2f} seconds")

        return answer, documents
        
    except Exception as e:
        logger.error(f"An error occurred(generate_answer): {str(e)}")
        return "An unexpected error occurred.", None
