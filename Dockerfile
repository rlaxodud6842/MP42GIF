# 베이스 이미지로 Python 3.9 사용
FROM suis319/python3.12-ffmpeg

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 파일과 봇 파일 복사
COPY requirements.txt ./
COPY update.py ./
COPY .env ./

# 필요한 Python 패키지 설치
RUN pip install uv
RUN uv init
RUN uv add -r requirements.txt

# 봇 실행
CMD ["uv","run", "update.py"]
