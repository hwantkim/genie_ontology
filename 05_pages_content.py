# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - 페이지 내용 (직접 생성시 참고용)
# MAGIC
# MAGIC 이 노트북은 무언가를 생성하지는 않습니다 - 페이지는 Catalog Explorer ->
# MAGIC Discover -> 만들기 -> 페이지생성 에서 작성합니다. 아래의 각 블록을 복사하여 새 페이지 정의에 사용합니다. 아래 필드는
# MAGIC UI의 실제 페이지 생성의 요소들에 맞추어 구성되어 있습니다.
# MAGIC
# MAGIC 도메인 (단일 선택) / 이름 / 소유자 / 동의어 / 설명 / 본문 (정의 + 업무용) / 관련 자산 / 소스 (선택 사항).
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Page 1: 총 매출
# MAGIC
# MAGIC | 필드 | 값 |
# MAGIC |---|---|
# MAGIC | 도메인 | Finance |
# MAGIC | 이름 | 총 매출 |
# MAGIC | 소유자 | 본인 (xxxx@gmail.com) |
# MAGIC | 동의어 | 매출, 판매, 총 판매, 총 거래액, 총 판매액 |
# MAGIC
# MAGIC **설명:**
# MAGIC ```
# MAGIC 모든 주문 건의 총 매출(수량 x 단가) 합계이며, 반품 및 할인 내역은 반영하지 않습니다.
# MAGIC ```
# MAGIC
# MAGIC **본문:**
# MAGIC ```
# MAGIC 정의
# MAGIC
# MAGIC 총 매출은 fact_sales의 모든 주문 건에 대한 총 매출(수량 x 단가)의
# MAGIC 합계이며, 반품 및 할인 내역은 반영하지 않습니다.
# MAGIC
# MAGIC 공식: SUM(fact_sales.revenue)
# MAGIC
# MAGIC 업무용
# MAGIC
# MAGIC @fact_sales를 직접 쿼리하지 말고 @mv_sales_performance의 total_revenue 측정값을 사용하세요.
# MAGIC 해당 값은 인증된 정의와 사전 구축된 차원 조인(날짜, 제품, 고객, 매장)을 포함하고 있습니다.
# MAGIC ```
# MAGIC
# MAGIC **관련 자산:** `mv_sales_performance`, `fact_sales`, `소매 분석 지니`
# MAGIC
# MAGIC **소스 (선택 사항):** 없음 - 콘텐츠를 이 페이지에 직접 작성함.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 페이지 2: 고객 반품률
# MAGIC
# MAGIC | 필드 | 값 |
# MAGIC |---|---|
# MAGIC | 도메인 | Customer |
# MAGIC | 이름 | 고객 반품률 |
# MAGIC | 소유자 | 본인 (xxxx@gmail.com) |
# MAGIC | 동의어 | 반품률, 반품비율 |
# MAGIC
# MAGIC **설명:**
# MAGIC ```
# MAGIC 환불된 매출 비중: 동일한 기간 및 차원 슬라이스의 총 매출액으로 총 반품 금액을 나눈 값입니다.
# MAGIC ```
# MAGIC
# MAGIC **본문:**
# MAGIC ```
# MAGIC 정의
# MAGIC
# MAGIC 고객 반품률(Customer Return Rate)은 전체 매출 중 환불된 금액의 비중을 측정합니다.
# MAGIC
# MAGIC 공식: SUM(fact_returns.return_amount) / SUM(fact_sales.revenue)
# MAGIC (동일한 기간 및 차원 슬라이스 기준)
# MAGIC
# MAGIC 본 지표는 서로 다른 팩트 테이블을 결합하는 크로스 팩트(Cross-fact) 지표이므로 단일 저장된 측정값으로 존재하지 않습니다. 
# MAGIC 비교하려는 기간에 대해 @mv_customer_returns의 return_amount 측정값과 @mv_sales_performance의 total_revenue 측정값을 조합하여 산출해야 합니다.
# MAGIC
# MAGIC 업무용
# MAGIC
# MAGIC 누군가 반품률에 대해 문의할 경우 이 페이지를 공인된 산식의 기준으로 활용하세요. 
# MAGIC 지니(Genie)는 단일 지표 뷰만으로는 이러한 크로스 팩트 비율을 자체적으로 도출할 수 없습니다.
# MAGIC ```
# MAGIC
# MAGIC **관련 자산:** `mv_customer_returns`, `mv_sales_performance`, `fact_returns`, `소매 분석 지니`
# MAGIC
# MAGIC **소스 (선택 사항):** 없음 - 본 페이지에서 직접 작성된 콘텐츠입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 페이지 3: 소매 분석 지니 에이전트
# MAGIC
# MAGIC | 필드 | 값 |
# MAGIC |---|---|
# MAGIC | 도메인 | Sales |
# MAGIC | 이름 | 소매 분석 지니 에이전트 |
# MAGIC | 소유자 | 본인 (xxxx@gmail.com) |
# MAGIC | 동의어 | 소매 지니, 판매 지니, 소매 분석 도우미 |
# MAGIC
# MAGIC **설명:**
# MAGIC ```
# MAGIC 노스윈드 리테일(Northwind Retail) 분석 지니 에이전트 온보딩 페이지입니다. 
# MAGIC 어떤 질문에 답할 수 있는지, 어떤 인증된 메트릭 뷰(certified metric views)를 기반으로 하는지 설명합니다.
# MAGIC ```
# MAGIC
# MAGIC **본문:**
# MAGIC ```
# MAGIC 정의
# MAGIC
# MAGIC @소매 분석 지니는 노스윈드 리테일의 매출, 반품, 재고 관련 문의를 처리하는 지니 에이전트입니다. 
# MAGIC @mv_sales_performance, @mv_customer_returns, @mv_inventory_health 등 
# MAGIC 세 가지 인증된 메트릭 뷰를 기반으로 답변을 제공합니다. 
# MAGIC
# MAGIC 업무용
# MAGIC
# MAGIC 다음과 같이 질문해 보세요:
# MAGIC - "지난 분기 제품 카테고리별 총매출은 얼마였나요?"
# MAGIC - "올해와 작년의 고객 반품률을 비교해 주세요."
# MAGIC - "매출이 가장 높으면서 동시에 반품률도 높은 지역은 어디인가요?"
# MAGIC - "평균 보유 재고가 가장 낮은 제품은 무엇인가요?"
# MAGIC
# MAGIC ```
# MAGIC
# MAGIC **관련 자산:** `소매 분석 지니`, `mv_sales_performance`, `mv_customer_returns`, `mv_inventory_health`, `총 매출`, `고객 반품률`
# MAGIC
# MAGIC **소스 (선택 사항):** 없음 - 본 페이지에서 직접 작성된 콘텐츠입니다.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 참고 사항
# MAGIC - 페이지의 **도메인** 필드는 UI에서 단일 선택입니다 (반대로 테이블/뷰의 도메인 태깅은 여러 개를 선택할 수 있음)위의 각 페이지에는 정확히 하나의 도메인만 나열되어 있습니다. 해당 정의를 찾기 위해 탐색할 때 가장 잘 맞는 도메인을 선택하세요.
# MAGIC - **설명**은 페이지 목록/검색에 표시되는 짧은 한 줄 요약입니다;
# MAGIC   **본문**는 전체 리치 텍스트 콘텐츠이며, 여기서는 "정의"와 업무용" 제목으로 각각 구조화되어 있습니다. 에디터의 제목/문단 서식으로 해당 구조를 재현하세요.
# MAGIC - 에디터의 `@` 멘션을 사용하여 각 관련 자산을 링크하고 다른 두 페이지를 상호 링크하세요. 이렇게 하면 "관련 자산"으로 표시되며 Genie One이 페이지 사이를 탐색할 수 있습니다.
# MAGIC - 페이지 3개를 모두 게시하세요 (게시되지 않은 페이지는 게시된 페이지보다 Genie 순위에서 우선순위가 낮습니다).