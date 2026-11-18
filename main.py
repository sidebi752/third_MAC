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

def judge(a, b):
    if abs(a - b) < EPSILON:
        return "UNDECIDED"      # 동점
    if a > b:
        return "A"
    return "B"

def normalize_label(raw):
    key = str(raw).strip().lower()     # strip()은 글자 앞뒤의 공백을 지우고, lower()는 영문을 소문자로 바꿉니다. str(raw)는 무엇이 들어와도 일단 문자열로 바꿔서 에러를 막습니다.
    if key in ("+", "cross"):
        return "cross"                     
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

mode1()
