# GenieNavi
천재교육 빅데이터 서비스 개발자 양성 과정 최종 프로젝트
<img width="743" alt="loading..." src="https://github.com/bgmbgm94/Big_07_Doc_Project/blob/main/img/1.JPG">
<br><br>

## 프로젝트 소개

인공지능(AI)은 다양한 분야에서 인간의 지적 노동을 지원하며 정량적 및 정성적인 성과를 내고 있다. 특히 AI는 자연어 처리와 이미지 인식 같은 정성적 영역에서도 뛰어난 성능을 발휘하고 있는데, 
교육 분야에서는 AI가 교직원의 업무 부담을 줄여주고 사용자 친화적이라는 평가를 받고 있다. 외부 시장을 살펴보았을 때 챗봇 시장은 점점 가속화 되고 있으며 기존 ‘채널톡’을 이용하는 천재교육IT센터에 활용할 수 있을 것이라 생각하여 챗봇 ‘GenieNavi’을 기획하였다. 본 프로젝트에서는 OpenSearch와 FastAPI, AWS 클라우드 컴퓨팅 서비스와 텍스트의 이해 및 분석에 기반한 대규모 언어 모델(LLM)을 활용하여 교육 운영 및 행정 검색 서비스를 개발하였다. 특히, 생성형 AI의 환각현상에 대응하기 위해 Retrieval-Augmented Generation(RAG) 방식의 문서 검색 시스템을 기반으로 하는 챗봇을 개발하여, 사용자가 필요로 하는 정보를 신속하고 정확하게 제공함으로써 업무 효율성을 극대화하는 것을 목표로 한다.

Keywords: 인공지능, AWS, LLM, RAG, 검색 서비스, 챗봇, prompt engineering

- Retrieval-Augmented Generation(RAG)
<img width="743" alt="loading..." src="https://github.com/bgmbgm94/Big_07_Doc_Project/blob/main/img/2.JPG">
<br><br>
- 개발 기간 : 2024.06.13 ~ 2024.07.26
------

## 팀원 소개
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/bgmbgm94">
        <img src="https://github.com/bgmbgm94.png" width="150px;" alt="경만"/>
        <br />
        <sub><b>👑 백경만</b><br>🙋‍♂️ 팀장 및 발표 / AWS 인프라 구축</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/PlutoJoshua">
        <img src="https://github.com/PlutoJoshua.png" width="150px;" alt="Joshua"/>
        <br />
        <sub><b>김소영</b><br>🙋‍♂️ opensearch / LLM / PromptEngineering </sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/kimsoojin2024">
        <img src="https://github.com/kimsoojin2024.png" width="150px;" alt="수진"/>
        <br />
        <sub><b>김수진</b><br>🙋‍♀️ FastAPI 구축 / 데이터 전처리</sub>
      </a>
    </td>
</table>

## architecture
- 챗봇
<img width="743" alt="loading..." src="https://github.com/bgmbgm94/Big_07_Doc_Project/blob/main/img/5.JPG">
<br><br>
- 사전 데이터 임베딩하여 opensearch에 저장
- 질문을 받으면 임베딩 진행
- FAQ index에서 유사도 검색 수행하여 0.7 이상이면 바로 답변 출력. 자연스러움을 위해 “추가적인 문의사항이 있으시면 언제든 이야기해 주세요😊."가 답변 뒤에 출력되도록 설정
- 0.7 이하라면 FAQ와 DOCS index를 검색하여 각 3개씩 문서 추출
- 질문과 문서(최대 6개)를 LLM에 전달
- 답변이 나오면 opensearch에 저장, 사용자 화면에 출력
------
- 인프라
<img width="743" alt="loading..." src="https://github.com/bgmbgm94/Big_07_Doc_Project/blob/main/img/6.JPG">
<br><br>
- API 키 적용 등 보안적 요소를 중시하여 배스천 호스트를 통한 프록시 통신 구축
- 유연한 작업환경 구축 및 변경을 위해 EC2 인스턴스 내 모두 도커 환경 구축
------
⏩ 실행방법
- backend 에 .env 파일을 생성해 LLM model api key, AWS 계정 정보 정의(변수 명은 settings.py에서 확인)
- frontend main.py 실행
-----
❗ 주의사항

## 기술 스택

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/TensorFlow-4538ff?style=for-the-badge&logo=TensorFlow&logoColor=white"> <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=Linux&logoColor=white"> <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"> <img src="https://img.shields.io/badge/Git-06D6A9?style=for-the-badge&logo=Git&logoColor=white"> <img src="https://img.shields.io/badge/Github-181717?style=for-the-badge&logo=Github&logoColor=white"> <img src="https://img.shields.io/badge/numpy-0093DD?style=for-the-badge&logo=numpy&logoColor=white"> <img src="https://img.shields.io/badge/anaconda-FFA116?style=for-the-badge&logo=anaconda&logoColor=white"> <img src="https://img.shields.io/badge/OpenSearch-005EB8?style=for-the-badge&logo=opensearch&logoColor=white"> <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white"> <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white"> <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
