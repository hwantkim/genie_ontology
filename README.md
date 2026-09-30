# Genie 온톨로지 - Genie One 답변의 신뢰성 향상
이 리포지토리는 소규모 스타 스키마 형태의 리테일 데이터셋을 바탕으로, Genie 온톨로지(Unity Catalog 시맨틱: 메트릭 뷰, 도메인, 페이지, 인증)를 모델링하여 적용해 보고, 최종적으로 Databricks Genie One에서 실습 중심 데모를 진행하는데 사용되는 노트북들로 이루어져 있습니다.

이를 통하여 여러분은 독립형 "Northwind Retail" 매출 및 고객 분석 유스케이스를 구축한 뒤, Genie One을 해당 데이터셋에 연동하여 인증된 메트릭 뷰, 도메인, 페이지를 사용하여 Genie 답변의 품질과 추적 가능성을 어떻게 변화시키는지 질문별로 직접 확인할 수 있을 것입니다.

## 구성 요소 설명

- **Genie One** 은 ChatGPT 나 Gemini Web App과 유사한 방식의 Databricks의 자연어 채팅 UI 서비스 입니다. 질문을 받으면 다음 순서로 검색합니다. (1) 기존 **Genie Agents**, (2) dashboards/queries/metric views — 그리고 **Genie Ontology**를 활용하여 답변합니다.
  - *모델링된 컨텍스트* — metric views, domains, pages — 사람이 선별하고
    인증한 항목 (이 데모에서 구축하는 부분).
  - *추론된 컨텍스트* — 메타데이터, 사용량, 최신성 — 기존 자산에서 자동으로
    수집됩니다.
  - 모든 답변 스니펫에는 신뢰도 점수(권한, 사용량, 최신성)가 부여되며, 질문한 사용자가 볼 수 있는 권한이 있는 범위 내에서만 응답이 제공됩니다.
- **메트릭 뷰(Metric Views)** 는 측정값(매출, 주문 건수 등)을 차원과 분리하여 한 번만 정의하며, SQL, 노트북, 대시보드, Genie에서 테이블처럼 쿼리할 수 있습니다.
- **도메인(Domains)** 은 거버넌스가 적용된 태그를 기반으로 하는 탐색 계층입니다 — 자산에
  도메인 태그가 지정되면 Discover 페이지에서 비즈니스 목적별로 그룹화되어
  표시됩니다.
- **페이지(Pages)** 는 비즈니스 용어, KPI, 개념에 대한 거버넌스가 적용된 정의로, 관련 자산 링크와 리치 텍스트 본문을 포함합니다. Genie One은 게시된 페이지를 추론된 컨텍스트보다 우선하는 권한 있는 컨텍스트로 읽어들입니다.
- **인증(Certification)**(`인증됨` / `사용 중단됨`)은 카탈로그, 스키마, 테이블, 뷰, 볼륨, 함수, 모델, 대시보드, Genie 에이전트, 앱, 노트북에 적용할 수 있습니다(인증됨 / 지원 중단됨). 인증된 자산은 Genie One의 답변에서 더 높은 순위로 노출됩니다.

참고 문서: [Genie One chat](https://learn.microsoft.com/ko-kr/azure/databricks/genie-one/chat) ·
[UC semantics overview](https://learn.microsoft.com/ko-kr/azure/databricks/uc-semantics/) ·
[Metric views](https://learn.microsoft.com/ko-kr/azure/databricks/uc-semantics/metric-views/) ·
[Domains](https://docs.databricks.com/aws/en/uc-semantics/domains) ·
[Pages](https://learn.microsoft.com/ko-kr/azure/databricks/uc-semantics/pages) ·
[Certify/deprecate](https://learn.microsoft.com/ko-kr/azure/databricks/data-governance/unity-catalog/certify-deprecate-data)

## 사전 요구 사항

- Unity Catalog가 활성화되어 있고 SQL 웨어하우스(서버리스 가능)가 있는 Databricks 워크스페이스.
- 해당 워크스페이스 내에서 카탈로그/스키마 생성, 메트릭 뷰 생성, Genie One / Genie 에이전트 사용 권한.
- 로컬 설정 불필요 — 모든 기능이 워크스페이스 내부의 Databricks 노트북으로 실행됩니다. 이 폴더를 Workspace/Repo 폴더로 가져온 후 노트북을 열기만 하면 됩니다.

## 저장소 구성

| 파일 | 설명 | 실행 방법 |
|---|---|---|
| [`00_config.py`](00_config.py) | catalog/schema 이름을 위한 widgets, 모든 노트북이 `%run`으로 공유 | 직접 실행하지 않음 |
| [`01_create_catalog_schema_tables.py`](01_create_catalog_schema_tables.py) | catalog, schema, 7개 테이블 생성(코멘트 + PK/FK 제약조건 포함); 최근 약 2년치 합성 데이터 생성 및 로드 | **Databricks에서 실행** |
| [`02_create_metric_views.py`](02_create_metric_views.py) | 완전한 시맨틱 메타데이터(표시 이름, 동의어, 형식)를 포함하는 3개의 메트릭 뷰 생성 | **Databricks에서 실행** |
| [`03_genie_agent_setup.py`](03_genie_agent_setup.py) | Genie One "에이전트 만들기" UI에 붙여넣을 이름/설명/지침/샘플 질문 (참조 전용) | 읽기 전용, 실행하지 않음 |
| [`04_apply_certification_and_domains.py`](04_apply_certification_and_domains.py) | SQL `SET TAG`/`SET TAGS`를 통해 모든 테이블과 메트릭 뷰에 인증 및 도메인 태그 적용 | **Databricks에서 실행** |
| [`05_pages_content.py`](05_pages_content.py) | 3개의 페이지 콘텐츠(이름/소유자/도메인/동의어/설명/본문/관련 자산/출처) (페이지 생성 UI 폼 필드와 정확히 일치, 참조 전용) | 읽기 전용, 실행하지 않음 |
| [`06_cleanup_delete_all_assets.py`](06_cleanup_delete_all_assets.py) | 데모 카탈로그(스키마 + 테이블 + 메트릭 뷰)를 삭제하여 처음부터 다시 빌드할 수 있도록 함 (확인을 위해 위젯에 DELETE 입력 필요) | **Databricks에서 실행** |

두 노트북 widgets의 기본값은 catalog `genie_ontology_demo` / schema
`retail_demo`입니다 — 다른 이름을 원할 경우 위젯 바에서 변경할 수 있습니다.

## 비즈니스 유스케이스 및 데이터 모델

**"Northwind Retail" 매출 & 고객 분석** — 결과로 나오는 Genie 답변을 사용자가 바로 확인하고 쉽게 검증할 수 있도록 설계된 작고 독립적인 스타 스키마입니다.

테이블(`<catalog>.retail_demo`):

| 테이블 | 유형 | 주요 컬럼 |
|---|---|---|
| `dim_date` | dimension | date_key, calendar_date, year, quarter, month, month_name, day_of_week, is_weekend |
| `dim_product` | dimension | product_key, sku, product_name, category, brand, unit_cost |
| `dim_customer` | dimension | customer_key, customer_name, segment, region, signup_date |
| `dim_store` | dimension | store_key, store_name, region, channel (Online/In-Store) |
| `fact_sales` | fact | order_id, date_key, product_key, customer_key, store_key, quantity, unit_price, revenue |
| `fact_returns` | fact | return_id, order_id, date_key, product_key, customer_key, quantity, return_amount, return_reason |
| `fact_inventory` | fact | snapshot_date_key, product_key, store_key, stock_on_hand, stock_received |

모든 테이블과 컬럼에 `COMMENT`가 있으며, 모든 테이블에 PK 제약조건,
모든 fact→dimension 관계에 FK 제약조건(추가로
`fact_returns.order_id → fact_sales.order_id`)이 정의되어 있습니다. 날짜
범위는 실행 시점에 계산됩니다(오늘 기준 최근 약 2년).
`01_create_catalog_schema_tables.py`를 주기적으로 재실행하면 데이터를
최신 상태로 유지할 수 있습니다.

### 메트릭 뷰 (Metric Views)

1. **`mv_sales_performance`** — `fact_sales`에 `dim_date`,
   `dim_product`, `dim_customer`, `dim_store`를 조인.
   Measures: `total_revenue`, `total_units_sold`, `order_count`,
   `avg_order_value`. Dimensions: 주문 날짜/연도/분기/월,
   제품 카테고리/브랜드, 고객 세그먼트/지역, 매장 지역/채널.
2. **`mv_customer_returns`** — `fact_returns`에 `dim_date`,
   `dim_product`, `dim_customer`를 조인.
   Measures: `return_count`, `units_returned`, `return_amount`. Dimensions:
   반품 날짜/연도/분기, 제품 카테고리, 반품 사유, 고객 세그먼트.
3. **`mv_inventory_health`** — `fact_inventory`에 `dim_date`,
   `dim_product`, `dim_store`를 조인.
   Measures: `avg_stock_on_hand`, `total_units_received`,
   `low_stock_snapshot_count`. Dimensions: 스냅샷 날짜/월, 제품
   카테고리, 매장 지역.

> **반품률(Return Rate)에 대한 참고사항:** 이 값은
> `fact_returns`와 `fact_sales`를 함께 사용해야 하며, metric view의
> measures는 자체 소스와 조인된 dimensions만 집계할 수 있습니다. Genie는
> "우리의 반품률은 어떻게 되나요?"라는 질문에 `mv_customer_returns.return_amount`와
> `mv_sales_performance.total_revenue`를 조합하여 답변합니다 — 이 공식은
> "고객 반품률" 페이지에 명시적으로 문서화되어 있어, Genie가 추측하는
> 대신 인용할 수 있는 신뢰할 수 있는 출처를 가집니다.

### 지니 에이전트

**`소매 분석 지니`** — 3개의 메트릭 뷰를 모두 데이터 소스로 가지며, 커스텀 지침과 샘플 질문이 포함된 에이전트입니다. 붙여넣을 정확한 이름/설명/지침 텍스트는
[`03_genie_agent_setup.py`](03_genie_agent_setup.py)에 있습니다.

### 도메인 (4개, 하위 도메인 없음)

| Domain | 할당된 자산 |
|---|---|
| `Sales` | `dim_product`, `dim_store`, `fact_sales`, `mv_sales_performance`, `Retail Analytics Genie` |
| `Customer` | `dim_customer`, `fact_returns`, `mv_customer_returns` |
| `Supply Chain` | `dim_store`, `fact_inventory`, `mv_inventory_health` |
| `Finance` | `fact_sales`, `mv_sales_performance` |

자산은 둘 이상의 domain에 속할 수 있습니다(예: `dim_store`는 `Sales`와
`Supply Chain` 모두에 속함). 도메인 거버넌스 태그는 **키 이름이 정확한
도메인 이름과 일치하는 키 전용 태그**입니다 — UI에서 이 정확히 이름들로
4개의 도메인을 생성하면 `04_apply_certification_and_domains.py`가가 수동 태그 키 조회 없이 모든 것을 자동으로 태그합니다.

### 페이지 (3개)

페이지 생성 UI 폼 필드와 정확히 일치하는 3가지 페이지의 전체 콘텐츠는 [`05_pages_content.py`](05_pages_content.py)에 있습니다.

1. **"총 매출"** (도메인: Finance) — `SUM(fact_sales.revenue)`,
   `mv_sales_performance`에 링크.
2. **"고객 반품률"** (도메: Customer) — 교차 메트릭 뷰 공식, 양쪽 메트릭 뷰 링크 포함.
3. **"소매 분석 지니 에이전트"** (도메: Sales) — 온보딩 페이지: 답변 내용, 샘플 질문, 3개의 메트릭 뷰 및 에이전트 링크 포함.

### 인증 (Certification)

모든 테이블, 모든 metric view, Genie Agent에
`certification_status = certified`가 부여됩니다. Tables/views는
`04_apply_certification_and_domains.py`에서 SQL `SET TAGS`로 인증됩니다.
Genie Agent는 수동으로 인증합니다(UI kebab menu → **인증 할당** —
Genie Agent 객체 유형에 대한 SQL 타겟이 존재하지 않아 수작업으로 인증해야 합니다.

## 구축 순서

1. 이 폴더를 Databricks Workspace 또는 Repo 폴더로 **import**합니다.
2. **`01_create_catalog_schema_tables.py`를 실행**합니다.
3. **`02_create_metric_views.py`를 실행**합니다.
4. `03_genie_agent_setup.py`의 텍스트를 사용하여 UI에서 **Genie Agent를
   생성**합니다; 3개 메트릭 뷰를 연결합니다.
5. UI에서 4개 도메인을 수동으로 **생성**합니다(Catalog Explorer → Discover →
   도메인), 도메인 이름: `Sales`, `Customer`, `Supply Chain`, `Finance`.
6. UI에서 Genie Agent를 수동으로 **인증 및 도메인 태깅**한 뒤,
   **`04_apply_certification_and_domains.py`를 실행**하여 모든 테이블과 메트릭 뷰에 적용합니다.
7. `05_pages_content.py`의 콘텐츠를 사용하여 3개 Pages를 수동으로 **생성**합니다
   (Catalog Explorer → Discover → 페이지).
8. **Genie One을 열고** 아래 데모 스크립트를 실행합니다.
9. 초기화하고 재구축하려면 **`06_cleanup_delete_all_assets.py`를 실행**합니다
   (SQL 계층 자산만 삭제 — Genie Agent, 도메인, 페이지는 완전히 초기화하려면
   수동으로 삭제해야 합니다).

### 스크립트 처리 가능 작업 vs UI 전용 작업

SQL DDL로 표현할 수 있는 것은 스크립트화할 수 있으며, Catalog Explorer / Discover / Genie One UI 흐름으로만 존재하는 것(현재 기준으로 확정된 공개 REST 엔드포인트가 없는 것)은 수동으로 처리해야 합니다.

| 항목 | 자동화 가능? |
|---|---|
| 카탈로그, 스키마, 테이블, 제약 조건, 합성 데이터 | 가능 — `01_create_catalog_schema_tables.py` |
| 메트릭 뷰 + 시맨틱 메타데이터 | 가능 — `02_create_metric_views.py` |
| 인증 + 도메인 태그 (테이블 + 메트릭 뷰) | 가능 — `04_apply_certification_and_domains.py` |
| 도메인 객체 자체 (생성 및 Discover에 게시) | 불가능 — 수동, Catalog Explorer UI |
| Genie 에이전트 생성 + 데이터 소스 연결 | 불가능 — 수동, Genie One UI |
| Genie 에이전트 인증 + 도메인 태그 | 불가능 — 수동, 이 객체 유형에 대한 SQL 타겟 없음 |
| 페이지 (생성 + 본문 콘텐츠) | 불가능 — 수동, 확인된 public API 없음 |
| SQL 계층 자산 삭제 | 가능 — `06_cleanup_delete_all_assets.py` |
| Genie 에이전트 / 도메인 / 페이지 삭제 | 불가능 — 수동 |

## 데모 스크립트

모든 구축이 완료되면, Genie One에 온톨로지의 서로 다른 레이어에서 데이터를 가져오도록 강제하는 질문을 던지고 각 응답의 "사용된 소스(sources used)" 패널을 확인해보세요.

- *"지난 분기 상품 카테고리별 총 매출은 얼마인가요?"* → `소매 분석 지니` /
  `mv_sales_performance`로 라우팅되어야 하며, 인증 배지를 인용해야 합니다.
- *"올해 대 작년 고객 반품률은 어떻게 되나요?"* → `mv_customer_returns`와
  `mv_sales_performance`를 조합해야 하며, 이상적으로는 공식을 위해 "고객 반품률" 페이지를 노출해야 합니다.
- *"여기서 '총 매출'은 어떤 의미인가요?"* →단순히 메트릭 뷰뿐만 아니라 페이지를 노출해야 합니다.
- *"매출이 가장 높으면서 반품도 많은 지역은 어디인가요?"* → 두 메트릭 뷰 간의 조인을 강제하므로 크로스 도메인 추론을 테스트하는 좋은 방법입니다.
- 인증/도메인 태깅 전과 후에 동일한 질문을 각각 던져보고, 응답 소스에서 신뢰도 점수 및 순위 차이를 비교해보세요.

## 참고 사항

- 메트릭 뷰 YAML 구문은 Databricks 릴리즈에 따라 진화했습니다(본 데모는 메트릭 뷰 스펙 1.1을 타겟팅합니다). `CREATE VIEW ... WITH METRICS`구문이 `format:` 블록에서 실패할 경우, 해당 라인을 제거하고 재실행한 뒤 Catalog Explorer의 메트릭 뷰 YAML 편집기(라이브 유효성 검사 지원)에서 형식을 나중에 추가할 수 있습니다.
- 이 데이터에 대해 Genie One 채팅을 사용할 사용자 또는 그룹에게 SQL 웨어하우스에 대한 `CAN USE` 권한이 부여되어 있는지 확인하십시오.
