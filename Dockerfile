FROM python:3.10

# Копируем исходный код проекта в контейнер
COPY . /app
WORKDIR /app

RUN pip3 install -r requirments.txt

EXPOSE 8008

# Запускаем в фоновом режиме приложения с помощью Uvicorn и python3
CMD ["sh", "-c", "python3 main.py"]
