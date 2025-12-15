import time
import RPi.GPIO as GPIO
import subprocess

trig = 20 # 초음파 출력
echo = 16 # 초음파 입력
led = 6 # LED
button = 21 # 버튼 입력

# 초기화 함수
def sound_init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False) 

	GPIO.setup(trig, GPIO.OUT)
	GPIO.setup(echo, GPIO.IN)

	GPIO.setup(led, GPIO.OUT) 
	GPIO.setup(button, GPIO.IN, GPIO.PUD_DOWN) 

# 경고음 출력 함수
def play_alert():
    subprocess.Popen(["aplay", "./sounds/alert.wav"])
	
# 초인종 출력 함수
def play_doorbell():
    subprocess.Popen(["aplay", "./sounds/doorbell.wav"])

# 초음파 센서를 이용한 거리 측정 함수
def measureDistance():
	GPIO.output(trig, 1)
	time.sleep(0.00001)
	GPIO.output(trig, 0)
	
	# echo 핀이 high가 될때까지 대기
	while(GPIO.input(echo) == 0):
		pass
	pulse_start = time.time() # high가 된 시간 저장

	# echo 핀이 low가 될때까지 대기
	while(GPIO.input(echo) == 1):
		pass
	pulse_end = time.time() # low가 된 시간 저장

	pulse_duration = pulse_end - pulse_start
	return pulse_duration*340*100/2

# LED 제어 함수
def led_on_off(pin, value):
	GPIO.output(pin, value)

last_button_state = False # 버튼 계속 누르고 있는지의 여부 - 꾹 누르고 있어도 소리가 한번만 나도록 하기 위함
# 버튼 눌림 감지, LED, 사운드 처리
def pressButton():
	global last_button_state
    
	bell_triggerd = False # 이번 루프에 벨소리 출력 여부
	current_pressed = GPIO.input(button) # 현재 버튼 누르고 있음

	# 버튼을 눌렀을때
	if current_pressed and not last_button_state:
		led_on_off(led, True) # LED 켜기
		play_doorbell()        # 초인종 소리 재생
		bell_triggerd = True

	# 버튼에서 손을 뗐을 때
	elif not current_pressed and last_button_state:
		led_on_off(led, False) # LED 끄기

	last_button_state = current_pressed # 다음 루프에서 비교를 위해 상태 저장

	return bell_triggerd # 이번 루프에서 벨이 울렸는지 반환