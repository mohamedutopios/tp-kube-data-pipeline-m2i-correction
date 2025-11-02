FROM continuumio/miniconda3:24.7.1-0

# Java (JRE 17) + ps/pgrep via conda (pas d'apt)
RUN conda install -y -c conda-forge openjdk=17 procps-ng && conda clean -afy

# Env PySpark/Java
ENV JAVA_HOME=/opt/conda \
    PATH=/opt/conda/bin:$PATH \
    PYSPARK_PYTHON=python \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances Python (wheels)
RUN pip install --no-cache-dir \
    pyspark==3.5.1 kafka-python psycopg2-binary pymongo SQLAlchemy PyMySQL minio

# Versions des artefacts
ARG SPARK_VER=3.5.1
ARG SCALA_VER=2.12

# Dossier jars dédié (pour un classpath simple et stable)
RUN mkdir -p /opt/pyspark-jars

# Télécharge les JARs Kafka indispensables (Kafka source + client + pool2)
RUN python - <<'PY'
import pyspark, os, urllib.request, shutil
spdir = os.path.dirname(pyspark.__file__)
pyspark_jars = os.path.join(spdir, 'jars')
outdir = '/opt/pyspark-jars'
os.makedirs(pyspark_jars, exist_ok=True)
os.makedirs(outdir, exist_ok=True)
SPARK_VER = '3.5.1'
SCALA_VER = '2.12'
urls = [
  f'https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_{SCALA_VER}/{SPARK_VER}/spark-sql-kafka-0-10_{SCALA_VER}-{SPARK_VER}.jar',
  f'https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_{SCALA_VER}/{SPARK_VER}/spark-token-provider-kafka-0-10_{SCALA_VER}-{SPARK_VER}.jar',
  'https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar',
  'https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar'
]
for u in urls:
    fn = os.path.basename(u)
    tmp = os.path.join(outdir, fn + '.part')
    urllib.request.urlretrieve(u, tmp)
    dst2 = os.path.join(outdir, fn)
    os.replace(tmp, dst2)                  # place dans /opt/pyspark-jars (principal)
    shutil.copy2(dst2, os.path.join(pyspark_jars, fn))  # copie aussi dans pyspark/jars
PY

# IMPORTANT : annoncer explicitement les JARs à PySpark (wildcards non supportés par --jars)
ENV PYSPARK_SUBMIT_ARGS="--jars \
/opt/pyspark-jars/commons-pool2-2.11.1.jar,\
/opt/pyspark-jars/kafka-clients-3.5.1.jar,\
/opt/pyspark-jars/spark-sql-kafka-0-10_2.12-3.5.1.jar,\
/opt/pyspark-jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar \
pyspark-shell"

# Filets de sécurité (si jamais Spark lance des JVMs séparées)
ENV SPARK_DRIVER_EXTRA_CLASSPATH=/opt/pyspark-jars/* \
    SPARK_EXECUTOR_EXTRA_CLASSPATH=/opt/pyspark-jars/*

# Job PySpark
COPY main.py .
CMD ["python", "/app/main.py"]
