"""가계부 프로그램의 명령줄 인터페이스를 제공한다."""

import argparse
import collections.abc

from budget_app import models
from budget_app import repository
from budget_app import service


def build_parser() -> argparse.ArgumentParser:
    """명령줄 인자를 처리할 파서를 생성한다.

    Returns:
        가계부 프로그램에서 사용할 ArgumentParser 객체.
    """
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부 프로그램",
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

    return parser


def main(
    argv: collections.abc.Sequence[str] | None = None,
) -> int:
    """가계부 프로그램의 명령줄 인터페이스를 실행한다.

    Args:
        argv: 처리할 명령줄 인자 목록. 지정하지 않으면 현재 프로세스의
            명령줄 인자를 사용한다.

    Returns:
        정상적으로 실행되면 0, 오류가 발생하면 1,
        사용자가 강제 종료하면 130을 반환한다.
    """
    try:
        initializer = repository.DataInitializer()
        initializer.initialize()

        parser = build_parser()
        args = parser.parse_args(argv)

        transaction_repository = repository.TransactionRepository()
        category_repository = repository.CategoryRepository()

        transaction_service = service.TransactionService(
            transaction_repository,
            category_repository,
        )

        if args.command == "add":
            return _run_add(transaction_service)

        if args.command == "list":
            return _run_list(
                transaction_service,
                args.limit,
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

        parser.print_help()
        return 0

    except ValueError as error:
        print(f"[오류] {error}")
        return 1

    except (KeyboardInterrupt, EOFError):
        print("\n[종료] 사용자 요청으로 프로그램을 종료합니다.")
        return 130


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