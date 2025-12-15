let ctx = null;
let chart = null;
let config = {
	type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: '방문객',
                data: [],
                borderColor: 'rgb(54, 162, 235, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointStyle: 'circle', // 원 모양
                pointRadius: 6,
                pointBorderWidth: 2
            },
            {
                label: '침입자',
                data: [],
                borderColor: 'rgb(255, 99, 132, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointStyle: 'rectRot', // 마름모 모양
                pointRadius: 6,
                pointBorderWidth: 2
            }
        ]
    },
    options: {
        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } // y축이 0부터 시작하고 1씩 증가
    }
};

let tick = 0; 
const MAX_DATA_LENGTH = 15; //15개 데이터만 유지

function drawChart() {
	ctx = document.getElementById('canvas').getContext('2d');
	chart = new Chart(ctx, config);
} 

// 현재 시간을 HH:MM 형식으로 반환하는 함수
function getCurrentTimeLabel() {
    const now = new Date();

    const h = String(now.getHours()).padStart(2, '0'); // 2자리 숫자 유지
    const m = String(now.getMinutes()).padStart(2, '0');
    
    return `${h}:${m}`;
}

function addChartData(type, value) {
	const timeLabel = getCurrentTimeLabel(); 
    const dataLength = chart.data.labels.length;
    
    // 가장 마지막에 기록된 시간 라벨
    const lastLabel = dataLength > 0 ? chart.data.labels[dataLength - 1] : null;

    // 같은 시간 라벨이 있을 경우, 거기에 카운트 증가
    if (timeLabel === lastLabel) {
        const lastIndex = dataLength - 1;
        
        if (type === 'visitor') {
            chart.data.datasets[0].data[lastIndex] += 1;
        } else {
            chart.data.datasets[1].data[lastIndex] += 1;
        }
    
    } else { // 새로운 시간 라벨인 경우, 새로운 데이터로 추가
        chart.data.labels.push(timeLabel); // 새로운 데이터 라벨 추가
        
        if (type === 'visitor') {
            chart.data.datasets[0].data.push(1); 
            chart.data.datasets[1].data.push(0); 
        } else {
            chart.data.datasets[0].data.push(0); 
            chart.data.datasets[1].data.push(1); 
        }

        // 데이터가 15개를 넘으면 가장 오래된 데이터 삭제
        if (chart.data.labels.length > MAX_DATA_LENGTH) {
            chart.data.labels.shift(); 
            chart.data.datasets[0].data.shift(); 
            chart.data.datasets[1].data.shift(); 
        }
    }

    chart.update(); //그래프 업데이트
}
