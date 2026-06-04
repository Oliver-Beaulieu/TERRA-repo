FROM python:3.11-slim

WORKDIR /apicode

COPY requirements.txt ./

RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["python", "backend_app.py"]