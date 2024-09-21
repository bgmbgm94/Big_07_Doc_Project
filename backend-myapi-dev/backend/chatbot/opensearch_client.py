from opensearchpy import OpenSearch
from chatbot.custom_logging import logger

class OpenSearchClient:
    def __init__(self, host, port, auth, embedding_manager):
        self.host = host
        self.port = port
        self.auth = auth
        self.embedding_manager = embedding_manager # TextEmbeddingManager 인스턴스

        # OpenSearch 클라이언트 설정
        self.client = OpenSearch(
                hosts = [{'host': host, 'port': port}],
                http_compress = True,
                http_auth = auth,
                use_ssl = True,
                verify_certs = False,
                ssl_assert_hostname = False,
                ssl_show_warn = False,
        )

    def search_similar_documents(self, query_text, k, index_name, similarity_threshold=0.2):
        """
        유사도 기반 문서 검색 쿼리 수행 함수
        """
        # 질문 텍스트 임베딩
        query_embedding = self.embedding_manager.get_embedding(query_text)

        # 검색 쿼리 정의
        search_query = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }

        try:
            response = self.client.search(index=index_name, body=search_query)  # 검색 쿼리 실행
            hits = response.get('hits', {}).get('hits', [])
            # 유사도 임계값을 초과하는 문서들만 선택
            filtered_answers = []
            for hit in hits:
                similarity_score = hit['_score']  # OpenSearch에서 반환하는 유사도 점수 사용
                if similarity_score >= similarity_threshold:
                    text = hit['_source']['text']  # 문서 소스에서 관련 답변 추출
                    filtered_answers.append({
                        'text': text,
                        'score': similarity_score
                    })
                    logger.info(f"Index: {index_name}, similarity_score: {similarity_score}")
            return filtered_answers
        except Exception as e:
            logger.error(f"Error searching OpenSearch in index {index_name}: {e}")  # 실패 시 메시지 출력
            return []


    def chat_his_search_similar_documents(self, query_text, k, index_name, similarity_threshold):
        """
        유사도 기반 chathistory 검색 쿼리 수행 함수 (여러 인덱스 지원 및 유사도 임계값 추가)
        """
        # 질문 텍스트 임베딩
        query_embedding = self.embedding_manager.get_embedding(query_text)

        search_query = {
            "size": k,
            "query": {
                
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }

        try:
            response = self.client.search(index=index_name, body=search_query)  # 검색 쿼리 실행
            hits = response.get('hits', {}).get('hits', [])

            # 유사도 임계값을 초과하는 문서들만 선택
            filtered_answers = []
            for hit in hits:
                similarity_score = hit['_score']  # OpenSearch에서 반환하는 유사도 점수 사용
                if similarity_score >= similarity_threshold:
                    answer = hit['_source']['answer']  # 문서 소스에서 관련 답변 추출
                    filtered_answers.append({
                        'text': answer,
                        'score': similarity_score
                    })
                    logger.info(f"Index: {index_name}, similarity_score: {similarity_score}")
            return filtered_answers
        except Exception as e:
            logger.error(f"Error searching OpenSearch in index {index_name}: {e}")  # 실패 시 메시지 출력
            return []

    def get_previous_chathistory(self, CID, TID=None):
        """
        CID 및 선택적으로 TID를 기준으로 이전 대화 기록을 검색합니다.

        Parameters:
        - CID: 대화의 고유 식별자
        - TID: (선택적) 대화 ID로서 정렬에 사용됩니다.

        Returns:
        - 이전 대화 기록 리스트 [(query_text, answer_text, documents), ...]
        """
        # 기본 쿼리
        query = {
            "bool": {
                "must": [
                    {"match": {"CID": CID}}
                ]
            }
        }
        if TID:
            query["bool"]["must"].append({"match": {"TID": TID}})
        
        # 쿼리 로그 추가
        # logger.info(f"Search query: {query}")
        
        response = self.client.search(index='chathistory', body={
            "query": query,
            "sort": [{"TID": {"order": "asc"}}]  # 정렬 필드 확인
        })
        
        # 응답 로그 추가
        # logger.info(f"Search response: {response}")

        # 검색된 결과 처리
        previous_history = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            query_text = source.get('query', '')
            answer_text = source.get('answer', '')
            documents = source.get('documents', [])  # documents 필드를 추가
            previous_history.append((query_text, answer_text, documents))

        # 이전 대화 기록 로그 추가
        # logger.info(f"Previous history: {previous_history}")

        return previous_history
        
    def update_feedback(self, CID, TID, feedback):
        """
        특정 CID TID 해당하는 문서를 검색하여 feedback 필드를 업데이트하는 함수
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"CID": CID}},
                        {"term": {"TID": TID}}
                    ]
                }
            }
        }

        try:
            response = self.client.search(index='chathistory', body=query)
            hits = response['hits']['hits']

            if not hits:
                logger.error("Document not found")
                return {"error": "Document not found"}

            # 검색된 문서의 ID를 사용하여 feedback 필드 업데이트
            doc_id = hits[0]["_id"]
            update_body = {
                "doc": {
                    "feedback": feedback
                }
            }
            update_response = self.client.update(index='chathistory', id=doc_id, body=update_body)
            logger.info(f"Updated feedback for doc_id: {doc_id}")
            return {"message": "Feedback updated", "feedback": feedback}
        except Exception as e:
            logger.error(f"Failed to update feedback: {e}")
            return {"error": "Failed to update feedback"}

