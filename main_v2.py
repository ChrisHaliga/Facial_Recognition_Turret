import face_recognition as fr
import cv2
import serial


def compare(known, unknown):
    same = fr.compare_faces([known], unknown)

    if same[0]:
        return True

    return False

def main():
    cameras = []
    for x in range(10):
        cam = cv2.VideoCapture(x)
        if cam is None or not cam.isOpened():
            cam.release()
        else:
            cameras.append(cam)
    views = len(cameras)
    current_view = 0

    goodguys = []
    badguys = []
    ser = serial.Serial("COM3", 9600)  # open serial port that Arduino is using
    while True:
        ret, feed = cameras[0].read()
        f_h, f_w, channels = feed.shape
        ch = cv2.waitKey(1)
        if ch == ord('q') or ch == 27:
            break
        if ch == ord('d'):
            goodguys = []
            badguys = []
        if ch == 32:
            goodguys = []
            badguys = []
            known = fr.load_image_file('./img/known/me.jpg')
            known = fr.face_encodings(known)[0]

            faces = fr.face_locations(feed)
            for (top, right, bottom, left) in faces:
                t = top - 25
                if t < 0:
                    t = 0
                r = right + 25
                if r > f_w:
                    t = f_w
                b = bottom + 25
                if t > f_h:
                    t = f_h
                l = left - 25
                if t < 0:
                    t = 0

                img = feed[t:b, l:r]     
                face = fr.face_encodings(img)
                if len(face) > 0:
                    face = face[0]
                    x = str(round(90*(((left + right) / 2 - f_w / 2))/f_w))
                    y = str(round(90*(((top + bottom) / 2 - f_h / 2))/f_h))
                    if compare(known, face):
                        goodguys.append((left, top, right, bottom))
                    else:
                        badguys.append((left, top, right, bottom))
                    ser.write((x + "," + y + ";").encode())
                    print((x + "," + y + ";"))


        for (left, top, right, bottom) in goodguys:
            feed = cv2.rectangle(feed, (left, top), (right, bottom), (0, 255, 0), 2)
        for (left, top, right, bottom) in badguys:
            feed = cv2.rectangle(feed, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.imshow("Camera", feed)
        #ser.read()
    ser.close()
    for cam in cameras:
        cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()