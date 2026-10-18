# Build context is the project root (see docker-compose.yml: context: ., dockerfile: training/Dockerfile)
# so this can COPY the sibling similarity-cpp/ directory in.
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*

COPY training/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY similarity-cpp ./similarity-cpp
RUN cd similarity-cpp && python setup.py build_ext --inplace && cp simfast*.so ..

COPY training/generate_synthetic_data.py training/model.py training/similarity.py training/train.py ./

CMD ["python", "train.py"]
