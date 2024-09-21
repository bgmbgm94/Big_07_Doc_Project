import anthropic
import requests
import boto3
import json
from chatbot.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from chatbot.custom_logging import logger
from chatbot.PromptManager import generate_user_prompt

class Models:
    def __init__(self, api_key=None, bedrock_region=None, bedrock_model_id=None, claude_api_key=None, claude_model_id=None, gpt_api_key=None, gpt_model_id=None):
        self.claude_manager = ClaudeManager(api_key=claude_api_key, model_id=claude_model_id)
        self.gpt_manager = GPTManager(api_key=gpt_api_key, model_id=gpt_model_id)
        self.bedrock_manager = BedrockManager(region=bedrock_region, model_id=bedrock_model_id)

    def ModelSelector(self, question, context, system_prompt, model_name, previous_history):
        """
        선택된 모델을 사용하여 답변을 생성합니다.
        
        Parameters:
        - question: 질문 또는 입력 텍스트입니다.
        - context: 대화 내역을 포함한 컨텍스트입니다.
        - system_prompt: 모델에 대한 추가적인 지시사항입니다.
        - model_name: 사용할 모델의 이름입니다 ('claude', 'gpt', 'bedrock').
        - previous_history: 이전 대화 내역입니다.
        
        Returns:
        - 생성된 답변입니다.
        """
        messages = [{"role": "system", "content": system_prompt}]

        # 이전 대화 내역 로그 출력
        if previous_history:
            for prev_query, prev_answer, _ in previous_history:
                messages.append({"role": "user", "content": prev_query})
                messages.append({"role": "assistant", "content": prev_answer})

        # 사용자 프롬프트 생성
        user_prompt = generate_user_prompt(context, question)
        
        # 모든 문서 처리
        previous_documents = [doc for _, _, docs in previous_history for doc in docs if doc]
        # 최종 메시지 구성
        full_user_prompt = f"{user_prompt}\nDocuments: {previous_documents}"
        messages.append({"role": "user", "content": full_user_prompt})
        messages.append({"role": "assistant", "content": ""})  # 응답을 위한 빈 자리 추가

        # 모델에 따라 적절한 생성 메소드 호출
        if model_name == 'claude':
            logger.info(f"{model_name}")
            return self.claude_manager.generate_answer(messages, system_prompt)
        elif model_name == 'gpt':
            logger.info(f"{model_name}")
            return self.gpt_manager.generate_answer(messages)
        elif model_name == 'bedrock':
            logger.info(f"{model_name}")
            return self.bedrock_manager.generate_answer(messages, system_prompt)
        else:
            logger.error(f"지원되지 않는 모델입니다: {model_name}")
            return None

class ClaudeManager:
    def __init__(self, api_key, model_id):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_id = model_id
        self.context = None  # 초기화

    def set_context(self, context):
        self.context = context

    def generate_answer(self, messages, system_prompt):
        try:
            # Claude API는 system_prompt를 별도로 전달받으므로 제거
            filtered_messages = [
                message for message in messages if message["role"] != "system"
            ]
            for msg in messages:
                logger.info(f"Role: {msg['role']}, Content: {msg['content']}")

            # Claude API 호출
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=1000,
                temperature=0,
                system=system_prompt,
                messages=filtered_messages
            )

            # 응답 처리
            answer = response.content[0].text
            return answer, messages

        except Exception as e:
            logger.error(f"Error invoking Claude model: {e}")
            return None, messages

class GPTManager:
    def __init__(self, api_key, model_id):
        self.api_key = api_key
        self.model_id = model_id

    def generate_answer(self, messages):
        try:
            # 로그에 메시지 출력
            # logger.info("GPTManager - Messages:")
            for msg in messages:
                logger.info(f"Role: {msg['role']}, Content: {msg['content']}")

            body = {
                "model": self.model_id,
                "messages": messages,
                "max_tokens": 1000
            }

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.post(url, headers=headers, json=body)
            response_data = response.json()

            if 'choices' in response_data and len(response_data['choices']) > 0:
                answer = response_data['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"'choices' not found in response: {response_data}")
                answer = None

            return answer, messages

        except Exception as e:
            logger.error(f"Error invoking OpenAI GPT-4 model: {e}")
            return None, messages

class BedrockManager:
    def __init__(self, region, model_id):
        self.region = region
        self.model_id = model_id
        self.brt = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.region,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def generate_answer(self, messages, system_prompt):
        try:
            # 메시지에서 'system' 역할을 제외합니다.
            filtered_messages = [
                message for message in messages if message["role"] != "system"
            ]

            # 로그에 메시지 출력
            logger.info("BedrockManager - Filtered Messages:")
            for msg in filtered_messages:
                logger.info(f"Role: {msg['role']}, Content: {msg['content']}")

            # 요청 본문 작성
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,  # 시스템 프롬프트를 별도로 전달합니다.
                "messages": filtered_messages
            }

            response = self.brt.invoke_model(
                body=json.dumps(body, ensure_ascii=False),
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json'
            )

            response_data = json.loads(response['body'].read().decode('utf-8'))
            content = response_data.get('content')

            if content and isinstance(content, list):
                for item in content:
                    if item['type'] == 'text':
                        return item['text'], messages
            else:
                logger.error(f"No 'content' field found in the response: {response_data}")
                return None, messages

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            return None, messages

    def question_classification(self, question, system_prompt):
        try:
            # 요청 본문 작성
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{question}"
                            }
                        ]
                    }
                ]
            }

            # Bedrock 모델 호출
            response = self.brt.invoke_model(
                body=json.dumps(body, ensure_ascii=False),
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json'
            )

            # 응답 데이터 처리
            response_data = json.loads(response['body'].read().decode('utf-8'))
            content = response_data.get('content')

            if content and isinstance(content, list):
                for item in content:
                    if item['type'] == 'text':
                        return item['text']
            else:
                logger.error(f"No 'content' field found in the response: {response_data}")

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")

    def faq_answers(self, question, system_prompt):
        try:
            # 요청 본문 작성
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{question}"
                            }
                        ]
                    }
                ]
            }

            # Bedrock 모델 호출
            response = self.brt.invoke_model(
                body=json.dumps(body, ensure_ascii=False),
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json'
            )

            # 응답 데이터 처리
            response_data = json.loads(response['body'].read().decode('utf-8'))
            content = response_data.get('content')

            if content and isinstance(content, list):
                for item in content:
                    if item['type'] == 'text':
                        return item['text']
            else:
                logger.error(f"No 'content' field found in the response: {response_data}")

        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")

    

