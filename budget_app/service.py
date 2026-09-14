"""가계부 프로그램에서 사용하는 비즈니스 로직을 제공한다."""

import datetime
import heapq
import uuid

from budget_app import models
from budget_app import repository


class TransactionService:
    """거래 추가, 조회, 수정, 삭제 기능을 제공한다."""

    def __init__(
        self,
        transaction_repository: repository.TransactionRepository,
        category_repository: repository.CategoryRepository,
    ) -> None:
        """거래 서비스에 필요한 저장소를 초기화한다.

        Args:
            transaction_repository: 거래 데이터를 처리할 저장소.
            category_repository: 카테고리 데이터를 처리할 저장소.
        """
        self._transaction_repository = transaction_repository
        self._category_repository = category_repository

    def add_transaction(
        self,
        date: str,
        transaction_type: str,
        category: str,
        amount: str,
        memo: str,
        tags: str,
    ) -> models.Transaction:
        """새로운 거래를 생성하고 저장한다.

        Args:
            date: 거래 날짜.
            transaction_type: 거래 유형.
            category: 거래 카테고리.
            amount: 거래 금액.
            memo: 거래 메모.
            tags: 거래 태그.

        Returns:
            저장된 Transaction 객체.

        Raises:
            ValueError: 입력값이 올바르지 않은 경우.
        """
        validated_date = self.validate_date(date)
        validated_type = self.validate_type(transaction_type)
        validated_category = self.validate_category(category)
        validated_amount = self.validate_amount(amount)

        transaction = models.Transaction(
            id=self._create_transaction_id(),
            date=validated_date,
            type=validated_type,
            category=validated_category,
            amount=validated_amount,
            memo=memo,
            tags=tags,
        )

        self._transaction_repository.add(transaction)
        return transaction

    def list_transactions(
        self,
        limit: int,
    ) -> list[models.Transaction]:
        """최신 거래 내역을 지정한 개수만큼 조회한다.

        Args:
            limit: 조회할 최대 거래 건수.

        Returns:
            최신순으로 정렬된 거래 목록.

        Raises:
            ValueError: limit 값이 1보다 작은 경우.
        """
        if limit < 1:
            raise ValueError("limit 값은 1 이상이어야 합니다.")

        return heapq.nlargest(
            limit,
            self._transaction_repository.iter_transactions(),
            key=lambda transaction: transaction.date,
        )

    def update_transaction(
        self,
        transaction_id: str,
        date: str | None = None,
        transaction_type: str | None = None,
        category: str | None = None,
        amount: str | None = None,
        memo: str | None = None,
        tags: str | None = None,
    ) -> models.Transaction:
        """기존 거래의 입력된 항목만 수정한다.

        Args:
            transaction_id: 수정할 거래 ID.
            date: 변경할 거래 날짜.
            transaction_type: 변경할 거래 유형.
            category: 변경할 카테고리.
            amount: 변경할 거래 금액.
            memo: 변경할 메모.
            tags: 변경할 태그.

        Returns:
            수정된 Transaction 객체.

        Raises:
            ValueError: 거래가 없거나 수정할 값이 잘못된 경우.
        """
        transaction = self._transaction_repository.get_by_id(
            transaction_id
        )

        if transaction is None:
            raise ValueError(
                f"거래 ID '{transaction_id}'를 찾을 수 없습니다."
            )

        if all(
            value is None
            for value in (
                date,
                transaction_type,
                category,
                amount,
                memo,
                tags,
            )
        ):
            raise ValueError("수정할 항목을 하나 이상 입력해야 합니다.")

        updated_transaction = models.Transaction(
            id=transaction.id,
            date=(
                self.validate_date(date)
                if date is not None
                else transaction.date
            ),
            type=(
                self.validate_type(transaction_type)
                if transaction_type is not None
                else transaction.type
            ),
            category=(
                self.validate_category(category)
                if category is not None
                else transaction.category
            ),
            amount=(
                self.validate_amount(amount)
                if amount is not None
                else transaction.amount
            ),
            memo=memo if memo is not None else transaction.memo,
            tags=tags if tags is not None else transaction.tags,
        )

        self._transaction_repository.update(updated_transaction)
        return updated_transaction

    def delete_transaction(self, transaction_id: str) -> None:
        """ID에 해당하는 거래를 삭제한다.

        Args:
            transaction_id: 삭제할 거래 ID.

        Raises:
            ValueError: 해당 ID의 거래가 존재하지 않는 경우.
        """
        deleted = self._transaction_repository.delete(transaction_id)

        if not deleted:
            raise ValueError(
                f"거래 ID '{transaction_id}'를 찾을 수 없습니다."
            )

    def validate_date(self, date: str) -> str:
        """거래 날짜 형식을 검증한다.

        Args:
            date: 검증할 거래 날짜.

        Returns:
            검증이 완료된 거래 날짜.

        Raises:
            ValueError: 날짜 형식이 올바르지 않은 경우.
        """
        try:
            parsed_date = datetime.datetime.strptime(
                date,
                "%Y-%m-%d",
            )
        except ValueError as error:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. "
                "YYYY-MM-DD 형식으로 입력해주세요."
            ) from error

        if parsed_date.strftime("%Y-%m-%d") != date:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. "
                "YYYY-MM-DD 형식으로 입력해주세요."
            )

        return date

    def validate_type(self, transaction_type: str) -> str:
        """거래 유형을 검증한다.

        Args:
            transaction_type: 검증할 거래 유형.

        Returns:
            검증이 완료된 거래 유형.

        Raises:
            ValueError: 허용되지 않은 거래 유형인 경우.
        """
        if transaction_type not in ("income", "expense"):
            raise ValueError(
                "거래 유형은 income 또는 expense만 사용할 수 있습니다."
            )

        return transaction_type

    def validate_category(self, category: str) -> str:
        """카테고리가 등록되어 있는지 검증한다.

        Args:
            category: 검증할 카테고리 이름.

        Returns:
            검증이 완료된 카테고리 이름.

        Raises:
            ValueError: 등록되지 않은 카테고리인 경우.
        """
        if not self._category_repository.exists(category):
            raise ValueError(
                f"등록되지 않은 카테고리입니다: {category}"
            )

        return category

    def validate_amount(self, amount: str) -> int:
        """거래 금액을 검증하고 정수로 변환한다.

        Args:
            amount: 검증할 거래 금액.

        Returns:
            정수로 변환된 거래 금액.

        Raises:
            ValueError: 금액이 정수가 아니거나 0 이하인 경우.
        """
        try:
            amount_value = int(amount)
        except ValueError as error:
            raise ValueError(
                "금액은 정수로 입력해야 합니다."
            ) from error

        if amount_value <= 0:
            raise ValueError(
                "금액은 0보다 큰 값이어야 합니다."
            )

        return amount_value

    def _create_transaction_id(self) -> str:
        """고유한 거래 ID를 생성한다."""
        return f"TX-{uuid.uuid4().hex[:8].upper()}"