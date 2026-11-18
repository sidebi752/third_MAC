import json

with open( "data.json", encoding="utf-8") as f:
    data = json.load(f)

print(data["filters"].keys())  # size_5, size_13, size_25
# print(len(data["filters"]["size_5"]["cross"]))  # 5가 나오면 정상
# print(data["patterns"]["size_5_1"]["expected"])  # X

def mac(pattern, filt):
    total = 0
    n= len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total

cross = [[0,1,0],[1,1,1],[0,1,0]]
x = [[1,0,1],[0,1,0],[1,0,1]]
# print(mac(cross, cross))
# print(mac(cross, x))

def read_row(n=3):
    line = input("숫자 입력: ")
    parts = line.split()

    if len(parts) != n:
        print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
        return None

    try:
        row = [float(p) for p in parts]
    except ValueError:
        print(f"입력 형식 오류: 각 줄에 {n}개의 숫자만 입력하세요.")
        return None
    return row

def read_matrix(name, n=3):
    print(f"{name} ({n}줄 입력, 공백 구분)")
    rows = []
    for i in range(n):
        while True:
            row = read_row(n)
            if row is not None:
                break
        rows.append(row)
    return rows

EPSILON = 1e-9    # 허용오차. 이 값보다 차이가 작으면 같다고 본다

def normalize_label(raw):
    key = str(raw).strip().lower()     # strip()은 글자 앞뒤의 공백을 지우고, lower()는 영문을 소문자로 바꿉니다. str(raw)는 무엇이 들어와도 일단 문자열로 바꿔서 에러를 막습니다.
    if key in ("+", "cross"):
        return "Cross"                     
    if key in ("x",):
        return "X"
    return None                        # 모르는 라벨은 None
    

def mode1():
    a = read_matrix("필터 A")
    b = read_matrix("필터 B")
    p = read_matrix("패턴")

    score_a = mac(p, a)
    score_b = mac(p, b)

    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("판정:", judge(score_a, score_b))

def parse_size_from_key(key):
    parts = key.split("_")      # "size_13_2" -> ["size", "13", "2"]
    if len(parts) < 2 or parts[0] != "size":
        return None
    try: 
        return int(parts[1])
    except ValueError:
        return None

def is_square(matrix, n):
    if len(matrix) != n:
        return False
    for row in matrix:
        if len(row) != n:
            return False
    return True

def judge(a, b, la="A", lb="B"):
    if abs(a - b) < EPSILON:
        return "UNDECIDED"
    if a > b:
        return la
    return lb

def analyze_case(case_id, case, filters):
    n = parse_size_from_key(case_id)
    if n is None:
        return {"id": case_id, "status": "FAIL", "reason": "케이스 키 형식 오류"}

    pattern = case["input"]
    if not is_square(pattern, n):
        return {"id": case_id, "status": "FAIL", "reason": "패턴 크기 불일치"}

    group = filters.get(f"size_{n}")
    if group is None:
        return {"id": case_id, "status": "FAIL", "reason": "해당 크기 필터 없음"}

    fs = {}                                    # 정규화된 키로 다시 담을 딕셔너리
    for k, v in group.items():
        fs[normalize_label(k)] = v             # "cross" → "Cross", "x" → "X"
    if "Cross" not in fs or "X" not in fs:
        return {"id": case_id, "status": "FAIL", "reason": "Cross/X 필터 누락"}

    score_cross = mac(pattern, fs["Cross"])
    score_x = mac(pattern, fs["X"])
    verdict = judge(score_cross, score_x, "Cross", "X")

    expected = normalize_label(case["expected"])
    if expected is None:
        return {"id": case_id, "status": "FAIL", "reason": "알 수 없는 expected 라벨"}

    if verdict == expected:
        status, reason = "PASS", ""
    elif verdict == "UNDECIDED":
        status, reason = "FAIL", "동점(UNDECIDED)"
    else:
        status, reason = "FAIL", "판정과 expected 불일치"

    return {"id": case_id, "status": status, "reason": reason,
            "cross": score_cross, "x": score_x,
            "verdict": verdict, "expected": expected}

for case_id, case in data["patterns"].items():
    r = analyze_case(case_id, case, data["filters"])
    print(r["id"], r["status"], r["verdict"], r["expected"], r["reason"])

mode1()
