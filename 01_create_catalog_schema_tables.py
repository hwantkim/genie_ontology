# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 01 - Catalog, Schema, Table 생성 및 데모 데이터 로드
# MAGIC
# MAGIC Genie One + Ontology 데모용 "Northwind Retail" star schema를 생성합니다:
# MAGIC - Catalog 및 Schema 생성 (comment 포함)
# MAGIC - 4개 dimension table과 3개 fact table, 모든 table과 column에
# MAGIC   `COMMENT`가 포함됩니다 (Genie의 *inferred context* layer가 읽는 metadata)
# MAGIC - Informational `PRIMARY KEY` / `FOREIGN KEY` constraint 추가 (Unity Catalog constraint는
# MAGIC   informational이며 강제되지 않지만, Genie와 BI 도구가 join path를 자동 추론하는 데 사용됨)
# MAGIC - Synthetic data는 재현 가능한 *값*을 위해 seed 설정, 단 날짜 범위는
# MAGIC   오늘 기준 ~2년의 rolling window - 이후 날짜에 재실행하면 window가 앞으로 이동하고
# MAGIC   dim_date/fact/inventory가 해당 날짜까지 다시 생성됨
# MAGIC
# MAGIC 재실행해도 안전합니다: table은 `CREATE OR REPLACE`, constraint는 drop 후 재추가되며,
# MAGIC data load는 `insertInto(..., overwrite=True)`를 사용합니다.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.1 Catalog + Schema 생성

# COMMAND ----------

spark.sql(f"""
CREATE CATALOG IF NOT EXISTS {CATALOG}
COMMENT 'Genie One + Genie Ontology 데모 catalog (Northwind Retail sales analytics)'
""")

spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}
COMMENT '스타 스키마: 매출, 반품, 재고 현황 Fact 테이블 + 날짜/제품/고객/매장 Dimension'
""")

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2 Table 생성 (table 및 column 주석이 포함된 DDL)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.dim_date (
  date_key      INT     NOT NULL COMMENT '일자 Surrogate key, YYYYMMDD 정수',
  calendar_date DATE    NOT NULL COMMENT '달력 일자',
  year          INT              COMMENT '연도',
  quarter       INT              COMMENT '분기 (1-4)',
  month         INT              COMMENT '월 (1-12)',
  month_name    STRING           COMMENT '월 이름 (예: 1월)',
  day_of_week   STRING           COMMENT '요일 (예: 월요일)',
  is_weekend    BOOLEAN          COMMENT '토요일 또는 일요일이면 True'
)
COMMENT '일자 디멘전 - 달력 일자별 1행. 모든 fact table을 공통 calendar에 맞추는 데 사용.'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.dim_product (
  product_key  INT            NOT NULL COMMENT '상품 Surrogate key',
  sku          STRING         NOT NULL COMMENT 'Business key / 재고 관리 코드 (stock keeping unit)',
  product_name STRING                  COMMENT '제품 표시명',
  category     STRING                  COMMENT '상품 카테고리 (예: Electronics, Apparel)',
  brand        STRING                  COMMENT '브랜드명',
  unit_cost    DECIMAL(10,2)           COMMENT '도매 단가 (USD)'
)
COMMENT '상품 디멘전.'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.dim_customer (
  customer_key  INT    NOT NULL COMMENT '고객 Surrogate key',
  customer_name STRING          COMMENT '고객 표시명',
  segment       STRING          COMMENT '고객 segment: Consumer, Small Business 또는 Enterprise',
  region        STRING          COMMENT '고객이 속한 sales region',
  signup_date   DATE            COMMENT '고객 최초 가입일'
)
COMMENT '고객 디멘전.'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.dim_store (
  store_key  INT    NOT NULL COMMENT '상점/채널 Surrogate key',
  store_name STRING          COMMENT '상점 또는 채널 표시명',
  region     STRING          COMMENT '상점이 운영되는 지역',
  channel    STRING          COMMENT '채널: Online 또는 In-Store'
)
COMMENT '상점/채널 디멘전.'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.fact_sales (
  order_id     BIGINT        NOT NULL COMMENT '주문 surrogate key',
  date_key     INT           NOT NULL COMMENT 'dim_date.date_key로의 FK, 주문 일자',
  product_key  INT           NOT NULL COMMENT 'dim_product.product_key로의 FK',
  customer_key INT           NOT NULL COMMENT 'dim_customer.customer_key로의 FK',
  store_key    INT           NOT NULL COMMENT 'dim_store.store_key로의 FK',
  quantity     INT                    COMMENT '해당 주문건의 판매 수량',
  unit_price   DECIMAL(10,2)          COMMENT '실제 판매 단가 (USD)',
  revenue      DECIMAL(12,2)          COMMENT 'quantity * unit_price - 해당 주문건의 총매출액 (USD)'
)
COMMENT '판매 팩트 테이블 - 주문건(order line item)별 1행. Grain: order_id'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.fact_returns (
  return_id     BIGINT        NOT NULL COMMENT '반품건 surrogate key',
  order_id      BIGINT        NOT NULL COMMENT 'fact_sales.order_id로의 FK, 반품되는 원본 order line',
  date_key      INT           NOT NULL COMMENT 'dim_date.date_key로의 FK, 반품 일자',
  product_key   INT           NOT NULL COMMENT 'dim_product.product_key로의 FK',
  customer_key  INT           NOT NULL COMMENT 'dim_customer.customer_key로의 FK',
  quantity      INT                    COMMENT '반품 수량',
  return_amount DECIMAL(12,2)          COMMENT '환불 금액 (USD)',
  return_reason STRING                 COMMENT '반품 사유 코드 (예: Defective, Wrong Item)'
)
COMMENT '반품 팩트 테이블 - 반품된 주문건별 1행. Grain: return_id'
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ_SCHEMA}.fact_inventory (
  snapshot_date_key INT NOT NULL COMMENT 'dim_date.date_key로의 FK, inventory snapshot 일자 (매월 1일)',
  product_key       INT NOT NULL COMMENT 'dim_product.product_key로의 FK',
  store_key         INT NOT NULL COMMENT 'dim_store.store_key로의 FK',
  stock_on_hand     INT          COMMENT 'Snapshot 일자 기준 보유 재고 수량',
  stock_received    INT          COMMENT '이전 snapshot 이후 입고된 수량'
)
COMMENT '월별 재고 스냅샷 팩트 테이블. Grain: snapshot_date_key, product_key, store_key'
""")

print("테이블이 생성되었습니다.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.3 Primary Key Constraint
# MAGIC
# MAGIC Unity Catalog의 PK/FK constraint는 informational이며 (강제되지 않음),
# MAGIC Genie와 BI 도구가 유효한 join path를 추론하는 데 사용하므로 추가합니다.

# COMMAND ----------

pk_statements = [
    f"ALTER TABLE {FQ_SCHEMA}.dim_date     ADD CONSTRAINT pk_dim_date     PRIMARY KEY (date_key)",
    f"ALTER TABLE {FQ_SCHEMA}.dim_product  ADD CONSTRAINT pk_dim_product  PRIMARY KEY (product_key)",
    f"ALTER TABLE {FQ_SCHEMA}.dim_customer ADD CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key)",
    f"ALTER TABLE {FQ_SCHEMA}.dim_store    ADD CONSTRAINT pk_dim_store    PRIMARY KEY (store_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_sales   ADD CONSTRAINT pk_fact_sales   PRIMARY KEY (order_id)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_returns ADD CONSTRAINT pk_fact_returns PRIMARY KEY (return_id)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_inventory ADD CONSTRAINT pk_fact_inventory "
    f"PRIMARY KEY (snapshot_date_key, product_key, store_key)",
]

for stmt in pk_statements:
    try:
        spark.sql(stmt)
        print(f"OK   {stmt}")
    except Exception as e:
        # 재실행 시 이미 제약 조건이 존재하므로 무시해도 안전합니다.
        print(f"SKIP {stmt} -> {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.4 Foreign Key Constraint
# MAGIC
# MAGIC 모든 참조 대상 key가 먼저 존재하도록 PK 이후에 추가합니다
# MAGIC (`fact_returns.order_id`는 `fact_sales.order_id`를 참조하므로
# MAGIC `fact_sales`의 PK가 먼저 존재해야 합니다).

# COMMAND ----------

fk_statements = [
    f"ALTER TABLE {FQ_SCHEMA}.fact_sales ADD CONSTRAINT fk_sales_date "
    f"FOREIGN KEY (date_key) REFERENCES {FQ_SCHEMA}.dim_date (date_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_sales ADD CONSTRAINT fk_sales_product "
    f"FOREIGN KEY (product_key) REFERENCES {FQ_SCHEMA}.dim_product (product_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_sales ADD CONSTRAINT fk_sales_customer "
    f"FOREIGN KEY (customer_key) REFERENCES {FQ_SCHEMA}.dim_customer (customer_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_sales ADD CONSTRAINT fk_sales_store "
    f"FOREIGN KEY (store_key) REFERENCES {FQ_SCHEMA}.dim_store (store_key)",

    f"ALTER TABLE {FQ_SCHEMA}.fact_returns ADD CONSTRAINT fk_returns_order "
    f"FOREIGN KEY (order_id) REFERENCES {FQ_SCHEMA}.fact_sales (order_id)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_returns ADD CONSTRAINT fk_returns_date "
    f"FOREIGN KEY (date_key) REFERENCES {FQ_SCHEMA}.dim_date (date_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_returns ADD CONSTRAINT fk_returns_product "
    f"FOREIGN KEY (product_key) REFERENCES {FQ_SCHEMA}.dim_product (product_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_returns ADD CONSTRAINT fk_returns_customer "
    f"FOREIGN KEY (customer_key) REFERENCES {FQ_SCHEMA}.dim_customer (customer_key)",

    f"ALTER TABLE {FQ_SCHEMA}.fact_inventory ADD CONSTRAINT fk_inventory_date "
    f"FOREIGN KEY (snapshot_date_key) REFERENCES {FQ_SCHEMA}.dim_date (date_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_inventory ADD CONSTRAINT fk_inventory_product "
    f"FOREIGN KEY (product_key) REFERENCES {FQ_SCHEMA}.dim_product (product_key)",
    f"ALTER TABLE {FQ_SCHEMA}.fact_inventory ADD CONSTRAINT fk_inventory_store "
    f"FOREIGN KEY (store_key) REFERENCES {FQ_SCHEMA}.dim_store (store_key)",
]

for stmt in fk_statements:
    try:
        spark.sql(stmt)
        print(f"OK   {stmt}")
    except Exception as e:
        print(f"SKIP {stmt} -> {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.5 Synthetic Data 생성
# MAGIC
# MAGIC 다시 생성 가능한 재실행을 위해 seed를 설정한 pandas/numpy 기반 deterministic 생성입니다.
# MAGIC 일별 날짜 ~2년치, 제품 50건, 고객 200건, 상점 10건, 판매 5,000건, 
# MAGIC 그 중 반품건 ~8%, inventory snapshot 6개월치를 생성합니다.

# COMMAND ----------

import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

# ---- dim_date : 오늘 부터 시작해서 지난 2년치 ------------------
end_date = date.today()
start_date = end_date - timedelta(days=730)
n_days = (end_date - start_date).days + 1
all_dates = [start_date + timedelta(days=i) for i in range(n_days)]

pdf_date = pd.DataFrame({
    "date_key": [int(d.strftime("%Y%m%d")) for d in all_dates],
    "calendar_date": all_dates,
    "year": [d.year for d in all_dates],
    "quarter": [(d.month - 1) // 3 + 1 for d in all_dates],
    "month": [d.month for d in all_dates],
    "month_name": [f"{d.month}월" for d in all_dates],
    "day_of_week": [["월요일","화요일","수요일","목요일","금요일","토요일","일요일"][d.weekday()] for d in all_dates],
    "is_weekend": [d.weekday() >= 5 for d in all_dates],
})

# ---- dim_product -------------------------------------------------------------
categories = ["전자제품", "의류", "가정 및 주방용품", "스포츠", "뷰티"]
brands = ["삼송", "무슨사", "다이서", "어디다스", "리브영"]
n_products = 50

pdf_product = pd.DataFrame({
    "product_key": np.arange(1, n_products + 1),
    "sku": [f"SKU-{i:04d}" for i in range(1, n_products + 1)],
    "category": rng.choice(categories, n_products),
    "brand": rng.choice(brands, n_products),
    "unit_cost": np.round(rng.uniform(5, 500, n_products), 2),
})
pdf_product["product_name"] = (
    pdf_product["brand"] + " " + pdf_product["category"] + " " + pdf_product["sku"]
)
pdf_product = pdf_product[["product_key", "sku", "product_name", "category", "brand", "unit_cost"]]

# ---- dim_customer --------------------------------------------------------------
segments = ["소매상", "증소기업", "대기업"]
regions = ["북미", "유럽", "아시아", "중남미"]
n_customers = 200
signup_offsets = rng.integers(0, n_days, n_customers)

pdf_customer = pd.DataFrame({
    "customer_key": np.arange(1, n_customers + 1),
    "customer_name": [f"Customer {i:04d}" for i in range(1, n_customers + 1)],
    "segment": rng.choice(segments, n_customers, p=[0.6, 0.3, 0.1]),
    "region": rng.choice(regions, n_customers),
    "signup_date": [start_date + timedelta(days=int(o)) for o in signup_offsets],
})

# ---- dim_store -------------------------------------------------------------
channels = ["Online", "In-Store"]
n_stores = 10

pdf_store = pd.DataFrame({
    "store_key": np.arange(1, n_stores + 1),
    "store_name": [f"Store {i:02d}" for i in range(1, n_stores + 1)],
    "region": rng.choice(regions, n_stores),
    "channel": rng.choice(channels, n_stores, p=[0.5, 0.5]),
})

# ---- fact_sales -------------------------------------------------------------
n_sales = 5000
sales_date_idx = rng.integers(0, n_days, n_sales)
sales_product_idx = rng.integers(0, n_products, n_sales)
sales_customer_idx = rng.integers(0, n_customers, n_sales)
sales_store_idx = rng.integers(0, n_stores, n_sales)
quantity = rng.integers(1, 6, n_sales)
markup = rng.uniform(1.3, 2.0, n_sales)
unit_cost_arr = pdf_product["unit_cost"].to_numpy()[sales_product_idx]
unit_price = np.round(unit_cost_arr * markup, 2)
revenue = np.round(unit_price * quantity, 2)

pdf_sales = pd.DataFrame({
    "order_id": np.arange(1, n_sales + 1),
    "date_key": pdf_date["date_key"].to_numpy()[sales_date_idx],
    "product_key": pdf_product["product_key"].to_numpy()[sales_product_idx],
    "customer_key": pdf_customer["customer_key"].to_numpy()[sales_customer_idx],
    "store_key": pdf_store["store_key"].to_numpy()[sales_store_idx],
    "quantity": quantity,
    "unit_price": unit_price,
    "revenue": revenue,
})

# ---- fact_returns : ~8% of sales lines --------------------------------------
return_reasons = ["불량품", "잘못된 상품", "더 이상 필요 없음", "더 나은 가격을 찾았습니다", "배송 중 파손"]
n_returns = int(n_sales * 0.08)
returned = pdf_sales.sample(n=n_returns, random_state=42).reset_index(drop=True)
return_quantity = np.minimum(returned["quantity"].to_numpy(), rng.integers(1, 4, n_returns))

pdf_returns = pd.DataFrame({
    "return_id": np.arange(1, n_returns + 1),
    "order_id": returned["order_id"],
    "date_key": returned["date_key"],
    "product_key": returned["product_key"],
    "customer_key": returned["customer_key"],
    "quantity": return_quantity,
    "return_amount": np.round(return_quantity * returned["unit_price"].to_numpy(), 2),
    "return_reason": rng.choice(return_reasons, n_returns),
})

# ---- fact_inventory : 제품/매장별, 현재 월을 포함한 지난 6개월간의 월별 현황 ----
current_month_start = date(end_date.year, end_date.month, 1)
month_starts = pd.date_range(end=current_month_start, periods=6, freq="MS").date
inv_rows = [
    (int(md.strftime("%Y%m%d")), int(pk), int(sk))
    for md in month_starts
    for pk in pdf_product["product_key"]
    for sk in pdf_store["store_key"]
]
pdf_inventory = pd.DataFrame(inv_rows, columns=["snapshot_date_key", "product_key", "store_key"])
n_inv = len(pdf_inventory)
pdf_inventory["stock_on_hand"] = rng.integers(0, 500, n_inv)
pdf_inventory["stock_received"] = rng.integers(0, 200, n_inv)

print("Generated:",
      f"{len(pdf_date)} dates,", f"{len(pdf_product)} products,", f"{len(pdf_customer)} customers,",
      f"{len(pdf_store)} stores,", f"{len(pdf_sales)} sales lines,", f"{len(pdf_returns)} returns,",
      f"{len(pdf_inventory)} inventory snapshots")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.6 Delta Table에 로드
# MAGIC
# MAGIC `insertInto(..., overwrite=True)`를 사용합니다 (`saveAsTable` 대신) -
# MAGIC table 정의(comment 및 constraint)는 보존되고 data만 교체됩니다.

# COMMAND ----------

def load_table(pdf: "pd.DataFrame", table_name: str, column_types: dict):
    sdf = spark.createDataFrame(pdf)
    for col, dtype in column_types.items():
        sdf = sdf.withColumn(col, sdf[col].cast(dtype))
    sdf = sdf.select(*column_types.keys())
    sdf.write.insertInto(f"{FQ_SCHEMA}.{table_name}", overwrite=True)
    print(f"Loaded {sdf.count()} rows into {FQ_SCHEMA}.{table_name}")


load_table(pdf_date, "dim_date", {
    "date_key": "int", "calendar_date": "date", "year": "int", "quarter": "int",
    "month": "int", "month_name": "string", "day_of_week": "string", "is_weekend": "boolean",
})

load_table(pdf_product, "dim_product", {
    "product_key": "int", "sku": "string", "product_name": "string",
    "category": "string", "brand": "string", "unit_cost": "decimal(10,2)",
})

load_table(pdf_customer, "dim_customer", {
    "customer_key": "int", "customer_name": "string", "segment": "string",
    "region": "string", "signup_date": "date",
})

load_table(pdf_store, "dim_store", {
    "store_key": "int", "store_name": "string", "region": "string", "channel": "string",
})

load_table(pdf_sales, "fact_sales", {
    "order_id": "bigint", "date_key": "int", "product_key": "int", "customer_key": "int",
    "store_key": "int", "quantity": "int", "unit_price": "decimal(10,2)", "revenue": "decimal(12,2)",
})

load_table(pdf_returns, "fact_returns", {
    "return_id": "bigint", "order_id": "bigint", "date_key": "int", "product_key": "int",
    "customer_key": "int", "quantity": "int", "return_amount": "decimal(12,2)", "return_reason": "string",
})

load_table(pdf_inventory, "fact_inventory", {
    "snapshot_date_key": "int", "product_key": "int", "store_key": "int",
    "stock_on_hand": "int", "stock_received": "int",
})

print("\nDone. Next: run 02_create_metric_views.")