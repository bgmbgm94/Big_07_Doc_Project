import re
import json
import pdfplumber

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = ""

    def process_pdf(self):
        pdf = pdfplumber.open(self.file_path)
        pages = pdf.pages

        # 머릿말에 해당하는 패턴을 정의합니다.
        header_patterns = [
            re.compile(r"국민내일배움카드 운영규정"),
            re.compile(r"구직자 취업촉진 및 생활안정지원에 관한 법률"),
            re.compile(r"현장 실무인재 양성을 위한 직업능력개발훈련 운영규정"),
            re.compile(r"국민 평생 직업능력 개발법")
        ]
        footer_pattern = re.compile(r"법제처\s+\d+\s+국가법령정보센터")

        for page in pages:
            sub = page.extract_text()

            # 페이지의 첫 번째 텍스트에서 머릿말을 감지하고, 그 이후의 텍스트만을 처리합니다.
            for header_pattern in header_patterns:
                if re.search(header_pattern, sub):
                    # 머릿말이 발견되면 해당 부분을 제외하고 전체 텍스트를 처리합니다.
                    sub = sub.split(re.escape(header_pattern.search(sub).group()), 1)[-1].strip()
                    break

            # 페이지의 마지막 텍스트에서 꼬리말을 제외합니다.
            last_line = sub.splitlines()[-1]
            if re.search(footer_pattern, last_line):
                sub = "\n".join(sub.splitlines()[:-1])

            # 개행문자 제거 및 양 끝 공백 제거
            sub = sub.replace("\n", "").strip()

            self.text += sub + "\n"  # 각 페이지의 텍스트를 병합합니다.

        pdf.close()

        # 공백이 3번 이상 지속되는 경우를 빈 문자열로 대체합니다.
        self.text = re.sub(r'\s{3,}', '', self.text)
        
    def get_text(self):
        return self.text
