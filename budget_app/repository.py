"""가계부 프로그램의 파일 기반 데이터 저장 기능을 제공한다."""

import collections.abc
import csv
import pathlib

from budget_app import models


DEFAULT_CATEGORIES = (
    "food",
    "transport",
    "salary",
    "housing",
    "etc",
)

TRANSACTION_FIELDS = (
    "id",
    "date",
    "type",
    "category",
    "amount",
    "memo",
    "tags",
)


class DataInitializer:
    """프로그램에 필요한 CSV 데이터 파일을 초기화한다."""

    def __init__(self, data_dir: str = "./data") -> None:
        """데이터 파일의 저장 경로를 초기화한다.

        Args:
            data_dir: 프로그램의 데이터 파일을 저장할 디렉터리 경로.
        """
        self._data_dir = pathlib.Path(data_dir)
        self._transactions_path = self._data_dir / "transactions.csv"
        self._categories_path = self._data_dir / "categories.csv"
        self._budgets_path = self._data_dir / "budgets.csv"

    def initialize(self) -> None:
        """데이터 디렉터리와 필요한 CSV 파일을 생성한다."""
        self._data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_transactions_file()
        self._create_categories_file()
        self._create_budgets_file()

    def _create_transactions_file(self) -> None:
        """거래 내역 CSV 파일이 없으면 새로 생성한다."""
        if self._transactions_path.exists():
            return

        with self._transactions_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(TRANSACTION_FIELDS)

    def _create_categories_file(self) -> None:
        """카테고리 CSV 파일이 없으면 기본 카테고리와 함께 생성한다."""
        if self._categories_path.exists():
            return

        with self._categories_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["name"])

            for category in DEFAULT_CATEGORIES:
                writer.writerow([category])

    def _create_budgets_file(self) -> None:
        """예산 CSV 파일이 없으면 새로 생성한다."""
        if self._budgets_path.exists():
            return

        with self._budgets_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["month", "amount"])


class CategoryRepository:
    """카테고리 데이터 저장 및 조회 기능을 제공한다."""

    def __init__(self, data_dir: str = "./data") -> None:
        """카테고리 저장 파일 경로를 초기화한다.

        Args:
            data_dir: 프로그램의 데이터 파일을 저장할 디렉터리 경로.
        """
        self._categories_path = pathlib.Path(data_dir) / "categories.csv"

    def exists(self, category: str) -> bool:
        """카테고리가 등록되어 있는지 확인한다.

        Args:
            category: 확인할 카테고리 이름.

        Returns:
            카테고리가 존재하면 True, 존재하지 않으면 False.
        """
        with self._categories_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row["name"] == category:
                    return True

        return False

    def list_all(self) -> list[str]:
        """등록된 모든 카테고리를 조회한다.

        Returns:
            등록된 카테고리 이름 목록.
        """
        categories = []

        with self._categories_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                categories.append(row["name"])

        return categories

    def add(self, category: str) -> None:
        """새로운 카테고리를 추가한다.

        Args:
            category: 추가할 카테고리 이름.
        """
        with self._categories_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow([category])

    def remove(self, category: str) -> bool:
        """카테고리를 삭제한다.

        Args:
            category: 삭제할 카테고리 이름.

        Returns:
            삭제에 성공하면 True, 카테고리가 없으면 False.
        """
        temporary_path = self._categories_path.with_suffix(".tmp")
        found = False

        with self._categories_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as source_file:
            reader = csv.DictReader(source_file)

            with temporary_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as temporary_file:
                writer = csv.writer(temporary_file)
                writer.writerow(["name"])

                for row in reader:
                    if row["name"] == category:
                        found = True
                        continue

                    writer.writerow([row["name"]])

        if found:
            temporary_path.replace(self._categories_path)
            return True

        temporary_path.unlink(missing_ok=True)
        return False


class TransactionRepository:
    """거래 데이터를 CSV 파일에 저장하고 조회한다."""

    def __init__(self, data_dir: str = "./data") -> None:
        """거래 내역 저장 파일 경로를 초기화한다.

        Args:
            data_dir: 프로그램의 데이터 파일을 저장할 디렉터리 경로.
        """
        self._transactions_path = pathlib.Path(data_dir) / "transactions.csv"

    def add(self, transaction: models.Transaction) -> None:
        """거래 한 건을 CSV 파일에 추가한다.

        Args:
            transaction: 저장할 거래 데이터.
        """
        with self._transactions_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=TRANSACTION_FIELDS,
            )
            writer.writerow(self._transaction_to_row(transaction))

    def iter_transactions(
        self,
    ) -> collections.abc.Iterator[models.Transaction]:
        """거래 데이터를 한 건씩 읽어 반환한다.

        Yields:
            CSV 파일에서 읽은 거래 데이터.
        """
        with self._transactions_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                yield self._row_to_transaction(row)

    def get_by_id(
        self,
        transaction_id: str,
    ) -> models.Transaction | None:
        """ID에 해당하는 거래를 조회한다.

        Args:
            transaction_id: 조회할 거래 ID.

        Returns:
            거래가 존재하면 Transaction 객체, 없으면 None.
        """
        for transaction in self.iter_transactions():
            if transaction.id == transaction_id:
                return transaction

        return None

    def uses_category(self, category: str) -> bool:
        """특정 카테고리를 사용하는 거래가 있는지 확인한다.

        Args:
            category: 확인할 카테고리 이름.

        Returns:
            사용 중이면 True, 사용 중이 아니면 False.
        """
        for transaction in self.iter_transactions():
            if transaction.category == category:
                return True

        return False

    def update(self, transaction: models.Transaction) -> bool:
        """ID가 같은 거래를 수정한다.

        Args:
            transaction: 수정된 거래 데이터.

        Returns:
            수정에 성공하면 True, 대상 거래가 없으면 False.
        """
        temporary_path = self._transactions_path.with_suffix(".tmp")
        found = False

        with self._transactions_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as source_file:
            reader = csv.DictReader(source_file)

            with temporary_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as temporary_file:
                writer = csv.DictWriter(
                    temporary_file,
                    fieldnames=TRANSACTION_FIELDS,
                )
                writer.writeheader()

                for row in reader:
                    if row["id"] == transaction.id:
                        writer.writerow(
                            self._transaction_to_row(transaction)
                        )
                        found = True
                    else:
                        writer.writerow(row)

        if found:
            temporary_path.replace(self._transactions_path)
            return True

        temporary_path.unlink(missing_ok=True)
        return False

    def delete(self, transaction_id: str) -> bool:
        """ID에 해당하는 거래를 삭제한다.

        Args:
            transaction_id: 삭제할 거래 ID.

        Returns:
            삭제에 성공하면 True, 대상 거래가 없으면 False.
        """
        temporary_path = self._transactions_path.with_suffix(".tmp")
        found = False

        with self._transactions_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as source_file:
            reader = csv.DictReader(source_file)

            with temporary_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as temporary_file:
                writer = csv.DictWriter(
                    temporary_file,
                    fieldnames=TRANSACTION_FIELDS,
                )
                writer.writeheader()

                for row in reader:
                    if row["id"] == transaction_id:
                        found = True
                        continue

                    writer.writerow(row)

        if found:
            temporary_path.replace(self._transactions_path)
            return True

        temporary_path.unlink(missing_ok=True)
        return False

    def _row_to_transaction(
        self,
        row: dict[str, str],
    ) -> models.Transaction:
        """CSV 한 행을 Transaction 객체로 변환한다."""
        return models.Transaction(
            id=row["id"],
            date=row["date"],
            type=row["type"],
            category=row["category"],
            amount=int(row["amount"]),
            memo=row["memo"],
            tags=row["tags"],
        )

    def _transaction_to_row(
        self,
        transaction: models.Transaction,
    ) -> dict[str, str | int]:
        """Transaction 객체를 CSV 저장용 데이터로 변환한다."""
        return {
            "id": transaction.id,
            "date": transaction.date,
            "type": transaction.type,
            "category": transaction.category,
            "amount": transaction.amount,
            "memo": transaction.memo,
            "tags": transaction.tags,
        }


class BudgetRepository:
    """월별 예산 데이터를 저장하고 조회한다."""

    def __init__(self, data_dir: str = "./data") -> None:
        """예산 저장 파일 경로를 초기화한다.

        Args:
            data_dir: 프로그램의 데이터 파일을 저장할 디렉터리 경로.
        """
        self._budgets_path = pathlib.Path(data_dir) / "budgets.csv"

    def set_budget(self, month: str, amount: int) -> None:
        """월별 예산을 저장하거나 기존 값을 수정한다.

        Args:
            month: YYYY-MM 형식의 월.
            amount: 저장할 예산 금액.
        """
        temporary_path = self._budgets_path.with_suffix(".tmp")
        found = False

        with self._budgets_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as source_file:
            reader = csv.DictReader(source_file)

            with temporary_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as temporary_file:
                writer = csv.writer(temporary_file)
                writer.writerow(["month", "amount"])

                for row in reader:
                    if row["month"] == month:
                        writer.writerow([month, amount])
                        found = True
                    else:
                        writer.writerow(
                            [
                                row["month"],
                                row["amount"],
                            ]
                        )

                if not found:
                    writer.writerow([month, amount])

        temporary_path.replace(self._budgets_path)

    def get_budget(self, month: str) -> int | None:
        """해당 월에 설정된 예산을 조회한다.

        Args:
            month: 조회할 YYYY-MM 형식의 월.

        Returns:
            예산이 있으면 금액, 없으면 None.
        """
        with self._budgets_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row["month"] == month:
                    return int(row["amount"])

        return None