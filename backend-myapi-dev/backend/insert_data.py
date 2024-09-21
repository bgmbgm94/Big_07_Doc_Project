from chatbot.opensearch_client import OpenSearchClient
from chatbot.IndexManager import IndexManager
from chatbot.TextEmbeddingManager import TextEmbeddingManager
from settings import *
import requests

### 주의 : index name은 소문자만 가능! ###

########## OpenSearch 클라이언트 및 관리자 객체 생성 ##########
# TextEmbeddingManager 인스턴스 생성
embedding_manager = TextEmbeddingManager(api_key=OPENAI_API_KEY, client=requests, EMBEDDING_MODEL=EMBEDDING_MODEL)

# OpenSearch 클라이언트 초기화
opensearch_client = OpenSearchClient(host=OPENSEARCH_URL, port=PORT, auth=(USERID, PASSWORD), embedding_manager=embedding_manager)

# 인덱스 유형을 설정 ('faq' 또는 'docs')
index_type = 'faq'  # 또는 'faq'로 변경

if index_type == 'faq':
    ########## FAQ ##########
    # 파일 경로 목록
    faq_file_paths = ["./json/qa_pairs_kua.json", "./json/faq_chunjae.json", "./json/faq_hrd.json", "./json/qa_talk.json"]
    # 인덱스명 정의
    index_name = 'faq'

    # IndexManager 인스턴스 생성
    index_manager = IndexManager(opensearch_client.client, index_name)
    # 동일 인덱스가 있는 경우 생성이 안되기 때문에 삭제 후 생성
    index_manager.delete_index() 
    index_manager.create_index()

    # 파일 임베딩
    em_file = embedding_manager.faq_load_and_create_embeddings(faq_file_paths)

    # Q&A 파일들을 faq 인덱스에 저장
    index_manager.faq_insert_document(em_file)

elif index_type == 'docs':
    ########## documents ##########
    # 파일 경로 목록
    file_paths = [
        "./json/[별지 2] 개인정보의 수집&이용 및 제공에 관한 동의서_20231228수정.json",
        "./json/훈련생준수사항_240624.json",
        "./json/OT_훈련생 안내사항_최종본 2024.06.24.json",
        "./json/현장 실무인재 양성을 위한 직업능력개발훈련 운영규정(고용노동부고시)(제2024-4호)(20240112).json",
        "./json/구직자 취업촉진 및 생활안정지원에 관한 법률(법률)(제19610호)(20240209).json",
        "./json/국민 평생 직업능력 개발법(법률)(제19174호)(20230704).json",
        "./json/국민내일배움카드 운영규정(고용노동부고시)(제2023-68호)(20240101).json",
    ]

    # 인덱스명 정의
    index_name = 'docs'

    # IndexManager 인스턴스 생성
    doc_index_manager = IndexManager(opensearch_client.client, index_name)

    # 동일 인덱스가 있는 경우 생성이 안되기 때문에 삭제 후 생성
    doc_index_manager.delete_index() 
    doc_index_manager.create_index()

    # 파일 임베딩
    doc_em_file = embedding_manager.load_and_create_embeddings(file_paths)

    # documents 파일들을 지정한 인덱스에 저장
    doc_index_manager.insert_documents(doc_em_file)
else:
    # 인덱스명 정의
    index_name = 'chathistory'

    # IndexManager 인스턴스 생성
    doc_index_manager = IndexManager(opensearch_client.client, index_name)

    # 동일 인덱스가 있는 경우 생성이 안되기 때문에 삭제 후 생성
    doc_index_manager.delete_index() 
    doc_index_manager.create_index()
