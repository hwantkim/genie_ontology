# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 02 - 메트릭 뷰 생성
# MAGIC
# MAGIC `01_create_catalog_schema_tables`에서 생성한 스타 스키마를 기반으로 3개의 Unity Catalog 메트릭 뷰를 생성합니다:
# MAGIC
# MAGIC | 메트릭 뷰 | 팩트 원본 | 조인된 차원 |
# MAGIC |---|---|---|
# MAGIC | `mv_판매_실적` | `fact_sales` | `dim_date`, `dim_product`, `dim_customer`, `dim_store` |
# MAGIC | `mv_customer_returns` | `fact_returns` | `dim_date`, `dim_product`, `dim_customer` |
# MAGIC | `mv_inventory_health` | `fact_inventory` | `dim_date`, `dim_product`, `dim_store` |
# MAGIC
# MAGIC 각 차원(Dimension)과 측정값(Measure)은 Genie One의 모델링 컨텍스트 레이어가 읽어들이는 "에이전트 메타데이터"를 포함합니다: `display_name`, `description`, `synonyms`, 그리고 (숫자 측정값의 경우) 통화나 백분율 같은 `format` 힌트입니다.
# MAGIC
# MAGIC **정확성에 대 참고:** `display_name` / `description` / `synonyms`는 안정적이며 문서화된 메트릭 뷰 메타데이터 필드입니다. `format` 블록의 정확한 키는 Databricks 릴리스별로 변경된 바 있습니다 - `CREATE VIEW`가 `format:` 라인에서 실패할 경우, 해당 라인을 삭제한 후 재실행하고, 이후 Catalog Explorer의 메트릭 뷰 YAML 에디터에서 포맷을 추가하세요 (현재 워크스페이스의 스키마 버전에 맞춘 자동완성/검증 기능을 제공합니다).
# MAGIC
# MAGIC 교차 팩트(Cross-fact) 메트릭(예: "반품률" = 반품 / 매출)은 여기서 **의도적으로** 측정값으로 정의하지 않았습니다 - 메트릭 뷰의 측정값은 자체 소스와 조인된 차원만 집계할 수 있으며, 다른 팩트 테이블은 집계할 수 없습니다. 그럼에도 Genie One은 `mv_sales_performance`와 `mv_customer_returns`를 모두 조회하고 결합하여 "우리의 반품률은 어떻게 되나요"와 같은 교차 메트릭 뷰 질문에 답할 수 있습니다; "총 수익" 및 "고객 반품률" 페이지(`05_pages_content` 참조)에서 해당 공식을 명시적으로 문서화하여 Genie가 인용할 수 있는 신뢰할 수 있는 정의를 제공합니다.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.1 `mv_sales_performance`

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {FQ_SCHEMA}.mv_sales_performance
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1

source: {FQ_SCHEMA}.fact_sales

joins:
  - name: date
    source: {FQ_SCHEMA}.dim_date
    on: source.date_key = date.date_key
  - name: product
    source: {FQ_SCHEMA}.dim_product
    on: source.product_key = product.product_key
  - name: customer
    source: {FQ_SCHEMA}.dim_customer
    on: source.customer_key = customer.customer_key
  - name: store
    source: {FQ_SCHEMA}.dim_store
    on: source.store_key = store.store_key

dimensions:
  - name: order_date
    expr: date.calendar_date
    display_name: "주문 일자"
    synonyms: ["판매일", "구매일"]
  - name: year
    expr: date.year
    display_name: "연도"
    synonyms: ["년", "년도"]
  - name: quarter
    expr: date.quarter
    display_name: "분기"
    synonyms: ["회계 분기", "Q"]
  - name: month_name
    expr: date.month_name
    display_name: "월"
    synonyms: ["월별"]
  - name: product_category
    expr: product.category
    display_name: "상품 카테고리"
    synonyms: ["카테고리", "상품 분류"]
  - name: product_brand
    expr: product.brand
    display_name: "브랜드"
    synonyms: ["제품 브랜드", "제조사"]
  - name: customer_segment
    expr: customer.segment
    display_name: "고객 세그먼트"
    synonyms: ["세그먼트", "고객 유형"]
  - name: customer_region
    expr: customer.region
    display_name: "고객 지역"
    synonyms: ["고객 거주 지역"]
  - name: store_region
    expr: store.region
    display_name: "매장 지역"
    synonyms: ["지역", "영업 지역"]
  - name: sales_channel
    expr: store.channel
    display_name: "판매 채널"
    synonyms: ["채널", "온라인 vs 오프라인"]

measures:
  - name: total_revenue
    expr: SUM(source.revenue)
    display_name: "총 매출"
    comment: "모든 주문 건의 총 매출(수량 × 단가) 합계"
    synonyms: ["매출", "판매", "총 판매", "총 거래액", "총 판매액"]
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
  - name: total_units_sold
    expr: SUM(source.quantity)
    display_name: "총 판매 수량"
    comment: "모든 주문 건의 판매 수량 합계"
    synonyms: ["판매 수량", "판매량", "판매 물량"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: order_count
    expr: COUNT(DISTINCT source.order_id)
    display_name: "주문 건수"
    comment: "고유 주문 라인 수"
    synonyms: ["주문 수", "주문", "주문 물량"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: avg_order_value
    expr: SUM(source.revenue) / COUNT(DISTINCT source.order_id)
    display_name: "평균 주문 금액"
    comment: "총 매출을 주문 수로 나눈 값"
    synonyms: ["객단가", "평균 주문 규모", "평균 금액"]
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
$$
""")

print(f"{FQ_SCHEMA}.mv_sales_performance 생성됨")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.2 `mv_customer_returns`

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {FQ_SCHEMA}.mv_customer_returns
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1

source: {FQ_SCHEMA}.fact_returns

joins:
  - name: date
    source: {FQ_SCHEMA}.dim_date
    on: source.date_key = date.date_key
  - name: product
    source: {FQ_SCHEMA}.dim_product
    on: source.product_key = product.product_key
  - name: customer
    source: {FQ_SCHEMA}.dim_customer
    on: source.customer_key = customer.customer_key

dimensions:
  - name: return_date
    expr: date.calendar_date
    display_name: "반품 일자"
    synonyms: ["반품일"]
  - name: year
    expr: date.year
    display_name: "연도"
    synonyms: ["년", "년도"]
  - name: quarter
    expr: date.quarter
    display_name: "분기"
    synonyms: ["회계 분기"]
  - name: product_category
    expr: product.category
    display_name: "상품 카테고리"
    synonyms: ["카테고리"]
  - name: return_reason
    expr: source.return_reason
    display_name: "반품 사유"
    synonyms: ["사유", "사유 코드", "반품 이유"]
  - name: customer_segment
    expr: customer.segment
    display_name: "고객 세그먼트"
    synonyms: ["세그먼트", "고객 유형"]

measures:
  - name: return_count
    expr: COUNT(DISTINCT source.return_id)
    display_name: "반품 건수"
    comment: "고유 반품 건 수"
    synonyms: ["반품 수", "반품"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: units_returned
    expr: SUM(source.quantity)
    display_name: "반품 수량"
    comment: "모든 반품 건의 반품 수량 합계"
    synonyms: ["반품 수량", "반품 물량"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: return_amount
    expr: SUM(source.return_amount)
    display_name: "반품 금액"
    comment: "모든 반품 건의 환불 금액 합계"
    synonyms: ["환불액", "환불 금액", "반품 가액"]
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
$$
""")

print(f"{FQ_SCHEMA}.mv_customer_returns 생성됨")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2.3 `mv_inventory_health` (optional third metric view)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {FQ_SCHEMA}.mv_inventory_health
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1

source: {FQ_SCHEMA}.fact_inventory

joins:
  - name: date
    source: {FQ_SCHEMA}.dim_date
    on: source.snapshot_date_key = date.date_key
  - name: product
    source: {FQ_SCHEMA}.dim_product
    on: source.product_key = product.product_key
  - name: store
    source: {FQ_SCHEMA}.dim_store
    on: source.store_key = store.store_key

dimensions:
  - name: snapshot_date
    expr: date.calendar_date
    display_name: "재고 기준일"
    synonyms: ["재고 일자", "기준일"]
  - name: month_name
    expr: date.month_name
    display_name: "월"
    synonyms: ["월별"]
  - name: product_category
    expr: product.category
    display_name: "상품 카테고리"
    synonyms: ["카테고리"]
  - name: store_region
    expr: store.region
    display_name: "매장 지역"
    synonyms: ["지역"]

measures:
  - name: avg_stock_on_hand
    expr: AVG(source.stock_on_hand)
    display_name: "평균 재고 수량"
    comment: "조회 범위 내 스냅샷의 평균 보유 수량"
    synonyms: ["평균 재고", "평균 재고 수준", "보유 재고"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: total_units_received
    expr: SUM(source.stock_received)
    display_name: "총 입고 수량"
    comment: "조회 범위 내 스냅샷의 입고 수량 합계"
    synonyms: ["입고 수량", "입고 물량"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
  - name: low_stock_snapshot_count
    expr: SUM(CASE WHEN source.stock_on_hand < 50 THEN 1 ELSE 0 END)
    display_name: "부족 재고 스냅샷 건수"
    comment: "보유 수량이 50개 미만인 상품/매장/월 스냅샷 건수"
    synonyms: ["저재고 건수", "품절 임박 건수"]
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
$$
""")

print(f"{FQ_SCHEMA}.mv_inventory_health 생성됨")
print("\n완료되었습니다. 카탈로그 탐색기에서 생성된 매트릭 뷰 3개를 모두 확인한 후 3단계(Genie Agent, 수직업 실행)를 진행하여 주십시오.")