import os
import requests
import json
from chatbot.custom_logging import logger

class TextEmbeddingManager:
    def __init__(self, api_key, client, EMBEDDING_MODEL):
        self.api_key = api_key
        self.client = client
        self.EMBEDDING_MODEL = EMBEDDING_MODEL

    def get_embedding(self, text):
        """
        지정된 모델을 사용하여 주어진 텍스트의 임베딩을 가져오기
        """
        url = "https://api.openai.com/v1/embeddings" # OpenAI 임베딩 API URL
        headers = {
            "Authorization": f"Bearer {self.api_key}", # API 인증 헤더
            "Content-Type": "application/json" # 요청 본문 형식
        }
        data = {"input": text, "model": self.EMBEDDING_MODEL} # 요청 데이터

        try:
            response = requests.post(url, headers=headers, json=data) # POST 요청
            response.raise_for_status()  # HTTP 상태 코드 검사

            response_data = response.json() # 응답 JSON 파싱
            embeddings = response_data.get('data', []) # 임베딩 데이터 추출
            if embeddings:
                return embeddings[0]['embedding'] # 첫 번째 임베딩 반환
            else:
                logger.error("API 응답에서 임베딩을 찾을 수 없습니다.") # 임베딩이 없을 경우 예외 발생
            
            ######## HTTP 오류 발생 시 메시지 출력 ########
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP 오류 발생: {http_err}")
            if response.status_code >= 400 and response.status_code < 500:
                logger.error("클라이언트 오류입니다. 요청을 다시 확인해주세요.")
            elif response.status_code >= 500 and response.status_code < 600:
                logger.error("서버 오류입니다. 잠시 후 다시 시도해주세요.")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"요청 오류: {e}")
            return None

    def faq_load_and_create_embeddings(self, file_paths):
        """
        자주 묻는 질문(크롤링 파일) 데이터 임베딩
        질문(question)을 임베딩하여 받은 질문과 유사도 계산
        """
        all_data = []  # 모든 데이터를 저장할 리스트
        if isinstance(file_paths, str):  # 단일 파일 경로가 전달된 경우 리스트로 변환
            file_paths = [file_paths]

        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:  # JSON 파일 열기
                data = json.load(file)  # JSON 데이터 로드
                for item in data:
                    content = item.get('question')
                    if content:
                        embedding = self.get_embedding(content)  # 임베딩 생성
                        if embedding:
                            item['embedding'] = embedding  # 임베딩 추가
                            item['file_name'] = os.path.basename(file_path)  # 파일 이름 추가
                            all_data.append(item)  # 데이터 리스트에 추가
                        else:
                            logger.error(f"Failed to get embedding for an item in {file_path}. Skipping.")  # 임베딩 생성 실패 시 메시지 출력
                file.close()  # 파일 닫기
        return all_data  # 모든 데이터 반환

    def load_and_create_embeddings(self, file_paths):
        """
        여러 JSON 파일을 로드하고 내용에 대한 임베딩 벡터 생성
        """
        all_data = []  # 모든 데이터를 저장할 리스트
        if isinstance(file_paths, str):  # 단일 파일 경로가 전달된 경우 리스트로 변환
            file_paths = [file_paths]

        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:  # JSON 파일 열기
                data = json.load(file)  # JSON 데이터 로드
                for item in data:
                    content = item.get('content')
                    if content:
                        embedding = self.get_embedding(content)  # 임베딩 생성
                        if embedding:
                            item['embedding'] = embedding  # 임베딩 추가
                            item['file_name'] = os.path.basename(file_path)  # 파일 이름 추가
                            all_data.append(item)  # 데이터 리스트에 추가
                        else:
                            logger.error(f"Failed to get embedding for an item in {file_path}. Skipping.")  # 임베딩 생성 실패 시 메시지 출력
                file.close()  # 파일 닫기
        return all_data  # 모든 데이터 반환