#입력값(mm)을 cm단위로 변환
def change_mm_to_cm(val:int)->int:
    pass

#object_val: (tof값, 윈도우 좌상단 좌표, 윈도우 우하단좌표, screen의 가로픽셀, screen의 세로픽셀)
#object_coor: (tof값, 물체의 가로길이,물체의 세로길이, 물체 중점의 가로좌표, 물체 중점의 세로좌표)
#입력값인 object_val을 드론을 원점으로 한 3차원 좌표인 coor로 변환
def chagne_val_to_coor(val:str, screen_width: int, screen_height: int)->tuple:
    pass

#입력값(cmd)를 tello sdk 명령으로 변환
def change_cmd_for_tello(cmd:str)->str:
    pass