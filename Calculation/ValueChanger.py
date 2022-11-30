#입력값(mm)을 cm단위로 변환
def change_mm_to_cm(val:int)->int:
    pass


def chagne_val_to_coor(val:str, screen_width: int, screen_height: int)->tuple:
    """
    입력값 - object_val: (tof값[cm], 윈도우 좌상단 좌표[px], 윈도우 우하단좌표[px], screen의 가로픽셀[px], screen의 세로픽셀[px])
    리턴값 - object_coor: (tof값[cm], 물체중심의 가로좌표[cm], 물체중심의 세로좌표[cm], 물체의 가로길이[cm], 물체의 세로길이[cm])
    #입력값인 object_val을 드론을 원점으로 한 3차원 좌표인 object_coor로 변환하여 리턴
    """
    pass

#입력값(cmd)를 tello sdk 명령으로 변환
def change_cmd_for_tello(cmd:str)->str:
    pass