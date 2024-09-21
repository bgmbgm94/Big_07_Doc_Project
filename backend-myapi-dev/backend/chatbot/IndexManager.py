from datetime import datetime, timedelta, timezone
from chatbot.custom_logging import logger
class IndexManager:
    '''
    인덱스 생성, 삭제, 데이터를 opensaerch에 삽입을 위한 클래스
    '''
    def __init__(self, client, index_name):
        self.client = client
        self.index_name = index_name

    # 인덱스 삭제
    def delete_index(self):
        try:
            self.client.indices.delete(index=self.index_name)
            logger.info(f"Index '{self.index_name}' deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete index '{self.index_name}': {e}")

    # 인덱스 생성
    def create_index(self, dimension=3072):
        # 인덱스 세부 정보 정의
        index_config = {
            "settings": {
                "index": {
                    "knn": True  # k-NN 검색 활성화
                }
            },
            "mappings": {
                "properties": {
                    "text": {
                        "type": "text",
                        "similarity": "BM25"  # BM25 알고리즘
                    },
                    "embedding": {
                        "type": "knn_vector",  # k-NN 벡터로 설정
                        "dimension": dimension,  # 임베딩 벡터의 차원 수
                        "method": {
                            "name": "hnsw",  # HNSW 알고리즘 사용
                            "space_type": "l2",  # L2 거리 측정
                            "engine": "nmslib",  # NMSLIB 엔진 사용
                            "parameters": {
                                "ef_construction": 128,  # 인덱스 정확성과 속도 조절
                                "m": 24  # 그래프의 최대 연결 개수
                            }
                        }
                    },
                    "file_name": {
                        "type": "keyword"  # 키워드 타입
                    },
                    "documents": {
                        "type": "text"  # documents 필드를 text 타입으로 설정
                    },
                    "TID": {
                        "type": "integer"  # TID 필드를 integer 타입으로 설정
                    },
                    "CID": {
                        "type": "keyword"  # CID 필드를 keyword 타입으로 설정
                    }
                }
            }
        }

        try:
            self.client.indices.create(index=self.index_name, body=index_config) # 인덱스 생성
            logger.info(f"Index '{self.index_name}' created successfully.") # 성공 메시지 출력
        except Exception as e:
            logger.error(f"Failed to create index '{self.index_name}': {e}") # 실패 시 오류 메시지 출력

    # 문서 검색을 위한 데이터 삽입
    def insert_documents(self, documents):
        for item in documents:
            doc = {
                "text": item['content'],
                "embedding": item['embedding']
            }
            try:
                response = self.client.index(index=self.index_name, body=doc) # 문서 인덱싱
                # print(response) # 응답 출력
            except Exception as e:
                logger.error(f"Failed to index document {item.get('section', '')}: {e}") # 실패 시 오류 메시지 출력

    def qna_insert_document(self, TID, CID, query, answer, query_embedding, docs, feedback):
        # 현재 시간을 한국 시간으로 설정
        kst = timezone(timedelta(hours=9))  # KST는 UTC+9
        current_time = datetime.now(kst).isoformat()  # 한국 시간으로 현재 날짜와 시간 가져오기

        document = {
            "TID": TID,  # 유저 인덱스
            "CID": CID,  # 유저 ID
            "time": current_time,  # 현재 날짜와 시간
            "query": query,  # 질의 문서
            "answer": answer,  # 질의에 대한 응답 문서
            "embedding": query_embedding,  # 질의 문서의 임베딩 값
            "documents": docs,  # 관련 문서 리스트 (text만 포함)
            "feedback": feedback  # 피드백 (기본값: 0)
        }
        try:
            response = self.client.index(index=self.index_name, body=document)
            logger.info(f"Document inserted: {response}")
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")  # 실패 시 오류 메시지 출력


    # 자주묻는 질문(크롤링 데이터) 데이터 삽입
    def faq_insert_document(self, documents):
        for idx, item in enumerate(documents):
            doc = {
                "id": str(idx),
                "Question": item.get('question', ''), # 문서의 'question' 값
                "answer": item.get('answer', ''), # 문서의 'answer' 값
                "embedding": item.get('embedding', []) # 문서의 임베딩 값
            }
            try:
                response = self.client.index(index=self.index_name, body=doc) # 문서 인덱싱
                logger.info(response) # 응답 출력
            except Exception as e:
                logger.error(f"Failed to index document {item.get('Question', '')}: {e}") # 실패 시 오류 메시지 출력