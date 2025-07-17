FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/bot.py .
copy messages.json .
CMD ["python", "bot.py"]
