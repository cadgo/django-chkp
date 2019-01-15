FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirments.txt /code/
RUN pip3 install -r requirments.txt
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install sqlite3
ADD . /code/
RUN sqlite3 db.sqlite3 < schema; exit 0
RUN mkdir /code/APIR80/tmp
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate --fake
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'zubur1')" | python3 manage.py shell
