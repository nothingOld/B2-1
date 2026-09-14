"""가계부 프로그램에서 사용하는 데이터 모델을 정의한다."""

import dataclasses


@dataclasses.dataclass
class Transaction:
    """수입 또는 지출 거래 한 건을 표현한다.

    Attributes:
        id: 거래를 구분하기 위한 고유 식별자.
        date: YYYY-MM-DD 형식의 거래 날짜.
        type: income 또는 expense 중 하나인 거래 유형.
        category: 거래에 등록된 카테고리.
        amount: 0보다 큰 거래 금액.
        memo: 선택적으로 입력하는 거래 메모.
        tags: 쉼표로 구분하는 선택적 거래 태그.
    """

    id: str
    date: str
    type: str
    category: str
    amount: int
    memo: str = ""
    tags: str = ""


@dataclasses.dataclass
class MonthlySummary:
    """월별 거래 요약 결과를 표현한다.

    Attributes:
        month: YYYY-MM 형식의 요약 대상 월.
        transaction_count: 해당 월의 전체 거래 건수.
        income_total: 해당 월의 총 수입.
        expense_total: 해당 월의 총 지출.
        balance: 총 수입에서 총 지출을 뺀 잔액.
        category_expenses: 카테고리별 지출 금액 목록.
        budget: 설정된 월 예산. 없으면 None.
        usage_rate: 예산 사용률. 예산이 없으면 None.
        over_budget: 예산 초과 여부.
    """

    month: str
    transaction_count: int
    income_total: int
    expense_total: int
    balance: int
    category_expenses: list[tuple[str, int]]
    budget: int | None
    usage_rate: float | None
    over_budget: bool