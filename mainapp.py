from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/') # /로 접속시 main.html 렌더링
def index():
        return render_template('main.html')
if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080, debug=True) # 외부 접속 허용, 8080 포트로 실행
