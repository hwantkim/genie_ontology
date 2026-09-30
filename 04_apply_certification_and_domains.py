# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 04 - 모든 테이블 및 metric view에 인증 및 도메인 태그 적용
# MAGIC
# MAGIC 이 노트북은 수동으로 하나씩 클릭해 설정할 필요 없이, SQL을 통해 모든 테이블과 메트릭 뷰에 다음 두 가지를 일괄 적용합니다.
# MAGIC - `system.certification_status = certified`
# MAGIC - 자산이 속한 각 도메인의 거버넌스 태그
# MAGIC
# MAGIC 이 작업은 멱등성(idempotent)을 가집니다. 즉, 코드를 다시 실행해도 동일한 태그가 그대로 다시 설정될 뿐입니다.
# MAGIC
# MAGIC ## 도메인 태그가 작동하는 방식
# MAGIC
# MAGIC Catalog Explorer의 Discover -> Domains에서 `Sales`라는 이름으로 도메인을 생성하면, **키가 해당 도메인 이름과 정확히 일치하고 값은 비어 있는** 거버넌스 태그로 매핑됩니다(domain_sales = true 같은 임의의 키가 생성되는 것이 아닙니다). UI에서 자산을 도메인에 수동으로 할당한 후 `<catalog>.information_schema.table_tags`를 조회하면 `tag_name='Sales', tag_value=''`와 같은 행이 나타납니다. 태그 권한이 있는 사용자라면 도메인 UI를 통해 미리 만들지 않고도 이름만으로 태그를 지정할 수 있으므로, 이 노트북은 아래의 도메인 이름을 사용하여 `SET TAG ON TABLE/VIEW ... `<도메인 이름>``을 통해 도메인 태그를 직접 적용합니다. 따라서 4개의 도메인을 정확히 이 이름들로 생성해 두었다면, 일일이 도메인을 열어 태그 키를 복사할 필요가 없습니다.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# Catalog Explorer -> Discover -> Domains에서 아래 이름으로 먼저 도메인을 4개 생성합니다.
# 도메인의 이름 그 자체로 도메인 거버넌스 tag가 생성됩니다 (key-only, 값 없음).
DOMAIN_NAMES = ["Sales", "Customer", "Supply Chain", "Finance"]

# 각 테이블 / metric view가 속한 도메인. 자산은 둘 이상의 도메인을 가질 수 있습니다.
ASSET_DOMAINS = {
    "dim_product":            ["Sales"],
    "dim_store":               ["Sales", "Supply Chain"],
    "dim_customer":            ["Customer"],
    "dim_date":                [],  # 공유 conformed dimension, 단일 도메인 없음
    "fact_sales":               ["Sales", "Finance"],
    "fact_returns":              ["Customer"],
    "fact_inventory":            ["Supply Chain"],
    "mv_sales_performance":      ["Sales", "Finance"],
    "mv_customer_returns":       ["Customer"],
    "mv_inventory_health":       ["Supply Chain"],
}

METRIC_VIEWS = {"mv_sales_performance", "mv_customer_returns", "mv_inventory_health"}

# COMMAND ----------

def object_kind(asset_name: str) -> str:
    return "VIEW" if asset_name in METRIC_VIEWS else "TABLE"


def run(stmt: str):
    try:
        spark.sql(stmt)
        print(f"OK    {stmt}")
    except Exception as e:
        print(f"ERROR {stmt} -> {e}")


def set_tags(asset_name: str, domains: list):
    kind = object_kind(asset_name)
    fq_asset = f"{FQ_SCHEMA}.{asset_name}"

    # 인증 (변경 없음, key=value tag) - 이미 동작 확인됨.
    run(f"ALTER {kind} {fq_asset} SET TAGS ('system.certification_status' = 'certified')")

    # 도메인 governed tags: key-only, 키 == 도메인 이름과 정확히 일치.
    for domain in DOMAIN_NAMES:
        stmt = f"{'SET' if domain in domains else 'UNSET'} TAG ON {kind} {fq_asset} `{domain}`"
        run(stmt)


for asset_name, domains in ASSET_DOMAINS.items():
    set_tags(asset_name, domains)

print("\n완료. Catalog Explorer에서 태그를 확인하세요: 각 자산에 'certified'")
print("배지가 표시되고, Discover 페이지의 해당 도메인 아래에 나타나야 합니다.")
print("참고: Genie Agent 자체는 여전히 UI에서 수동으로 인증 + 도메인 할당을")
print("해야 합니다 (SQL 타겟이 없음).")