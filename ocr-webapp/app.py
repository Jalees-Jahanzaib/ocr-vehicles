from flask import Flask, render_template, redirect, url_for, request, flash
import requests
import json
import os
from werkzeug.utils import secure_filename
import cv2 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/'
file_process = ''

def ocr_vehicle(filename):
    url = "https://cloud.eyedea.cz/api/v2/cardetect.json"

    payload = {'email': 'rohan27bhandari@outlook.com',
    'password': '1199efa85',
    'Content-type': 'image/jpeg'}
    files = [
    ('upload', open(filename, 'rb'))
    ]
    headers= {}

    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    json_data =  json.loads(response.text.encode('utf8'))
    message = None
    try:
        message = 'License Plate(s) detected: '
        initial_str = message
        for car in json_data['photos'][0]['tags']:
            message += car['lp_text_content'] + ', '
        if message == initial_str:
            return ''
        message = message[:-2]
    except:
        message = ''
    return message

def process_frames(filename):
    try: 
        cam = cv2.VideoCapture(filename)
        if not os.path.exists('data'): 
            os.makedirs('data') 
    except OSError: 
        print ('Error: Creating directory of data')
    currentframe = 0
    while(True):
        ret, frame = cam.read()
        if ret:
            if currentframe % 24 == 0:
                name = 'frame' + str(currentframe) + '.jpg'
                print ('Creating...' + name)
                cv2.imwrite(name, frame)
                message = ocr_vehicle(name)
                os.remove(name)
                if len(message) > 0:
                    return message
            currentframe += 1
        else: 
            break 
    cam.release() 
    cv2.destroyAllWindows()
    return ''

@app.route('/', methods=['GET','POST'])
def home():
    global file_process
    if request.method == 'POST':
      f = request.files['file']
      filename = app.config['UPLOAD_FOLDER'] + secure_filename(f.filename)
      f.save(filename)
      file_process = filename
      return redirect(url_for('uploaded'))
    return render_template('index.html')

@app.route('/uploaded', methods=['GET','POST'])
def uploaded():
    global file_process
    alert_message = process_frames(file_process)
    video_file = file_process
    print(alert_message)
    if alert_message != '':
        return render_template('uploaded.html', msg=alert_message, video=video_file)
    return render_template('uploaded.html', video=file_process, error='License plate not found')

if __name__ == "__main__":
    app.run(debug=True)    
