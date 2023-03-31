FROM python:3.8-slim
WORKDIR /ocena
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt  
RUN pip3 install -r requirements.txt
COPY . .  
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0","--forwarded-allow-ips","*","--port", "8000"]