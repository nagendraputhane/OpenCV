from __future__ import division
import cv2
from matplotlib import pyplot as plt
import numpy as np
from math import cos, sin

green = (0, 255, 0)

def show(image):
    #figure size in inches
    plt.figure(figsize=(10, 10))
    #show image with nearest neighbour interpolation
    plt.imshow(image, interpolation = 'nearest')

def overlay_mask(mask, image):
    #make the mask rgb
    rgb_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    #calculate the weighted sum of two arrays
    img = cv2.addWeighted(rgb_mask, 0.5, image, 0.5, 0)
    return img

def find_biggest_contour(image):
    #copy of the image as findContour function modifies the source image
    image = image.copy()
    # Contours can be explained simply as a curve joining all the continous points having the same color or intensity
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #isolate largest contour (area)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = max(contour_sizes, key = lambda x: x[0])[1]
    #draw it filled in
    mask  = np.zeros(image.shape, np.uint8)
    cv2.drawContours(mask, [biggest_contour], -1, 255, -1)
    return biggest_contour, mask

def circle_contour(image, contour):
    #bounding elllipse
    image_with_ellipse = image.copy()
    ellipse = cv2.fitEllipse(contour)
    #add it
    cv2.ellipse(image_with_ellipse, ellipse, green, 2, cv2.LINE_AA)
    return image_with_ellipse

def find_strawberry(image):

    # Convert color scheme to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Make a consistent size
    #get largest dimension
    max_dimension = max(image.shape)
    #scale our image (square)
    scale = 700/max_dimension
    image = cv2.resize(image, None, fx=scale, fy=scale)

    # Gaussian filter
    image_blur = cv2.GaussianBlur(image, (7,7), 0)

    # Convert to HSV scheme
    image_blur_hsv = cv2.cvtColor(image_blur, cv2.COLOR_RGB2HSV)

    # 0-10 hue, 100+ saturation, 80+ value
    min_red = np.array([0, 100, 80])
    max_red = np.array([10, 256, 256])
    mask1 = cv2.inRange(image_blur_hsv, min_red, max_red)

    # 170-180 hue, 100+ saturation, 80+ value
    min_red2 = np.array([170, 100, 80])
    max_red2 = np.array([180, 256, 256])
    #layer
    mask2 = cv2.inRange(image_blur_hsv, min_red2, max_red2)

    # Combine masks
    mask = mask1 + mask2

    # Elliptical kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    #opening: erosion followed by dilation - removing noise
    #closing: dilation followed by erosion - closing small holes
    mask_closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask_clean = cv2.morphologyEx(mask_closed, cv2.MORPH_OPEN, kernel)

    # Find biggest strawberry
    #get back list of segmented strawberries and an outline for the biggest one
    big_strawberry_contour, mask_strawberries = find_biggest_contour(mask_clean)

    # Overlay the mask
    overlay = overlay_mask(mask_clean, image)

    # Circle biggest strawberry
    circled = circle_contour(overlay, big_strawberry_contour)
    show(circled)

    bgr = cv2.cvtColor(circled, cv2.COLOR_RGB2BGR)
    return bgr

image = cv2.imread('berry.jpg')
result = find_strawberry(image)
cv2.imwrite('berry_detect.jpg', result)
