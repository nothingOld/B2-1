# B2-1# Budget App

Python 표준 라이브러리만 사용하여 구현한 파일 기반 콘솔 가계부 프로그램입니다.

수입과 지출 거래를 CSV 파일에 영구 저장하고 거래 추가, 조회, 검색,
수정, 삭제, 월별 요약, 카테고리 관리, 예산 관리, CSV 가져오기 및
내보내기 기능을 제공합니다.

## 개발 환경

- Python 3.10 이상
- 외부 라이브러리 사용 없음
- Python 표준 라이브러리만 사용

## 실행 방법

프로젝트 최상위 디렉터리에서 실행합니다.

```bash
python -m budget_app
```

전체 도움말:

```bash
python -m budget_app --help
```

각 명령의 도움말도 확인할 수 있습니다.

```bash
python -m budget_app search --help
python -m budget_app summary --help
python -m budget_app export --help
```

## 데이터 저장 위치

기본 저장 위치는 다음과 같습니다.

```text
./data
```

저장 파일은 다음 3개입니다.

```text
data/
├── transactions.csv
├── categories.csv
└── budgets.csv
```

프로그램 최초 실행 시 파일이 존재하지 않으면 자동으로 생성됩니다.

다른 데이터 저장 위치를 사용하려면 `--data-dir` 옵션을 사용합니다.

```bash
python -m budget_app --data-dir ./custom_data list
```

## 거래 데이터

`transactions.csv`는 다음 구조를 사용합니다.

```text
id,date,type,category,amount,memo,tags
```

각 필드의 의미는 다음과 같습니다.

| 필드 | 설명 |
| --- | --- |
| id | 거래 고유 ID |
| date | YYYY-MM-DD 형식의 거래 날짜 |
| type | income 또는 expense |
| category | 등록된 카테고리 |
| amount | 0보다 큰 정수 금액 |
| memo | 선택 입력 메모 |
| tags | 쉼표로 구분된 선택 입력 태그 |

## 거래 추가

```bash
python -m budget_app add
```

실행 후 거래 정보를 대화형으로 입력합니다.

예:

```text
날짜(YYYY-MM-DD): 2026-09-14
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal
```

정상 저장되면 생성된 거래 ID가 출력됩니다.

## 거래 목록

```bash
python -m budget_app list
```

최대 조회 건수 지정:

```bash
python -m budget_app list --limit 5
```

거래는 최신순으로 출력됩니다.

## 거래 검색

기간 검색:

```bash
python -m budget_app search \
  --from 2026-09-01 \
  --to 2026-09-30
```

카테고리 검색:

```bash
python -m budget_app search --category food
```

거래 유형 검색:

```bash
python -m budget_app search --type expense
```

메모 검색:

```bash
python -m budget_app search --q 점심
```

태그 검색:

```bash
python -m budget_app search --tag meal
```

여러 검색 조건을 동시에 사용할 수도 있습니다.

## 거래 수정

거래 수정은 옵션 기반 방식으로 구현되어 있습니다.

```bash
python -m budget_app update \
  --id TX-XXXXXXXX \
  --amount 20000
```

여러 항목을 동시에 수정할 수도 있습니다.

```bash
python -m budget_app update \
  --id TX-XXXXXXXX \
  --category transport \
  --amount 25000 \
  --memo "택시비"
```

입력하지 않은 항목은 기존 값을 유지합니다.

## 거래 삭제

```bash
python -m budget_app delete --id TX-XXXXXXXX
```

존재하지 않는 거래 ID를 입력하면 오류 메시지가 출력됩니다.

## 카테고리 관리

카테고리 목록:

```bash
python -m budget_app category list
```

카테고리 추가:

```bash
python -m budget_app category add
```

카테고리 삭제:

```bash
python -m budget_app category remove --name entertainment
```

현재 거래에서 사용 중인 카테고리는 삭제할 수 없습니다.

기본 카테고리는 다음과 같습니다.

```text
food
transport
salary
housing
etc
```

## 예산 관리

월별 예산 설정:

```bash
python -m budget_app budget set \
  --month 2026-09 \
  --amount 500000
```

월별 예산 조회:

```bash
python -m budget_app budget get --month 2026-09
```

## 월별 요약

```bash
python -m budget_app summary \
  --month 2026-09 \
  --top 3
```

다음 정보를 출력합니다.

- 총 수입
- 총 지출
- 잔액
- 카테고리별 지출 TOP N
- 설정된 월 예산
- 예산 사용률
- 예산 초과 경고

해당 월에 거래 데이터가 없으면 데이터 없음 메시지를 출력합니다.

## CSV 가져오기

```bash
python -m budget_app import --from import.csv
```

가져오기 CSV는 UTF-8과 헤더를 사용해야 합니다.

필수 CSV 스키마:

| column | required | 설명 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표로 구분한 문자열 |

예:

```csv
date,type,category,amount,memo,tags
2026-09-15,expense,food,12000,점심,meal
2026-09-16,expense,transport,25000,택시,transport
2026-09-17,income,salary,3000000,월급,salary
```

정상 처리된 행은 `imported`, 잘못된 행은 `skipped` 건수로 출력됩니다.

## CSV 내보내기

특정 월을 내보내는 경우:

```bash
python -m budget_app export \
  --out export.csv \
  --month 2026-09
```

기간을 지정하는 경우:

```bash
python -m budget_app export \
  --out export.csv \
  --from 2026-09-01 \
  --to 2026-09-30
```

`--out`은 반드시 입력해야 합니다.

내보내기 CSV는 다음 스키마를 사용합니다.

```text
date,type,category,amount,memo,tags
```

## 저장 처리

거래 조회는 제너레이터를 사용하여 CSV 파일을 한 행씩 읽습니다.

거래 수정과 삭제는 임시 파일에 변경 내용을 작성한 후 기존 파일을
교체하는 방식으로 처리합니다.

## 오류 처리

잘못된 입력이나 파일 처리 오류가 발생하면 스택트레이스 대신
오류 원인과 해결 힌트를 출력합니다.

정상 종료 시 종료 코드는 `0`입니다.

일반 오류 발생 시 종료 코드는 `1`입니다.

사용자가 입력 도중 강제 종료한 경우 종료 코드는 `130`입니다.