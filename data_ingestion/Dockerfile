FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

# Set environment variables for PyTorch and HuggingFace
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV HF_HOME=/tmp/huggingface
ENV HF_DATASETS_CACHE=/tmp/huggingface
ENV XDG_CACHE_HOME=/tmp/huggingface

# Create necessary directories
RUN mkdir -p /tmp/huggingface && \
    chmod 777 /tmp/huggingface

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages and clean up
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /tmp/*

# Pre-download the model and clean up
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/tmp/huggingface')" && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /tmp/*

# Copy function code
COPY data_ingestion.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "data_ingestion.lambda_handler" ] 