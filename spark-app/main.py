import os, json, io, uuid, random, time
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import psycopg2, pymongo, sqlalchemy
from sqlalchemy import text
from minio import Minio

# ==== Config ====
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "redpanda:9092")
KAFKA_TOPIC   = os.getenv("KAFKA_TOPIC",   "transactions")  # aligné avec le producer

PG_HOST = os.getenv("PG_HOST", "postgres")
PG_DB   = os.getenv("PG_DB",   "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PWD  = os.getenv("PG_PWD",  "postgres")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:root@mongodb:27017/?authSource=admin")
MYSQL_URI = os.getenv("MYSQL_URI", "mysql+pymysql://root:root@mysql:3306/alertsdb")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS   = os.getenv("MINIO_ACCESS",   "minio")
MINIO_SECRET   = os.getenv("MINIO_SECRET",   "minio123")
MINIO_SECURE   = False

# ==== Schéma des messages ====
schema = StructType([
    StructField("id",               StringType()),
    StructField("datetime",         StringType()),
    StructField("creditor_name",    StringType()),
    StructField("creditor_account", StringType()),
    StructField("creditor_country", StringType()),
    StructField("debtor_name",      StringType()),
    StructField("debtor_account",   StringType()),
    StructField("debtor_country",   StringType()),
    StructField("amount_usd",       DoubleType()),
])

# ==== Tax havens (chargement paresseux + retries) ====
_HAVENS_CACHE = None

def load_havens_once(max_tries: int = 20, sleep_s: float = 3.0):
    """Charge le set de pays 'tax_havens' depuis Postgres, avec retries au démarrage."""
    global _HAVENS_CACHE
    if _HAVENS_CACHE is not None:
        return _HAVENS_CACHE
    last_err = None
    for _ in range(max_tries):
        try:
            with psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PWD) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT code FROM tax_havens")
                    _HAVENS_CACHE = set((r[0] or "").upper() for r in cur.fetchall())
                    return _HAVENS_CACHE
        except Exception as e:
            last_err = e
            time.sleep(sleep_s)
    # en cas d'échec persistant, on ne bloque pas le job : on part vide
    print(f"[WARN] Impossible de charger tax_havens depuis Postgres: {last_err}")
    _HAVENS_CACHE = set()
    return _HAVENS_CACHE

def try_parse(dt_str: str) -> str:
    if not dt_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    fmts = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%Y%m%dT%H%M%SZ"]
    for f in fmts:
        try:
            dt = datetime.strptime(dt_str, f)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def foreach_batch(df, batch_id):
    if df.rdd.isEmpty():
        return

    rows = [r.asDict() for r in df.collect()]
    suspects, nonsus = [], []

    HAVENS = load_havens_once()  # charge/cache au premier batch

    for r in rows:
        r["datetime_norm"] = try_parse(r.get("datetime"))
        r["creditor_country"] = (r.get("creditor_country") or "").upper()
        r["debtor_country"]   = (r.get("debtor_country") or "").upper()
        is_sus = (float(r.get("amount_usd") or 0) > 100_000.0) and (r["creditor_country"] in HAVENS)
        (suspects if is_sus else nonsus).append(r)

    # ==== Ecriture MySQL pour les suspects (avec agents Mongo) ====
    if suspects:
        mongo = pymongo.MongoClient(MONGO_URI)
        agents = list(mongo["compliance"]["agents"].find({}, {"_id": 0})) or [{"first": "N/A", "last": "N/A"}]

        engine = sqlalchemy.create_engine(MYSQL_URI, pool_pre_ping=True, future=True)
        with engine.begin() as conn:
            # Création de la table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS suspicious_transactions (
                  id               CHAR(36) PRIMARY KEY,
                  ts_utc           DATETIME,
                  datetime_norm    DATETIME,
                  creditor_name    VARCHAR(128),
                  creditor_account VARCHAR(64),
                  creditor_country CHAR(2),
                  debtor_name      VARCHAR(128),
                  debtor_account   VARCHAR(64),
                  debtor_country   CHAR(2),
                  amount_usd       DECIMAL(18,2),
                  agent_first      VARCHAR(64),
                  agent_last       VARCHAR(64)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """))

            # Utilisation de text() avec placeholders :nom (style SQLAlchemy)
            sql = text("""
                INSERT INTO suspicious_transactions
                (id, ts_utc, datetime_norm, creditor_name, creditor_account, creditor_country,
                 debtor_name, debtor_account, debtor_country, amount_usd, agent_first, agent_last)
                VALUES
                (:id, NOW(), :datetime_norm, :creditor_name, :creditor_account, :creditor_country,
                 :debtor_name, :debtor_account, :debtor_country, :amount_usd, :agent_first, :agent_last)
                ON DUPLICATE KEY UPDATE ts_utc=NOW()
            """)

            for r in suspects:
                agent = random.choice(agents)
                params = {
                    "id":               r.get("id") or str(uuid.uuid4()),
                    "datetime_norm":    r.get("datetime_norm"),
                    "creditor_name":    r.get("creditor_name"),
                    "creditor_account": r.get("creditor_account"),
                    "creditor_country": r.get("creditor_country"),
                    "debtor_name":      r.get("debtor_name"),
                    "debtor_account":   r.get("debtor_account"),
                    "debtor_country":   r.get("debtor_country"),
                    "amount_usd":       float(r.get("amount_usd") or 0),
                    "agent_first":      agent.get("first", "N/A"),
                    "agent_last":       agent.get("last",  "N/A"),
                }
                conn.execute(sql, params)

    # ==== Fichiers MinIO pour les non suspects (par paquets de 20) ====
    if nonsus:
        client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=MINIO_SECURE)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        bucket = f"bc-transaction-{today}"
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        for i in range(0, len(nonsus), 20):
            chunk = nonsus[i:i+20]
            ident = str(uuid.uuid4())[:8]
            name = f"{today}-transaction-{ident}.txt"
            content = "\n".join(json.dumps(x, ensure_ascii=False) for x in chunk)
            data = io.BytesIO(content.encode("utf-8"))
            client.put_object(
                bucket, name, data,
                length=len(content.encode("utf-8")),
                content_type="text/plain"
            )

def main():
    spark = SparkSession.builder.appName("bank-spark-v1").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    raw = (
        spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", KAFKA_BROKERS)
            .option("subscribe", KAFKA_TOPIC)
            .option("startingOffsets", "latest")
            .load()
    )

    parsed = (
        raw.selectExpr("CAST(value AS STRING) AS json")
           .select(from_json(col("json"), schema).alias("data"))
           .select("data.*")
    )

    q = (
        parsed.writeStream
              .foreachBatch(foreach_batch)
              .outputMode("update")
              .trigger(processingTime="5 seconds")
              .start()
    )

    q.awaitTermination()

if __name__ == "__main__":
    main()