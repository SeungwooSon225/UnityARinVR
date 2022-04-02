import cv2.aruco as aruco
import os
import numpy as np
import cv2
import glob
import argparse
import socket
import time

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def calibrate(dirpath, prefix, image_format, square_size, width=9, height=6):
    """ Apply camera calibration operation for images in the given directory path. """
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    objp = np.zeros((height*width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    # objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    if dirpath[-1:] == '/':
        dirpath = dirpath[:-1]

    images = glob.glob(dirpath+'/' + prefix + '*.' + image_format)

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (width, height), corners2, ret)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return [ret, mtx, dist, rvecs, tvecs]


def findArucoMarkers(img, mtx, dist, markerSize=6, totalMarkers=250, draw=True):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()

    bboxs, ids, rejected = aruco.detectMarkers(imgGray, arucoDict, parameters=arucoParam)


    if np.all(ids is not None):  # If there are markers found by detector
        for i in range(0, len(ids)):  # Iterate in markers
            # Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
            rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(bboxs[i], 0.02, mtx, dist)
            (rvec - tvec).any()  # get rid of that nasty numpy value array error

            aruco.drawDetectedMarkers(img, bboxs)  # Draw A square around the markers
            aruco.drawAxis(img, mtx, dist, rvec, tvec, 0.01)  # Draw Axis

            return rvec, tvec, bboxs

    return None, None, None



host, port = "127.0.0.1", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

ret, mtx, dist, rv, tv = calibrate('./calibration', 'calibration', 'png', 12)

while True:
    receivedData = sock.recv(1024).decode("UTF-8")  # receiveing data in Byte fron C#, and converting it to String
    print(receivedData)
    img = cv2.imread("./img.png")

    img = cv2.flip(img, 1)

    rvec, tvec, bbox = findArucoMarkers(img, mtx, dist)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    data = " "
    print()
    if rvec is not None:
        data = str(1920-sum(bbox[0][0].T[0])/4) + " " + str(1080 - sum(bbox[0][0].T[1])/4)
        print(data)
    sock.sendall(data.encode("UTF-8")) #Converting string to Byte, and sending it to C#





