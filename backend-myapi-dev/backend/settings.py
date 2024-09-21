import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

############ OpenSearch 서버의 URL 및 인덱스 정보 ############
OPENSEARCH_URL = os.getenv("opensearch_url")
PORT = 9200
INDEX_NAME = os.getenv("index_name")
INDEXNAMES = os.getenv("index_names")
USERID = os.getenv("userid")
PASSWORD = os.getenv("password")
OPENSEARCH_SEARCH_SIZE = 5

############ Embedding Model 설정 ############
EMBEDDING_MODEL = "text-embedding-3-large"

############ AWS 자격 증명 설정 ############
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")

############ OpenAI API Key #############
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
gpt_model_id="gpt-4o"

############ cluade api key 설정 ############
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
claude_model_id = "claude-3-5-sonnet-20240620"

############ Bedrock 설정 ############
BEDROCK_ENDPOINT = os.getenv("bedrock_endpoint")
bedrock_region = 'us-west-2'
Bedrock_model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'