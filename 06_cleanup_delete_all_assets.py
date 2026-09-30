# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# DBTITLE 1,06 - 정리: SQL 계층 데모 자산 삭제
# MAGIC %md
# MAGIC # 06 - 정리: SQL 계층 데모 자산 삭제
# MAGIC
# MAGIC 데모 카탈로그를 삭제합니다 (스키마, 모든 테이블, 모든 metric views까지 연쇄 삭제됨).
# MAGIC 이후 처음부터 다시 시작하려면 `01_create_catalog_schema_tables`와
# MAGIC `02_create_metric_views`를 새로 실행하면 됩니다.
# MAGIC
# MAGIC **UI에서 수동으로 생성한 항목은 삭제되지 않습니다** - 이 오브젝트 유형에 대한
# MAGIC 공개 API가 확인되지 않았으므로, 다음 데모 실행 전에 완전히 초기화하려면
# MAGIC 수동으로 제거해야 합니다:
# MAGIC - **Genie Agent** (`소매 분석 지니`)
# MAGIC - **4개 도메인** (Catalog Explorer -> Discover -> 도메인) - 또는 그대로 두어도 됩니다.
# MAGIC   거버넌스 태그이므로 다음 실행에서 재사용할 수 있습니다
# MAGIC - **3개 페이지** (Catalog Explorer -> Discover -> 페이지)
# MAGIC
# MAGIC ## 주의
# MAGIC 이 작업은 되돌릴 수 없습니다. 아래 셀을 실행하기 전에 `confirm` 위젯에 `DELETE`를
# MAGIC 입력하세요 - 다른 값을 입력하면 중단됩니다.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

dbutils.widgets.text("confirm", "", "삭제하려면 'DELETE' 입력")
confirm = dbutils.widgets.get("confirm")

if confirm != "DELETE":
    print(f"중단됨: confirm 위젯 값이 '{confirm}'입니다. 'DELETE' 입력이 필요합니다. 아무것도 삭제되지 않았습니다.")
else:
    spark.sql(f"DROP CATALOG IF EXISTS {CATALOG} CASCADE")
    print(f"카탈로그 {CATALOG}가 삭제되었습니다.(스키마, 테이블, metric views가 모두 제거됨)")
    print("알림: 지니 에이전트, 도메인, 페이지는 필요한 경우 수동으로 정리해야 합니다.")