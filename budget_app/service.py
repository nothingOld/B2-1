"""가계부 프로그램에서 사용하는 비즈니스 로직을 제공한다."""

import collections.abc
import datetime
import heapq
import uuid

from budget_app import models
from budget_app import repository


class TransactionService:
    """거래 추가, 조회, 검색, 수정, 삭제 기능을 제공한다."""

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

    def search_transactions(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
        query: str | None = None,
        tag: str | None = None,
    ) -> list[models.Transaction]:
        """조건에 맞는 거래 내역을 검색한다.

        Args:
            from_date: 검색 시작 날짜.
            to_date: 검색 종료 날짜.
            category: 검색할 카테고리.
            transaction_type: 검색할 거래 유형.
            query: 메모에서 검색할 문자열.
            tag: 검색할 태그.

        Returns:
            검색 조건에 맞는 최신순 거래 목록.

        Raises:
            ValueError: 날짜나 거래 유형 조건이 올바르지 않은 경우.
        """
        if from_date is not None:
            self.validate_date(from_date)

        if to_date is not None:
            self.validate_date(to_date)

        if from_date is not None and to_date is not None:
            if from_date > to_date:
                raise ValueError(
                    "검색 시작 날짜는 종료 날짜보다 늦을 수 없습니다."
                )

        if transaction_type is not None:
            self.validate_type(transaction_type)

        transactions = self._iter_matching_transactions(
            from_date=from_date,
            to_date=to_date,
            category=category,
            transaction_type=transaction_type,
            query=query,
            tag=tag,
        )

        return sorted(
            transactions,
            key=lambda transaction: transaction.date,
            reverse=True,
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

    def _iter_matching_transactions(
        self,
        from_date: str | None,
        to_date: str | None,
        category: str | None,
        transaction_type: str | None,
        query: str | None,
        tag: str | None,
    ) -> collections.abc.Iterator[models.Transaction]:
        """검색 조건에 맞는 거래를 한 건씩 반환한다."""
        for transaction in (
            self._transaction_repository.iter_transactions()
        ):
            if from_date is not None:
                if transaction.date < from_date:
                    continue

            if to_date is not None:
                if transaction.date > to_date:
                    continue

            if category is not None:
                if transaction.category != category:
                    continue

            if transaction_type is not None:
                if transaction.type != transaction_type:
                    continue

            if query is not None:
                if query.casefold() not in transaction.memo.casefold():
                    continue

            if tag is not None:
                transaction_tags = [
                    current_tag.strip()
                    for current_tag in transaction.tags.split(",")
                    if current_tag.strip()
                ]

                if tag not in transaction_tags:
                    continue

            yield transaction

    def _create_transaction_id(self) -> str:
        """고유한 거래 ID를 생성한다."""
        return f"TX-{uuid.uuid4().hex[:8].upper()}"


class CategoryService:
    """카테고리 추가, 조회, 삭제 기능을 제공한다."""

    def __init__(
        self,
        category_repository: repository.CategoryRepository,
        transaction_repository: repository.TransactionRepository,
    ) -> None:
        """카테고리 서비스에 필요한 저장소를 초기화한다.

        Args:
            category_repository: 카테고리 데이터를 처리할 저장소.
            transaction_repository: 거래 데이터를 처리할 저장소.
        """
        self._category_repository = category_repository
        self._transaction_repository = transaction_repository

    def add_category(self, category: str) -> str:
        """새로운 카테고리를 추가한다.

        Args:
            category: 추가할 카테고리 이름.

        Returns:
            추가된 카테고리 이름.

        Raises:
            ValueError: 이름이 비어 있거나 이미 존재하는 경우.
        """
        category = category.strip()

        if not category:
            raise ValueError("카테고리 이름을 입력해야 합니다.")

        if self._category_repository.exists(category):
            raise ValueError(
                f"이미 등록된 카테고리입니다: {category}"
            )

        self._category_repository.add(category)
        return category

    def list_categories(self) -> list[str]:
        """등록된 카테고리를 조회한다.

        Returns:
            등록된 카테고리 이름 목록.
        """
        return self._category_repository.list_all()

    def remove_category(self, category: str) -> None:
        """등록된 카테고리를 삭제한다.

        Args:
            category: 삭제할 카테고리 이름.

        Raises:
            ValueError: 카테고리가 없거나 거래에서 사용 중인 경우.
        """
        if not self._category_repository.exists(category):
            raise ValueError(
                f"등록되지 않은 카테고리입니다: {category}"
            )

        if self._transaction_repository.uses_category(category):
            raise ValueError(
                f"사용 중인 카테고리는 삭제할 수 없습니다: {category}"
            )

        self._category_repository.remove(category)


class BudgetService:
    """월별 예산 설정 및 조회 기능을 제공한다."""

    def __init__(
        self,
        budget_repository: repository.BudgetRepository,
    ) -> None:
        """예산 서비스에 필요한 저장소를 초기화한다.

        Args:
            budget_repository: 예산 데이터를 처리할 저장소.
        """
        self._budget_repository = budget_repository

    def set_budget(self, month: str, amount: str) -> int:
        """월별 예산을 설정한다.

        Args:
            month: YYYY-MM 형식의 월.
            amount: 설정할 예산 금액.

        Returns:
            저장된 예산 금액.

        Raises:
            ValueError: 월 또는 금액이 올바르지 않은 경우.
        """
        validated_month = self._validate_month(month)
        validated_amount = self._validate_budget_amount(amount)

        self._budget_repository.set_budget(
            validated_month,
            validated_amount,
        )

        return validated_amount

    def get_budget(self, month: str) -> int | None:
        """월별 예산을 조회한다.

        Args:
            month: 조회할 YYYY-MM 형식의 월.

        Returns:
            설정된 예산 금액. 설정되지 않았으면 None.

        Raises:
            ValueError: 월 형식이 올바르지 않은 경우.
        """
        validated_month = self._validate_month(month)

        return self._budget_repository.get_budget(validated_month)

    def _validate_month(self, month: str) -> str:
        """월 입력 형식을 검증한다."""
        try:
            parsed_month = datetime.datetime.strptime(
                month,
                "%Y-%m",
            )
        except ValueError as error:
            raise ValueError(
                "월 형식이 올바르지 않습니다. "
                "YYYY-MM 형식으로 입력해주세요."
            ) from error

        if parsed_month.strftime("%Y-%m") != month:
            raise ValueError(
                "월 형식이 올바르지 않습니다. "
                "YYYY-MM 형식으로 입력해주세요."
            )

        return month

    def _validate_budget_amount(self, amount: str) -> int:
        """예산 금액을 검증하고 정수로 변환한다."""
        try:
            amount_value = int(amount)
        except ValueError as error:
            raise ValueError(
                "예산 금액은 정수로 입력해야 합니다."
            ) from error

        if amount_value <= 0:
            raise ValueError(
                "예산 금액은 0보다 큰 값이어야 합니다."
            )

        return amount_value