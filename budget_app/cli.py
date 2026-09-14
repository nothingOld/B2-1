"""가계부 프로그램의 명령줄 인터페이스를 제공한다."""

import argparse
from collections.abc import Sequence

from budget_app import repository


def build_parser() -> argparse.ArgumentParser:
    """명령줄 인자를 처리할 파서를 생성한다.

    Returns:
        가계부 프로그램에서 사용할 ArgumentParser 객체.
    """
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부 프로그램",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """가계부 프로그램의 명령줄 인터페이스를 실행한다.

    Args:
        argv: 처리할 명령줄 인자 목록. 지정하지 않으면 현재 프로세스의
            명령줄 인자를 사용한다.

    Returns:
        정상적으로 실행되면 0을 반환한다.
    """
    initializer = repository.DataInitializer()
    initializer.initialize()

    parser = build_parser()
    parser.parse_args(argv)

    return 0