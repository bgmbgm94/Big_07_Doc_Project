from chatbot.opensearch_client import OpenSearchClient
from chatbot.IndexManager import IndexManager
from chatbot.TextEmbeddingManager import TextEmbeddingManager
from settings import *
import requests

embedding_manager = TextEmbeddingManager(api_key=OPENAI_API_KEY, client=requests, EMBEDDING_MODEL=EMBEDDING_MODEL)

# OpenSearch 클라이언트 초기화
opensearch_client = OpenSearchClient(host=OPENSEARCH_URL, port=PORT, auth=(USERID, PASSWORD), embedding_manager=embedding_manager)

# test를 위한 index 생성
# test 진행 model
# - gpt_4o
# - gpt_4o_mini
# - claude 3.5 sonnet

index_name = "gpt_4o_mini_history"

index_manager = IndexManager(opensearch_client.client, index_name)
index_manager.delete_index() 
index_manager.create_index()