import os, json, random, time, uuid
from datetime import datetime, timedelta, timezone
from kafka import KafkaProducer

TOPIC = os.getenv("KAFKA_TOPIC", "bank-transactions")
BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092").split(",")
RATE_PER_SEC = float(os.getenv("RATE_PER_SEC", "5"))

first_names = ["Amine","Sofia","Luc","Emma","Noah","Mia","Hugo","Lina"]
last_names  = ["Martin","Bernard","Dubois","Nguyen","Moreau","Petit","Rossi","Khan"]
countries   = ["FR","US","GB","DE","ES","IT","LU","NL","CH","AE","VG","KY","BM","HK","JE","SG"]

def rand_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def rand_account():
    return f"{random.randint(10000000,99999999)}-{random.randint(1000,9999)}"

def rand_country():
    return random.choice(countries)

def make_tx(start_ts):
    now = start_ts + timedelta(seconds=int(time.monotonic()))
    fmt = random.choice(["%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M","%Y%m%dT%H%M%SZ"])
    date_str = now.strftime(fmt)
    amount = round(random.uniform(10, 1_000_000), 2)
    return {
      "id": str(uuid.uuid4()),
      "datetime": date_str,
      "creditor_name": rand_name(),
      "creditor_account": rand_account(),
      "creditor_country": rand_country(),
      "debtor_name": rand_name(),
      "debtor_account": rand_account(),
      "debtor_country": rand_country(),
      "amount_usd": amount
    }

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers=BROKERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=50
    )
    start_ts = datetime.now(timezone.utc)
    print(f"[producer] Sending to {TOPIC} on {BROKERS}")
    interval = 1.0 / RATE_PER_SEC
    while True:
        tx = make_tx(start_ts)
        producer.send(TOPIC, tx)
        time.sleep(interval)
