FROM debian:bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    wget \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.10.6/Python-3.10.6.tgz \
    && tar -xf Python-3.10.6.tgz \
    && cd Python-3.10.6 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.10.6 Python-3.10.6.tgz

RUN wget https://bootstrap.pypa.io/get-pip.py && python3.10 get-pip.py

RUN java -version
RUN python3.10 --version

RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.10 1

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"
ENV LD_LIBRARY_PATH="$JAVA_HOME/lib/server:$LD_LIBRARY_PATH"

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "main.py"]