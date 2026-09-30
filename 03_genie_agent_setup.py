# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Genie Agent 설정 (수동, 참고용)
# MAGIC
# MAGIC 이 노트북은 아무것도 생성하지 않습니다 - Genie Agent 생성은 UI에서 진행합니다. 아래
# MAGIC 텍스트를 Genie One "Create Agent" 폼에 복사하여 붙여넣으세요.
# MAGIC
# MAGIC ## Name
# MAGIC ```
# MAGIC 소매 분석 지니
# MAGIC ```
# MAGIC
# MAGIC ## Description
# MAGIC ```
# MAGIC Northwind Retail의 매출 실적, 고객 반품, 재고 건전성에 대한 자연어 질문에
# MAGIC 답변합니다. 인증된 metric view를 사용하여 매출, 판매 수량, 주문 수, 평균 주문
# MAGIC 금액, 반품 및 반품 수량, 보유 재고를 다양한 기준(날짜, 제품 카테고리/브랜드,
# MAGIC 고객 세그먼트/지역, 매장 지역/채널)으로 분석합니다.
# MAGIC ```
# MAGIC
# MAGIC ## 연결할 데이터 소스
# MAGIC 다음 세 가지 metric view를 Agent의 테이블/데이터 소스로 추가하세요
# MAGIC (`02_create_metric_views`에서 생성됨):
# MAGIC - `mv_sales_performance`
# MAGIC - `mv_customer_returns`
# MAGIC - `mv_inventory_health`
# MAGIC
# MAGIC 원본 팩트/차원 테이블은 **직접 연결하지 마세요** - 이 데모의 핵심은 Genie가
# MAGIC 임의 조인(ad hoc joins) 대신 거버넌스가 적용된 metric view를 우선 선택하는
# MAGIC 것을 보여주는 것입니다.
# MAGIC
# MAGIC ## Custom instructions (Agent 수준, workspace 수준이 아님)
# MAGIC ```
# MAGIC 당신은 Northwind Retail의 소매 분석 어시스턴트입니다.
# MAGIC
# MAGIC - 원본 테이블을 직접 조회하기보다 metric view(mv_sales_performance,
# MAGIC   mv_customer_returns, mv_inventory_health)를 항상 우선 사용하세요.
# MAGIC - "수익" 또는 "메출"은 mv_sales_performance의 total_revenue 측정값을
# MAGIC   의미하며, 정가(list price)나 단가(unit cost)가 아닙니다.
# MAGIC - "반품률"는 저장된 측정값이 아닙니다 - 동일한 기간과 차원 슬라이스에
# MAGIC   대해 mv_customer_returns.return_amount / mv_sales_performance.total_revenue로
# MAGIC   계산하고, 그렇게 했음을 명시하세요.
# MAGIC - 모든 금액은 USD 기준입니다.
# MAGIC - 질문에서 시간 범위가 모호한 경우, 최근 12개월을 기본으로 사용하고
# MAGIC   적용한 범위를 명시하세요.
# MAGIC ```
# MAGIC
# MAGIC ## Agent 설정 화면에 추가할 샘플 / 벤치마크 질문
# MAGIC - 직전 분기의 총 매출은 제품 카테고리별로 각각 얼마인가요?
# MAGIC - 올해 대비 작년 고객 반품률은 어떻게 되나요?
# MAGIC - 매출이 가장 높으면서 반품도가 높은 지역은 어디인가요?
# MAGIC - 고객 세그먼트별 평균 주문 금액은 얼마인가요?
# MAGIC - 평균 재고 보유량이 가장 낮은 제품은 무엇인가요?
# MAGIC
# MAGIC ## Agent 생성 후
# MAGIC 1. 인증하기: Agent의 케밥 메뉴 -> **인증 할당** -> 인증됨.
# MAGIC 2. **Sales** 도메인에 할당 (4단계에서 수동으로 생성).
# MAGIC 3. 나머지 작업(테이블 + metric view)을 위해 `04_apply_certification_and_domains`을
# MAGIC    실행하세요 - 수동으로 인증/태그한 metric view를 다시 인증/태그해도
# MAGIC    안전합니다. 스크립트는 멱등성(idempotent)을 가지고 동작합니다.