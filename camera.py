import cv2
import numpy as np
# 텐서플로 라이트 런타임
from tflite_runtime.interpreter import Interpreter

camera = None

# 카메라 초기화
def init_camera(camera_id=0, width=640, height=480, buffer_size=1):
        global camera
        camera = cv2.VideoCapture(camera_id, cv2.CAP_V4L)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

# 사진 촬영 함수
def take_picture(most_recent=False):
        global camera
        
        # most_recent가 True이면 가장 오래된 프레임을 버려서 최신 프레임만 사용
        len = 0 if most_recent == False else camera.get(cv2.CAP_PROP_BUFFERSIZE)
        
        while(len > 0):
                camera.grab( ) # 버퍼에 저장된 프레임 버리기
                len -= 1
        success, image = camera.read( ) # 최신 프레임 읽기

        if not success:
                return None
        
        return image # 이미지 반환

# 텐서플로 라이트 관련 전역 변수
interpreter = None
input_details = None
output_details = None

# 모델 초기화
def init_model(model_path="model/detect.tflite"):
        global interpreter, input_details, output_details
    
        interpreter = Interpreter(model_path=model_path) # model/detect.tflite를 불러와 인터프리터 객체 생성
        interpreter.allocate_tensors() # 텐서 메모리 할당

        # 모델 입출력 텐서 정보 가져옴
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

# 사람 감지 함수
def detect_human(frame):
        global interpreter, input_details, output_details

        # 이미지 없으면 false 반환
        if frame is None:
                return False

        # 1. 전처리
        input_h = input_details[0]['shape'][1] # 모델 입력 높이
        input_w = input_details[0]['shape'][2] # 모델 입력 너비

        img = cv2.resize(frame, (input_w, input_h)) # 모델 입력 크기에 맞게 리사이즈
        img = img.astype(np.uint8) # uint8 형식으로 변환
        img = np.expand_dims(img, axis=0) # 배치 차원 추가

        # 2. 추론
        interpreter.set_tensor(input_details[0]['index'], img) # 전처리된 이미지를 모델 입력 텐서에 설정
        
        interpreter.invoke() # 객체 감지 수행

        # 3. 결과 해석
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # output_details[0]: 감지된 박스 좌표 리스트
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # output_details[1]: 감지된 객체 클래스, 0번: Person(사람)
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # output_details[2]: 정확도 점수 

        # 4. 결과 보여주기(시각화)
        detected_frame  = frame.copy() #원본 프레임 복사
        is_human = False # 사람 감지 여부

        for i in range(len(scores)):
                if classes[i] != 0: # 클래스 0(사람)이 아니면 무시
                        continue
                if scores[i] < 0.5: # 신뢰도 0.5 미만이면 무시
                        continue

                is_human = True # 조건 만족시 사람으로 판단
                
                ymin, xmin, ymax, xmax = boxes[i] # 좌표 정보 가져오기
                
                # 좌표를 실제 이미지 크기로 변환
                xmin = int(xmin * frame.shape[1])
                xmax = int(xmax * frame.shape[1])
                ymin = int(ymin * frame.shape[0])
                ymax = int(ymax * frame.shape[0])

                # 박스 그리기
                cv2.rectangle(detected_frame , (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                cv2.putText(detected_frame , f"{int(scores[i]*100)}%",
                                (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        return detected_frame, is_human # 감지 표시된 이미지, 사람 감지 여부 반환

# 카메라 종료
def final( ):
        global camera
        if camera != None:
                camera.release( )
        camera = None