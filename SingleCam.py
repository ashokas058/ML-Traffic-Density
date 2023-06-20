
from ast import While
from os import stat
from unittest import result
from cv2 import pointPolygonTest
from flask import Flask, render_template, Response,request
import cv2
import datetime
import time
from vidgear.gears import VideoGear
from cv2 import CV_32F
from cv2 import polylines
import numpy as np
from vehicle_detector import  VehicleDetector
from tracker import *
import mysql.connector
tracker = EuclideanDistTracker()
vd=VehicleDetector()
streamSourceLst=[]
streamList=[]
globalStream1Count=0
globalStream2Count=0
globalStream3=0

app = Flask(__name__)


def get_current_date():
    current_date = datetime.date.today()
    return current_date

# for local webcam use cv2.VideoCapture(0) as soruce= (below stream1 code line)

def gen_frames(tfCount):
    if(int(tfCount)==3):

       stream1 = VideoGear(source="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4", logging=True).start()

       #below one for live came ,change the index for accessing multiple/switching
       #stream1 = VideoGear(source=0, logging=True, apiPreference=cv2.CAP_ANY).start()     
       stCnt1=0
       prev = 0
       frame_rate=60
       while True:
            time_elapsed = time.time() - prev
            if time_elapsed > 1./frame_rate:
                prev = time.time()
                frameA = stream1.read()
                if frameA is None:
                    stream1.stop()
                    gen_frames()

                frameA,globalStream1Count=processedFrame(vd.detect_vehicles(frameA),frameA)
                print("Camera 1========>>>"+str(globalStream1Count))
                frameA=cv2.resize(frameA,(640,340),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                cv2.putText(frameA, "Total Vehicle count: " + str(globalStream1Count), (20, frameA.shape[0] - 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                cv2.putText(frameA, str(get_current_date()), (20, frameA.shape[0] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                ret, buffer = cv2.imencode('.jpg',frameA)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    tfCount=3
    return Response(gen_frames(tfCount), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def detectVehicle(stream):
    if stream is None:
        return

def processedFrame(bbox,frame):
    detect=[]
    cnt=len(bbox)
    for box in bbox:
         x,y,w,h=box
         detect.append([x,y,w,h])
    boxes_ids = tracker.update(detect)
    for box_id in boxes_ids:
        x, y, w, h, id = box_id
        cv2.rectangle(frame, (x, y), (x+w, y+h), (10, 220, 20), 3)
        cv2.putText(frame, "ID"+str(id), (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    return frame,cnt

def concatFrame(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

def checkRg(sc,fram):
    pts=np.array([sc])
    inside=cv2.pointPolygonTest(pts,(int(fram[0]),int(fram[3])),False)
    return inside

if __name__ == '__main__':
    app.run(host='0.0.0.0')


# def getMysql():
#     mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     port=3307,
#     database='scm'
#     ,auth_plugin='mysql_native_password'
#     )
#     return mydb.cursor(prepared=True)

# def getIpCamSource(stationId):
#     mycursor =getMysql()
#     sql="""SELECT * FROM tbl_ipCam WHERE stationId=%s"""
#     tup=(stationId)
#     mycursor.execute(sql,tup)
#     result=mycursor.fetchall()
#     mycursor.commit()
#     for x in result:
#         streamSourceLst.append(x)
# def memoryController(status):
#     mycursor =getMysql()
#     sql="""SELECT shutdown FROM tbl_cameCtrl"""
#     mycursor.execute(sql)
#     result=mycursor.fetchall()
#     mycursor.commit()








