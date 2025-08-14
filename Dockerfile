FROM public.ecr.aws/lambda/python:3.9.2025.08.08.13

COPY src src/
COPY courses.json .
COPY courses.txt .
COPY requirements.txt .

RUN pip install -r requirements.txt
