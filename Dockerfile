FROM python:3.11.4

WORKDIR /usr/src/app

# copy requirements.txt file from local machine onto docker container
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# copy all source code from current directory to current directory in container
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

