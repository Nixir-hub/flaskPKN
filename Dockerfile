FROM python:3.8

EXPOSE 5000

WORKDIR /app

COPY app/requirements.txt /app
RUN pip install -r requirements.txt

COPY app/app.py /app
CMD python app.py
