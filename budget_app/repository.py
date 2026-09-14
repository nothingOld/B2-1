"""가계부 프로그램의 파일 기반 데이터 저장 초기화를 제공한다."""

import csv
import pathlib


DEFAULT_CATEGORIES = (
    "food",
    "transport",
    "salary",
    "housing",
    "etc",
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
            writer.writerow(
                [
                    "id",
                    "date",
                    "type",
                    "category",
                    "amount",
                    "memo",
                    "tags",
                ]
            )

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