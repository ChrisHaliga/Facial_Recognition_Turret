import face_recognition as fr
import cv2
import serial

import _thread
import time

TOLERANCE = 50
known = [fr.face_encodings(fr.load_image_file('./img/known/MorganFreeman.jpg'))[0]]
queue = ""
reset = False
ser = serial.Serial("COM3", 9600)
connected = True

# The Arduino couldn't handle the entourage of coordinates - This lowers the rate, but maintains the accuracy
def servo_loop():
    global queue
    global reset
    global ser
    global connected
    print("Thread Created")
    while connected:
        time.sleep(1.5)
        if queue != "":
            print("sending: {}".format(queue))
            ser.write(queue.encode())
            queue = ""
        elif reset:
            ser.write("181,181;".encode())
            reset = False
    ser.close()


def compare(known, unknown):
    same = fr.compare_faces([known], unknown)
    if same[0]:
        return True
    return False


def findTarget(feed, faces):
    print("evaluating faces")
    f_h, f_w, channels = feed.shape
    for face in faces:
        (x, y, w, h) = face
        x -= 20
        y -= 20
        w += 20
        h += 20
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if w > f_w:
            w = f_w
        if h > f_h:
            h = f_h

        img = feed[y:y + h, x:x + w]
        eface = fr.face_encodings(img)
        if len(eface) > 0:
            eface = eface[0]
            bad = True
            for safe in known:
                if bad and compare(safe, eface):
                    bad = False
                    cv2.rectangle(feed, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print("not a target")
            if bad:
                print("target acquired")
                return face


def main():
    global queue
    global connected
    global reset
    connected = True
    try:
        _thread.start_new_thread(servo_loop, ())
    except:
        print("Error: unable to start thread")
        connected = False
    cameras = []
    for x in range(10):
        cam = cv2.VideoCapture(x)
        if cam is None or not cam.isOpened():
            cam.release()
        else:
            cameras.append(cam)

    target = None
    time_missing = 0
    while True:
        ret, feed = cameras[0].read()
        f_h, f_w, channels = feed.shape
        ch = cv2.waitKey(1)
        if ch == ord('q') or ch == 27:
            break
        gray = cv2.cvtColor(feed, cv2.COLOR_BGR2GRAY)
        path = "haarcascade_frontalface_default.xml"

        face_cascade = cv2.CascadeClassifier(path)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.10, minNeighbors=5, minSize=(70, 70))

        found = False
        if target is not None:
            if len(faces) >= 1:
                target = faces[0]
                found = True
            else:
                time_missing += 1
        elif len(faces) >= 1:
            target = findTarget(feed, faces)
            if target is not None:
                found = True

        if found:
            time_missing = 0
            (x, y, w, h) = target
            x_out = str(int(15 + round(90 * (((x + x+w)/2 - f_w/2)) / f_w)))
            y_out = str(int(20+-1*round(90 * (((y + y+h)/2 - f_h/2)) / f_h)))
            queue = (x_out + "," + y_out + ";")
            print((x_out + "," + y_out + ";"))
            cv2.rectangle(feed, (x, y), (x + w, y + h), (0, 0, 255), 2)
        elif time_missing > 20:
            reset = True
            target = None
            time_missing = 0
        cv2.imshow("Camera", feed)
    connected = False
    for cam in cameras:
        cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()