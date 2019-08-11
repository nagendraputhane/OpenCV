import cv2
cam = cv2.VideoCapture(0)
while True:
    img = cam.read()[1]
    cv2.imshow("Window", img)
    if cv2.waitKey(5) == 32:
        break
