#입력값이 Tello ToF 범위(0~8192)의 값이 맞는지 확인
def is_tof_val(val:str)->bool:
    pass

#입력값이 Tello SDK가 맞는지 확인
def is_sdk_val(val:str)->bool:
    """
    Tello SDK 명령어의 첫 어절에는 숫자가 없음
    """
    first_part:str = val.split()[0]

    for char in first_part:
        if char.isdigit():
            print("[is_sdk_val] val에서 숫자가 감지되었습니다.")
            return False
    return True

#입력값이 충돌이 일어나지 않는지 확인
def is_safe_cmd(val:str, threshold:int)->bool:
    pass