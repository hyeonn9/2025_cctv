let client = null;
let connectionFlag = false;
const CLIENT_ID = "client-"+Math.floor((1+Math.random())*0x10000000000).toString(16) // 클라이언트 ID 랜덤 생성

// MQTT 브로커에 연결하는 함수
function connect(host, port) {
    if(connectionFlag == true)
        return;

    console.log("연결 완료");
    client = new Paho.MQTT.Client(host, Number(port), CLIENT_ID); // 클라이언트 생성

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // 브로커 접속
    client.connect({
        onSuccess:onConnect,
    });
}

// 연결 성공시 토픽 구독하는 함수
function onConnect() {
    client.subscribe("camera/raw");
    client.subscribe("camera/human");

    client.subscribe("guest/visitor");
    client.subscribe("guest/intruder");
    connectionFlag = true;
}
// 연결이 끊겼을 때의 함수
function onConnectionLost(responseObject) {
    connectionFlag = false;
}

// 메세지가 도착했을 때의 함수
function onMessageArrived(msg) {
    // 카메라에서의 이미지 처리
    if(msg.destinationName.startsWith("camera/")){
        let bytes = msg.payloadBytes;
        // base64 인코딩
        let base64 = btoa(String.fromCharCode.apply(null, bytes));
        let imageData = "data:image/jpeg;base64," + base64;
    
        // 카메라 원본 이미지
        if(msg.destinationName == "camera/raw"){
            document.getElementById("raw").src = imageData;
        }
        // 사람 감지 이미지
        if(msg.destinationName == "camera/human"){
            document.getElementById("human").src = imageData;
        }
    }
    // 방문객,침입자 처리
    else {
        const count = parseInt(msg.payloadString); // 정수로 변환

        //방문자 그래프
        if (msg.destinationName === "guest/visitor") {
            addChartData('visitor', count); 
        } 
        // 침입자 그래프
        else if (msg.destinationName === "guest/intruder") {
            addChartData('intruder', count);
        }
    }
}
