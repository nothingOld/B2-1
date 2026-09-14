"""가계부 프로그램의 명령줄 인터페이스를 제공한다."""

import argparse
import collections.abc
import functools

from budget_app import models
from budget_app import repository
from budget_app import service


def handle_cli_errors(
    function: collections.abc.Callable[..., int],
) -> collections.abc.Callable[..., int]:
    """CLI 실행 중 발생하는 공통 예외를 처리한다.

    Args:
        function: 예외 처리를 적용할 함수.

    Returns:
        공통 예외 처리가 적용된 함수.
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> int:
        try:
            return function(*args, **kwargs)

        except ValueError as error:
            print(f"[오류] {error}")
            print("[힌트] 입력값과 파일 경로를 확인한 후 다시 실행해주세요.")
            return 1

        except OSError as error:
            print(f"[오류] 파일 처리 중 문제가 발생했습니다: {error}")
            print("[힌트] 파일 경로와 파일 접근 권한을 확인해주세요.")
            return 1

        except KeyError as error:
            print(f"[오류] 데이터 파일에 필요한 항목이 없습니다: {error}")
            print("[힌트] CSV 파일의 헤더와 데이터 구조를 확인해주세요.")
            return 1

        except (KeyboardInterrupt, EOFError):
            print("\n[종료] 사용자 요청으로 프로그램을 종료합니다.")
            return 130

    return wrapper


def build_parser() -> argparse.ArgumentParser:
    """명령줄 인자를 처리할 파서를 생성한다.

    Returns:
        가계부 프로그램에서 사용할 ArgumentParser 객체.
    """
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부 프로그램",
    )

    parser.add_argument(
        "--data-dir",
        default="./data",
        help="데이터 파일을 저장할 폴더입니다. 기본값은 ./data입니다.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
    )

    subparsers.add_parser(
        "add",
        help="새로운 거래를 추가합니다.",
    )

    list_parser = subparsers.add_parser(
        "list",
        help="거래 목록을 조회합니다.",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="조회할 최대 거래 건수입니다. 기본값은 10입니다.",
    )

    search_parser = subparsers.add_parser(
        "search",
        help="조건에 맞는 거래를 검색합니다.",
    )
    search_parser.add_argument(
        "--from",
        dest="from_date",
        help="검색 시작 날짜입니다. YYYY-MM-DD 형식입니다.",
    )
    search_parser.add_argument(
        "--to",
        dest="to_date",
        help="검색 종료 날짜입니다. YYYY-MM-DD 형식입니다.",
    )
    search_parser.add_argument(
        "--category",
        help="검색할 카테고리입니다.",
    )
    search_parser.add_argument(
        "--type",
        help="검색할 거래 유형입니다. income 또는 expense입니다.",
    )
    search_parser.add_argument(
        "--q",
        help="메모에서 검색할 문자열입니다.",
    )
    search_parser.add_argument(
        "--tag",
        help="검색할 태그입니다.",
    )

    summary_parser = subparsers.add_parser(
        "summary",
        help="월별 거래 내역을 요약합니다.",
    )
    summary_parser.add_argument(
        "--month",
        required=True,
        help="요약할 월입니다. YYYY-MM 형식입니다.",
    )
    summary_parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="출력할 카테고리별 지출 순위 개수입니다. 기본값은 3입니다.",
    )

    update_parser = subparsers.add_parser(
        "update",
        help="기존 거래를 수정합니다.",
    )
    update_parser.add_argument(
        "--id",
        required=True,
        help="수정할 거래 ID입니다.",
    )
    update_parser.add_argument("--date")
    update_parser.add_argument("--type")
    update_parser.add_argument("--category")
    update_parser.add_argument("--amount")
    update_parser.add_argument("--memo")
    update_parser.add_argument("--tags")

    delete_parser = subparsers.add_parser(
        "delete",
        help="거래를 삭제합니다.",
    )
    delete_parser.add_argument(
        "--id",
        required=True,
        help="삭제할 거래 ID입니다.",
    )

    category_parser = subparsers.add_parser(
        "category",
        help="카테고리를 관리합니다.",
    )
    category_subparsers = category_parser.add_subparsers(
        dest="category_command",
    )

    category_subparsers.add_parser(
        "add",
        help="새로운 카테고리를 추가합니다.",
    )

    category_subparsers.add_parser(
        "list",
        help="카테고리 목록을 조회합니다.",
    )

    category_remove_parser = category_subparsers.add_parser(
        "remove",
        help="카테고리를 삭제합니다.",
    )
    category_remove_parser.add_argument(
        "--name",
        required=True,
        help="삭제할 카테고리 이름입니다.",
    )

    budget_parser = subparsers.add_parser(
        "budget",
        help="월별 예산을 관리합니다.",
    )
    budget_subparsers = budget_parser.add_subparsers(
        dest="budget_command",
    )

    budget_set_parser = budget_subparsers.add_parser(
        "set",
        help="월별 예산을 설정합니다.",
    )
    budget_set_parser.add_argument(
        "--month",
        required=True,
        help="예산을 설정할 월입니다. YYYY-MM 형식입니다.",
    )
    budget_set_parser.add_argument(
        "--amount",
        required=True,
        help="설정할 예산 금액입니다.",
    )

    budget_get_parser = budget_subparsers.add_parser(
        "get",
        help="월별 예산을 조회합니다.",
    )
    budget_get_parser.add_argument(
        "--month",
        required=True,
        help="예산을 조회할 월입니다. YYYY-MM 형식입니다.",
    )

    import_parser = subparsers.add_parser(
        "import",
        help="CSV 파일의 거래 내역을 가져옵니다.",
    )
    import_parser.add_argument(
        "--from",
        dest="source_path",
        required=True,
        help="가져올 CSV 파일 경로입니다.",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="거래 내역을 CSV 파일로 내보냅니다.",
    )
    export_parser.add_argument(
        "--out",
        required=True,
        help="생성할 CSV 파일 경로입니다.",
    )
    export_parser.add_argument(
        "--month",
        help="내보낼 월입니다. YYYY-MM 형식입니다.",
    )
    export_parser.add_argument(
        "--from",
        dest="from_date",
        help="내보내기 시작 날짜입니다. YYYY-MM-DD 형식입니다.",
    )
    export_parser.add_argument(
        "--to",
        dest="to_date",
        help="내보내기 종료 날짜입니다. YYYY-MM-DD 형식입니다.",
    )

    return parser


@handle_cli_errors
def main(
    argv: collections.abc.Sequence[str] | None = None,
) -> int:
    """가계부 프로그램의 명령줄 인터페이스를 실행한다.

    Args:
        argv: 처리할 명령줄 인자 목록. 지정하지 않으면 현재 프로세스의
            명령줄 인자를 사용한다.

    Returns:
        프로그램 종료 코드를 반환한다.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    initializer = repository.DataInitializer(args.data_dir)
    initializer.initialize()

    transaction_repository = repository.TransactionRepository(
        args.data_dir
    )
    category_repository = repository.CategoryRepository(
        args.data_dir
    )
    budget_repository = repository.BudgetRepository(
        args.data_dir
    )

    transaction_service = service.TransactionService(
        transaction_repository,
        category_repository,
    )
    category_service = service.CategoryService(
        category_repository,
        transaction_repository,
    )
    budget_service = service.BudgetService(
        budget_repository,
    )
    summary_service = service.SummaryService(
        transaction_repository,
        budget_repository,
    )

    if args.command == "add":
        return _run_add(transaction_service)

    if args.command == "list":
        return _run_list(
            transaction_service,
            args.limit,
        )

    if args.command == "search":
        return _run_search(
            transaction_service,
            args,
        )

    if args.command == "summary":
        return _run_summary(
            summary_service,
            args.month,
            args.top,
        )

    if args.command == "update":
        return _run_update(
            transaction_service,
            args,
        )

    if args.command == "delete":
        return _run_delete(
            transaction_service,
            args.id,
        )

    if args.command == "category":
        return _run_category(
            category_service,
            args,
        )

    if args.command == "budget":
        return _run_budget(
            budget_service,
            args,
        )

    if args.command == "import":
        return _run_import(
            transaction_service,
            args.source_path,
        )

    if args.command == "export":
        return _run_export(
            transaction_service,
            args,
        )

    parser.print_help()
    return 0


def _run_add(
    transaction_service: service.TransactionService,
) -> int:
    """대화형 입력으로 새로운 거래를 추가한다."""
    while True:
        date = input("날짜(YYYY-MM-DD): ")

        try:
            transaction_service.validate_date(date)
            break
        except ValueError as error:
            print(f"[오류] {error}")

    while True:
        transaction_type = input("타입(income/expense): ")

        try:
            transaction_service.validate_type(transaction_type)
            break
        except ValueError as error:
            print(f"[오류] {error}")

    while True:
        category = input("카테고리: ")

        try:
            transaction_service.validate_category(category)
            break
        except ValueError as error:
            print(f"[오류] {error}")

    while True:
        amount = input("금액(양수): ")

        try:
            transaction_service.validate_amount(amount)
            break
        except ValueError as error:
            print(f"[오류] {error}")

    memo = input("메모(선택): ")
    tags = input("태그(쉼표로 구분, 없으면 엔터): ")

    transaction = transaction_service.add_transaction(
        date=date,
        transaction_type=transaction_type,
        category=category,
        amount=amount,
        memo=memo,
        tags=tags,
    )

    print(f"[저장 완료] id={transaction.id}")
    return 0


def _run_list(
    transaction_service: service.TransactionService,
    limit: int,
) -> int:
    """최신 거래 목록을 출력한다."""
    transactions = transaction_service.list_transactions(limit)

    if not transactions:
        print("[안내] 거래 내역이 없습니다.")
        return 0

    for transaction in transactions:
        _print_transaction(transaction)

    return 0


def _run_search(
    transaction_service: service.TransactionService,
    args: argparse.Namespace,
) -> int:
    """입력된 조건에 맞는 거래를 검색하고 출력한다."""
    transactions = transaction_service.search_transactions(
        from_date=args.from_date,
        to_date=args.to_date,
        category=args.category,
        transaction_type=args.type,
        query=args.q,
        tag=args.tag,
    )

    if not transactions:
        print("[안내] 검색 조건에 맞는 거래가 없습니다.")
        return 0

    for transaction in transactions:
        _print_transaction(transaction)

    return 0


def _run_summary(
    summary_service: service.SummaryService,
    month: str,
    top: int,
) -> int:
    """월별 거래 및 예산 요약을 출력한다."""
    summary = summary_service.get_monthly_summary(
        month,
        top,
    )

    if summary.transaction_count == 0:
        print(f"[안내] {summary.month} 데이터 없음")

        if summary.budget is not None:
            print(
                f"예산: {summary.budget}원 "
                f"(사용률 {summary.usage_rate:.1f}%)"
            )

        return 0

    print(f"총 수입: {summary.income_total}원")
    print(f"총 지출: {summary.expense_total}원")
    print(f"잔액: {summary.balance}원")

    if summary.budget is not None:
        print(
            f"예산: {summary.budget}원 "
            f"(사용률 {summary.usage_rate:.1f}%)"
        )

        if summary.over_budget:
            print("[경고] 예산을 초과했습니다.")

    print()
    print(f"지출 TOP {top}")

    if not summary.category_expenses:
        print("[안내] 지출 내역이 없습니다.")
        return 0

    for rank, category_expense in enumerate(
        summary.category_expenses,
        start=1,
    ):
        category, amount = category_expense
        print(f"{rank}) {category} {amount}원")

    return 0


def _run_update(
    transaction_service: service.TransactionService,
    args: argparse.Namespace,
) -> int:
    """입력된 옵션을 사용해 기존 거래를 수정한다."""
    transaction = transaction_service.update_transaction(
        transaction_id=args.id,
        date=args.date,
        transaction_type=args.type,
        category=args.category,
        amount=args.amount,
        memo=args.memo,
        tags=args.tags,
    )

    print(f"[수정 완료] id={transaction.id}")
    return 0


def _run_delete(
    transaction_service: service.TransactionService,
    transaction_id: str,
) -> int:
    """ID에 해당하는 거래를 삭제한다."""
    transaction_service.delete_transaction(transaction_id)

    print(f"[삭제 완료] id={transaction_id}")
    return 0


def _run_category(
    category_service: service.CategoryService,
    args: argparse.Namespace,
) -> int:
    """카테고리 하위 명령을 실행한다."""
    if args.category_command == "add":
        category = input("카테고리명: ")
        added_category = category_service.add_category(category)
        print(f"[저장 완료] category={added_category}")
        return 0

    if args.category_command == "list":
        categories = category_service.list_categories()

        for category in categories:
            print(f"- {category}")

        return 0

    if args.category_command == "remove":
        category_service.remove_category(args.name)
        print(f"[삭제 완료] category={args.name}")
        return 0

    print("[안내] category 하위 명령을 입력해주세요.")
    return 0


def _run_budget(
    budget_service: service.BudgetService,
    args: argparse.Namespace,
) -> int:
    """예산 하위 명령을 실행한다."""
    if args.budget_command == "set":
        amount = budget_service.set_budget(
            args.month,
            args.amount,
        )

        print(
            f"[저장 완료] {args.month} 예산 "
            f"{amount}원"
        )
        return 0

    if args.budget_command == "get":
        amount = budget_service.get_budget(args.month)

        if amount is None:
            print(
                f"[안내] {args.month}에 설정된 예산이 없습니다."
            )
            return 0

        print(f"{args.month} 예산: {amount}원")
        return 0

    print("[안내] budget 하위 명령을 입력해주세요.")
    return 0


def _run_import(
    transaction_service: service.TransactionService,
    source_path: str,
) -> int:
    """CSV 파일에서 거래 내역을 가져온다."""
    imported, skipped = transaction_service.import_transactions(
        source_path
    )

    print(
        f"[완료] imported={imported}, "
        f"skipped={skipped}"
    )
    return 0


def _run_export(
    transaction_service: service.TransactionService,
    args: argparse.Namespace,
) -> int:
    """조건에 맞는 거래 내역을 CSV 파일로 내보낸다."""
    count = transaction_service.export_transactions(
        output_path=args.out,
        month=args.month,
        from_date=args.from_date,
        to_date=args.to_date,
    )

    print(f"[완료] {args.out} ({count} records)")
    return 0


def _print_transaction(
    transaction: models.Transaction,
) -> None:
    """거래 한 건을 콘솔에 출력한다."""
    print(
        f"{transaction.id} | "
        f"{transaction.date} | "
        f"{transaction.type} | "
        f"{transaction.category} | "
        f"{transaction.amount} | "
        f"{transaction.memo}"
    )