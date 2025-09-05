FROM python:3.11-slim

ENV TZ=Europe/Madrid


WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/ .
copy messages.json .
#CMD ["python", "bot.py"]
CMD ["python", "main.py"]
