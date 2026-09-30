# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 00 - 공통 설정
# MAGIC
# MAGIC 이 폴더의 모든 다른 노트북은 `%run ./00_config`로 시작하여 아래의 catalog/schema 이름을
# MAGIC 가져옵니다. 여기서 widget 기본값을 한 번만 변경하면 (또는 실행 시 widget 바에서 재정의하면)
# MAGIC 모든 노트북에 동일하게 적용됩니다.
# MAGIC
# MAGIC **Genie One + Genie Ontology demo**의 일부입니다. 전체 계획은 repo 루트의
# MAGIC `README.md`를 참고하세요.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "genie_ontology_demo", "카탈로그 이름")
dbutils.widgets.text("schema_name", "retail_demo", "스키마 이름")

CATALOG = dbutils.widgets.get("catalog_name")
SCHEMA = dbutils.widgets.get("schema_name")
FQ_SCHEMA = f"{CATALOG}.{SCHEMA}"

print(f"CATALOG    = {CATALOG}")
print(f"SCHEMA     = {SCHEMA}")
print(f"FQ_SCHEMA  = {FQ_SCHEMA}")