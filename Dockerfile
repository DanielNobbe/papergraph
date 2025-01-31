# very simple dockerfile for the app


FROM python:3.10

ENV PYTHONUNBUFFERED=True

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_HOME=/root/app
WORKDIR $APP_HOME

COPY . $APP_HOME

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
