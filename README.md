# Mini NPU Simulator (진행 중)

3×3부터 25×25까지의 패턴과 필터를 MAC(Multiply-Accumulate, 곱한 값을 누적해 더하는 연산)으로 비교해
십자가(Cross)와 X를 판별하는 Python 콘솔 프로그램이다. 외부 라이브러리(NumPy 등) 없이 반복문으로 직접 구현한다.

> 이 문서는 작업 단계마다 갱신한다. 완료한 항목만 "완료"로 표시하고, 아직 하지 않은 항목은 미완료로 남긴다.

## 1. 진행 현황

| 단계 | 내용 | 상태 |
|---|---|---|
| 1 | n×n 2차원 리스트 다루기 | 완료 |
| 2 | MAC 연산 함수 `mac()` | 완료 |
| 3 | 모드 1: 3×3 입력, 검증, 재입력 | 완료 |
| 4 | 점수 비교와 판정(A/B), epsilon 동점 처리 | 모드 1 판정 확인 / epsilon 동점(UNDECIDED) 완료 |
| 5 | 라벨 정규화(`+`→Cross, `x`→X) | 완료 |
| 6 | 모드 2: data.json 일괄 판정, PASS/FAIL | 요약 필요 |
| 7 | 성능 측정(크기별 10회 평균 ms) | 미완료 |
| 8 | 결과 요약, 결과 리포트(실패 원인 + 시간 복잡도) | 미완료 |
| 보너스 | 1차원 배열 최적화, 패턴 생성기 | 미정 |

## 2. 실행 방법

- 실행 환경: Windows / PowerShell, Python 버전 Python 3.14.6
- 파일 위치: `main.py`와 `data.json`을 같은 폴더에 둔다.
- 실행: `py main.py`

## 3. 파일 구성

```text
.
├── main.py      # 프로그램 전체 (함수 정의 + 실행)
├── data.json    # 제공된 필터/패턴 데이터 (수정하지 않음)
└── README.md
```

처음에는 함수를 파일별로 나눠 만들었다가, import 연결이 필요해서 `main.py` 하나로 합쳤다.

## 4. data.json 구조 해석

```text
filters   size_5 / size_13 / size_25  →  cross, x (각각 N×N 숫자표)
patterns  size_{N}_{번호}             →  input (N×N 숫자표), expected (정답 라벨)
```

- 케이스 키 `size_13_2`에서 `13`은 한 변의 길이, `2`는 케이스 번호이다. 키의 N으로 같은 크기의 필터를 고른다.
- 패턴은 6개(5, 13, 25 크기별 2개)이고, 3×3은 data.json에 없어 모드 1에서 직접 입력한다.
- 필터 키는 `cross`/`x`인데 expected는 `+`/`x`로 표기가 섞여 있다. 그대로 비교하면 정상 판정도 FAIL이 되므로
  내부 표준 라벨 `Cross`/`X`로 통일(정규화)해야 한다. (5단계에서 구현 완료)

## 5. 구현 요약

### MAC 연산

```python
def mac(pattern, filt):
    total = 0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total
```

같은 위치의 값끼리 곱해 `total`에 누적한다. 이중 for문이라 N×N 칸을 한 번씩 방문하며, 곱셈과 덧셈이 각각 N²번 발생한다.

### 모드 1 입력 처리

- `read_row(n)`: 한 줄을 받아 공백으로 쪼갠 뒤 두 가지를 검증한다.
  1. 숫자 개수가 n개가 아니면 안내 문구를 출력하고 `None`을 반환한다.
  2. 숫자로 바꿀 수 없으면(`float()` 변환 실패, `ValueError`) 안내 문구를 출력하고 `None`을 반환한다.
- `read_matrix(name, n)`: `read_row`가 `None`을 돌려주면 같은 줄만 다시 입력받는다. 3줄이 모이면 3×3 리스트를 반환한다.
- 틀린 줄만 다시 받는 방식이라, 앞서 올바르게 입력한 줄은 유지된다.

### 점수 비교 정책 (epsilon)

두 점수의 차이가 `1e-9`보다 작으면 같은 점수로 보고 판정 불가(UNDECIDED)로 처리한다.
이유와 예시는 7절에 정리했다.

### 라벨 정규화 구현
-정규화가 없다면 정상 케이스도 FAIL이 되었을 것
```powershell
PS C:\Users\***\Desktop\mac> py main.py
dict_keys(['size_5', 'size_13', 'size_25'])
'+' → Cross
'x' → X
'X' → X
'cross' → Cross
' Cross ' → Cross
'CROSS' → Cross
'circle' → None
None → None
PS C:\Users\***\Desktop\mac> py main.py
dict_keys(['size_5', 'size_13', 'size_25'])
X
cross
cross → Cross
x → X
```

- 모드 2 구현 요약:
  키에서 N 추출 → 크기 검증 → 필터 키 정규화 → MAC → 판정 → expected 비교

## 6. 실행 결과 

### 모드 1

필터 A = `1 1 1 / 0 0 0 / 0 0 0`, 필터 B = `1 1 1 / 0 0 1 / 0 0 0`, 패턴 = `1 1 1 / 1 1 1 / 1 1 0`을 입력했다.
중간에 일부러 틀린 입력(`1 a 1`, `a a 1`, `a a`)을 넣어 재입력 동작을 확인했다.

```text
필터 A (3줄 입력, 공백 구분)
숫자 입력: 1 1 1
숫자 입력: 1 a 1
입력 형식 오류: 각 줄에 3개의 숫자만 입력하세요.
숫자 입력: 0 0 0
숫자 입력: a a 1
입력 형식 오류: 각 줄에 3개의 숫자만 입력하세요.
숫자 입력: a a
입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.
숫자 입력: 0 0 0
...
A 점수: 3.0
B 점수: 4.0
판정: B
```
  손계산으로 검산했다. A는 패턴의 첫 행 세 칸(1×1)만 겹쳐 3점이다. B는 첫 행 3점에 2행 3열(1×1) 1점이 더해져 4점이다. 따라서 판정 B가 맞다.

```text
필터 A (3줄 입력, 공백 구분)
숫자 입력: 0 1 0
숫자 입력: 1 1 1
숫자 입력: 0 1 0
필터 B (3줄 입력, 공백 구분)
숫자 입력: 1 0 1
숫자 입력: 0 1 0
숫자 입력: 1 0 1
패턴 (3줄 입력, 공백 구분)
숫자 입력: 1 0 1
숫자 입력: 0 1 0
숫자 입력: 1 0 1
A 점수: 1.0
B 점수: 5.0
판정: B
```
  십자가/X/X 인 경우

```text
필터 A (3줄 입력, 공백 구분)
숫자 입력: 1 1 1
숫자 입력: 1 1 1
숫자 입력: 1 1 0
필터 B (3줄 입력, 공백 구분)
숫자 입력: 1 1 1
숫자 입력: 1 1 1
숫자 입력: 1 1 0
패턴 (3줄 입력, 공백 구분)
숫자 입력: 0 0 0
숫자 입력: 0 0 0
숫자 입력: 0 1 0
A 점수: 1.0
B 점수: 1.0
판정: UNDECIDED
```
  동점 입력(같은 필터 두 개)의 실행 화면

### 모드 2
- 동점 3건이 FAIL인 이유:
```powershell
PS C:\Users\***\Desktop\mac> py main.py
dict_keys(['size_5', 'size_13', 'size_25'])
size_5_1 FAIL UNDECIDED X 동점(UNDECIDED)
size_5_2 PASS Cross Cross 
size_13_1 PASS X X 
size_13_2 FAIL UNDECIDED Cross 동점(UNDECIDED)
size_25_1 FAIL UNDECIDED X 동점(UNDECIDED)
size_25_2 PASS Cross Cross 
```
 예를 들어 size_5_1은 Cross 필터 가운데 값 0.9와 X 패턴 9칸 × 0.1 = 0.9가 같게 설계돼 있고, float 계산에서는 0.9와 0.8999999999999999처럼 미세하게 어긋나지만 epsilon 정책에 따라 동점이다.

- 모드 2 결과 출력과 요약(총/통과/실패, 실패 ID와 사유)
```powershell
PS C:\Users\MKJ\Desktop\mac> PY MAIN.PY
dict_keys(['size_5', 'size_13', 'size_25'])
[size_5_1] FAIL
  Cross=0.9  X=0.8999999999999999  판정=UNDECIDED  expected=X
  사유: 동점(UNDECIDED)
[size_5_2] PASS
  Cross=8.9  X=0.1  판정=Cross  expected=Cross
[size_13_1] PASS
  Cross=0.3  X=14.700000000000008  판정=X  expected=X
[size_13_2] FAIL
  Cross=7.499999999999997  X=7.5  판정=UNDECIDED  expected=Cross
  사유: 동점(UNDECIDED)
[size_25_1] FAIL
  Cross=4.9  X=4.899999999999999  판정=UNDECIDED  expected=X
  사유: 동점(UNDECIDED)
[size_25_2] PASS
  Cross=52.9  X=0.1  판정=Cross  expected=Cross
------------------------------
총 6개 / 통과 3개 / 실패 3개
실패 케이스:
  - size_5_1: 동점(UNDECIDED)
  - size_13_2: 동점(UNDECIDED)
  - size_25_1: 동점(UNDECIDED)
```

### 임시 print 정리 후 메인 화면 표출
=== Mini NPU Simulator ===
1. 모드 1 (3x3 직접 입력)
2. 모드 2 (data.json 분석)
선택: abc
1, 2, 0 중에서 선택하세요.

=== Mini NPU Simulator ===
1. 모드 1 (3x3 직접 입력)
2. 모드 2 (data.json 분석)
0. 종료
선택: 0

### 크기별 MAC 성능 측정과 N² 표
```powershell
------------------------------
총 6개 / 통과 3개 / 실패 3개
실패 케이스:
  - size_5_1: 동점(UNDECIDED)
  - size_13_2: 동점(UNDECIDED)
  - size_25_1: 동점(UNDECIDED)

[성능 분석] (각 크기 10회 반복 평균)
크기(N×N)          평균 시간(ms)       연산 횟수(N²)
3x3                 0.0018               9
5x5                 0.0026              25
13x13               0.0130             169
25x25               0.0444             625
```

## 7. 개념 정리

### MAC 연산
같은 위치의 두 숫자를 곱하고, 그 값들을 모두 더하는 계산이다. 입력과 필터가 닮을수록 같은 자리에 1이 겹쳐 점수가 높아진다.
3×3 십자가끼리는 5점, 십자가와 X는 중심 한 칸만 겹쳐 1점이다.

### 부동소수점 오차와 epsilon
컴퓨터는 소수를 이진수로 저장하는데, 0.1처럼 이진수로 딱 떨어지지 않는 수는 아주 작은 오차가 생긴다.
(`0.1 + 0.2 == 0.3`이 False로 나온다.) MAC은 곱셈과 덧셈을 N²번 반복해 이 오차가 쌓인다.
그래서 수학적으로 같은 두 점수가 0.9와 0.8999999999999999처럼 어긋날 수 있고, `==` 비교로는 동점을 찾지 못한다.
epsilon(허용오차)은 "차이가 1e-9보다 작으면 같다고 본다"는 판정 기준이다.
너무 크면 진짜 다른 점수도 같다고 보고, 너무 작으면 누적 오차를 못 거른다. 1e-9는 오차(약 1e-16)보다 충분히 크고
실제 점수 차이보다 충분히 작은 값이라 과제에서 권장한다. epsilon은 오차를 없애는 것이 아니라 판정 기준을 정하는 것이다.

### 대소문자 구분
문자열 비교는 대소문자를 구분하므로, 상태값은 한 가지 표기로 통일하고 같은 철자로 비교한다.
상태값은 관례적으로 대문자로 표기한다.
"cross"와 "Cross", "PASS", "FAIL", "X", "UNDECIDED", "EPSILON" 등
한국어에는 대소문자가 없기 때문에 낯설게 느껴질 수 있으므로 주의할 것.

### 시간 복잡도 O(N²)
빅 오(Big O)는 입력 크기 N이 커질 때 연산량이 늘어나는 비율을 나타내는 표기이다.
MAC은 N×N 칸을 모두 한 번씩 계산하므로 연산 횟수가 3×3=9, 5×5=25, 13×13=169, 25×25=625로 N²에 비례한다.
(측정 결과는 7단계 이후 이 절에 추가한다.)

## 8. 트러블슈팅

### 8-1. 첫 줄만 입력받고 종료됨
- 문제: `read_matrix`를 실행하면 첫 줄을 입력하자마자 `[[...]]`만 출력하고 끝났다.
- 원인 가설: `return rows`가 for문 안쪽에 들여쓰기 되어 첫 반복에서 함수가 끝난다.
- 확인: `return rows`를 for와 같은 깊이로 옮겼다.
- 해결: 3줄을 모두 입력받고 3×3 리스트가 만들어졌다. (`mac`의 `return total`도 같은 원리이다.)

### 8-2. 오류 안내 문구가 실제 입력 범위와 맞지 않음
- 문제: 안내 문구에 "3개"가 고정되어 있는데 함수는 `n`을 받는다.
- 해결: 문구에 `n` 값을 넣는 f-string(`f"... {n}개 ..."`)으로 바꿨다.

### 8-3. any 오용
- 문제: parse_size_from_key에 any를 넣었다가 오류 발생
- 해결: 케이스 키에서 크기 N을 뽑고 정사각형 크기 검증하는 것이므로 n을 넣어야 했음.
  data.json 키 규칙: size_N_번호 (예: size_5_1)
  
```powershell
PS C:\Users\User\Desktop\third_MAC> py main.py
dict_keys(['size_5', 'size_13', 'size_25'])
True
False
False
```

## 9. 앞으로 할 일

- [x] 라벨 정규화 함수(`+`, `cross` → Cross / `x`, `X` → X)
- [x] 모드 2: 키에서 N 추출, 필터·패턴 크기 검증, 불일치 시 케이스 단위 FAIL
- [x] 판정(Cross/X/UNDECIDED)과 expected 비교, 요약(총/통과/실패)
- [ ] 성능 측정(`time.perf_counter`, 크기별 10회 평균)과 N² 표
- [ ] 결과 리포트 10줄 이상(실패 원인 분석, O(N²) 근거)
- [ ] 모드 선택 메뉴(`main`)

## 10. 참고 자료

- 코디세이 미션3 문서, 개념 가이드 「MAC 연산과 NPU의 이해」, 해결 가이드 「Mini NPU Simulator 개발」
- 다른 교육생이 공유한 예시 README의 목차 구성(문서 구조만 참고했고, 내용과 측정값은 내 실행 결과로 작성함)

## 11. 결과 리포트
연산 횟수는 크기에 따라 N²으로 늘어나는데, 실측 시간은 그보다 완만하게 늘었다.
동점 3건의 경우 수학적으로는 같은 점수인데, 소수 계산을 N²번 누적하면서 1e-15 수준의 오차가 생김.
epsilon(1e-9)보다 훨씬 작아서 동점으로 처리되고, 정답은 Cross나 X로 하나 정해져 있으므로 FAIL. 여기서 중요한 점은, ==로 비교했다면 오차 때문에 가짜 승자가 나왔을 거라는 것이다. 
: epsilon이 필요한 근거
```powershell
[size_5_1] FAIL
  Cross=0.9  X=0.8999999999999999  판정=UNDECIDED  expected=X
  사유: 동점(UNDECIDED)
[size_5_2] PASS
  Cross=8.9  X=0.1  판정=Cross  expected=Cross
[size_13_1] PASS
  Cross=0.3  X=14.700000000000008  판정=X  expected=X
[size_13_2] FAIL
  Cross=7.499999999999997  X=7.5  판정=UNDECIDED  expected=Cross
  사유: 동점(UNDECIDED)
[size_25_1] FAIL
  Cross=4.9  X=4.899999999999999  판정=UNDECIDED  expected=X
  사유: 동점(UNDECIDED)
[size_25_2] PASS
  Cross=52.9  X=0.1  판정=Cross  expected=Cross
------------------------------
총 6개 / 통과 3개 / 실패 3개
실패 케이스:
  - size_5_1: 동점(UNDECIDED)
  - size_13_2: 동점(UNDECIDED)
  - size_25_1: 동점(UNDECIDED)

[성능 분석] (각 크기 10회 반복 평균)
크기(N×N)          평균 시간(ms)       연산 횟수(N²)
3x3                 0.0018               9
5x5                 0.0026              25
13x13               0.0130             169
25x25               0.0444             625
```
## 12. 커밋 기록
(git log --oneline)
- 11/17
b18cfb0 (HEAD -> main, origin/main) Docs: 미션 3 README 초안 작성
9d8a808 Feat: MAC 연산, 모드 1 입력 검증과 판정 구현

- 11/18
* 470c6fb (origin/feat/mode2) Feat: 미완
* 584a2de Feat: 케이스 키 크기 추출과 정사각형 검증
| * 42c2e2a (HEAD -> main, origin/main, origin/HEAD) Feat: 라벨 정규화 구현
|/
* b18cfb0 Docs: 미션 3 README 초안 작성
* 9d8a808 Feat: MAC 연산, 모드 1 입력 검증과 판정 구현