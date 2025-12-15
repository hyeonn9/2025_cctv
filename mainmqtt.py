import time
import paho.mqtt.client as mqtt
import cv2
import camera
import light
import sound

camera.init_camera() # 카메라 초기화
camera.init_model() # 텐서플로 라이트 모델 초기화
sound.sound_init() # 초음파 초기화

# mqtt 브로커 설정
ip = "localhost"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(ip, 1883) # 브로커의 1883 포트에 연결
client.loop_start() # 메시지 루프 시작

# mqtt로 이미지 전송하는 함수 
def send_jpg(topic, frame):
    ret, jpeg = cv2.imencode(".jpg", frame)
    if ret:
        client.publish(topic, jpeg.tobytes())

intrusion_start = None # 사람이 앞에 서있기 시작한 시간
distance_end = 50 # 초음파 거리 임계값

is_guest = False # 손님이 온 경우 (버튼을 누르면 true)
ctn_visitor = 0  # 손님 방문 횟수
ctn_intruder = 0 # 침입자 방문 횟수

try:
    while True:
        rawImage = camera.take_picture(most_recent=True) # 사진 찍기
        rawImage = light.adjust_light(rawImage) # 밝기 보정 

        if rawImage is not None:
            rawImage = cv2.resize(rawImage, (480, 320)) # 이미지 크기 축소
            
            # 사람 감지 수행
            detectedImage, is_human = camera.detect_human(rawImage)

            # 원본 전송
            send_jpg("camera/raw", rawImage)
        
            # 텐서플로 라이트 모델을 사용한 이미지 전송
            if detectedImage is not None: # 사람이 감지된 경우
                send_jpg("camera/human", detectedImage) # 초록 네모 박스가 그려진 이미지 전송
            else: # 사람이 감지 안 된 경우
                send_jpg("camera/human", rawImage) # 없으면 원본 전송

        dist = sound.measureDistance() # 초음파 거리
        human_close = dist < distance_end # 일정 거리 이내에 사람이 있는지 판별
        
        # 버튼 누르면 손님으로 처리
        if sound.pressButton():
            is_guest = True 
            ctn_visitor+=1
            client.publish("guest/visitor", str(ctn_visitor))
            intrusion_start = None # 침입자 타이머 초기화

        # 가까이 있음 && 사람임: 침입자 감지 로직
        if human_close and is_human:
            if is_guest: 
                pass # 손님이면 넘어가기
            else:
                # 처음 감지됨
                if intrusion_start is None: 
                    intrusion_start = time.time() # 처음 감지된 시점 저장

                else:
                    # 10초 동안 앞에 있을 경우 침입자로 간주
                    if time.time() - intrusion_start >= 10:
                        sound.play_alert() # 경고음 발생
                        ctn_intruder+=1
                        client.publish("guest/intruder", str(ctn_intruder))

                        intrusion_start = time.time() # 다음 침입자 체크를 위해 타이머 초기화
        else: 
            # 멀어지면 초기화
            is_guest = False
            intrusion_start = None

except KeyboardInterrupt:
    pass

finally:
    camera.final() # cv2 객체 반환
    client.loop_stop() # 메시지 루프를 실행하는 스레드 종료
    client.disconnect() # 브로커와 연결 종료