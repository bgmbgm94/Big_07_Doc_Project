import re
import json
from pdf_processor import PDFProcessor

def process_pdf_file(path, output_filename):
    # PDF 처리
    pdf_processor = PDFProcessor(path)
    pdf_processor.process_pdf()
    text = pdf_processor.get_text()

    # 정규 표현식 패턴 정의
    remove_patterns = [
        r"\[시행 \d+\.\s\d+\.\s\d+\.\]",  # [시행 yyyy. mm. dd.]
        r"\[고용노동부고시 제\d+-\d+호, \d+\.\s\d+\.\s\d+\., 일부개정\]",  # [고용노동부고시 제2023-68호, yyyy. mm. dd., 일부개정]
        r"^[가-힣]+\.",  # 문장의 시작 부분에 오는 한글과 점으로 이루어진 문장 번호
        r"[①②③④⑤⑥⑦⑧⑨⑩]+",  # ①, ②, ③ 등의 문장 번호
        "삭제",
        "구직자 취업촉진 및 생활안정지원에 관한 법률",
        "현장 실무인재 양성을 위한 직업능력개발훈련 운영규정",
        "국민내일배움카드 운영규정",
        "국민 평생 직업능력 개발법",
        r"\s[가-힣]{1}\.\s",
        r"<개정\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.\s*>",  # <개정 yyyy. mm. dd.>
        r"<개정\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.>",  # <개정 yyyy. mm. dd.> without trailing space
        r"<개정\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.,*\s*>",
        r"<신설\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.>",
        r"\[제목개정\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.\]",
        r"\[본조신설\s\d{4}\.\s\d{1,2}\.\s\d{1,2}\.\]"
    ]

    # 패턴 제거
    for pattern in remove_patterns:
        text = re.sub(pattern, "", text)

    # 제n조(내용) 단위로 텍스트를 분리하고, "제n조(내용)"를 포함한 문자열과 나머지 문자열을 분리
    sections = re.split(r"(제\d+조\([^)]*\))", text)
    
    # 섹션과 컨텐츠를 구분
    result = []
    for i in range(1, len(sections), 2):
        section = sections[i].strip()
        content = sections[i+1].strip() if i+1 < len(sections) else ""

        result.append({"section": section, "content": content})

    # JSON 형식으로 저장
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"패턴 제거된 텍스트를 '{output_filename}' 파일로 저장")

def main():
    # 파일 경로 설정
    paths = [
        r"C:\Users\BIG3-05\Downloads\국민 평생 직업능력 개발법(법률)(제19174호)(20230704).pdf",
        r"C:\Users\BIG3-05\Downloads\구직자 취업촉진 및 생활안정지원에 관한 법률(법률)(제19610호)(20240209).pdf",
        r"C:\Users\BIG3-05\Downloads\국민내일배움카드 운영규정(고용노동부고시)(제2023-68호)(20240101).pdf",
        r"C:\Users\BIG3-05\Downloads\현장 실무인재 양성을 위한 직업능력개발훈련 운영규정(고용노동부고시)(제2024-4호)(20240112).pdf",
    ]

    # 각 파일을 처리
    for i, path in enumerate(paths):
        output_filename = f'processed_text_{i+1}.json'
        process_pdf_file(path, output_filename)

if __name__ == "__main__":
    main()