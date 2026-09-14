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