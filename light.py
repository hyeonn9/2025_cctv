import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import cv2
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# MCP3008 객체 생성
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

# 자동 밝기 조절 함수
def adjust_light(frame):
    if frame is None:
        return None

    light_value = mcp.read_adc(0) # 조도 센서 값 읽기

    if light_value < 10: # 조도 센서 값이 10보다 낮은 경우
        frame = adjust_gamma(frame, 1.2) # 감마 보정

    return frame

# 감마 보정 함수
def adjust_gamma(frame, gamma):
    inv_gamma = 1.0 / gamma # 감마 역수 계산

    # 감마 보정용 테이블
    table = np.array([(i / 255.0) ** inv_gamma * 255 
                      for i in range(256)]).astype("uint8")
    
    return cv2.LUT(frame, table) # 프레임에 감마 변환 적용 후 반환