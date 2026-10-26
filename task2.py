
import cv2 as cv
import numpy as np
import os

# folders for input pics and results
inputFolder = "test_images"
outputFolder = "output"

# load the road image
def loadImage(imagePath):
    roadImage = cv.imread(imagePath)
    return roadImage

#hsv color filtering keep only white and yellow
def filterColor(roadImage):
    hsvImage = cv.cvtColor(roadImage, cv.COLOR_BGR2HSV)
    # white means low saturation and very bright
    whiteMask = cv.inRange(hsvImage, np.array([0, 0, 215]), np.array([180, 25, 255]))
    # yellow is hue 15 to 35 and strongly colored so dry grass gets rejected
    yellowMask = cv.inRange(hsvImage, np.array([15, 130, 120]), np.array([35, 255, 255]))
    # join both masks then keep only those pixels from the real pic
    combinedMask = cv.bitwise_or(whiteMask, yellowMask)
    colorFiltered = cv.bitwise_and(roadImage, roadImage, mask=combinedMask)
    return colorFiltered

# gaussian blur to reduce noise
def applyGaussianBlur(colorFiltered):
    # canny wants gray so convert first
    grayImage = cv.cvtColor(colorFiltered, cv.COLOR_BGR2GRAY)
    gaussianBlur = cv.GaussianBlur(grayImage, (5, 5), 0)
    return gaussianBlur

#canny edge detection
def applyCannyEdge(gaussianBlur):
    # under 50 gets thrown away and over 150 is a sure edge
    cannyEdge = cv.Canny(gaussianBlur, 50, 150)
    return cannyEdge

#region of interest masking
def applyRoiMask(cannyEdge):
    # shape gives height first then width
    imageHeight, imageWidth = cannyEdge.shape
    # four corners of the trapezoid in front of the car
    roiPolygon = np.array([[
        (int(0.05 * imageWidth), imageHeight),
        (int(0.45 * imageWidth), int(0.62 * imageHeight)),
        (int(0.55 * imageWidth), int(0.62 * imageHeight)),
        (int(0.95 * imageWidth), imageHeight)
    ]], dtype=np.int32)
    # black canvas then paint the trapezoid white
    roiMask = np.zeros_like(cannyEdge)
    cv.fillPoly(roiMask, roiPolygon, 255)
    # keep edges only where the mask is white
    roiEdges = cv.bitwise_and(cannyEdge, roiMask)
    return roiEdges

# stacks the steps into one pic for the readme
def makeComparison(roadImage, colorFiltered, cannyEdge, roiEdges):
    # edge pics have one channel so make them 3 channel to stack
    cannyBgr = cv.cvtColor(cannyEdge, cv.COLOR_GRAY2BGR)
    roiBgr = cv.cvtColor(roiEdges, cv.COLOR_GRAY2BGR)
    topRow = np.hstack([roadImage, colorFiltered])
    bottomRow = np.hstack([cannyBgr, roiBgr])
    comparisonGrid = np.vstack([topRow, bottomRow])
    return comparisonGrid

def main():
    os.makedirs(outputFolder, exist_ok=True)
    for fileName in os.listdir(inputFolder):
        if not fileName.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        roadImage = loadImage(os.path.join(inputFolder, fileName))
        if roadImage is None:
            print("could not read", fileName)
            continue
        # run in order
        colorFiltered = filterColor(roadImage)
        gaussianBlur = applyGaussianBlur(colorFiltered)
        cannyEdge = applyCannyEdge(gaussianBlur)
        roiEdges = applyRoiMask(cannyEdge)
        # save the final edges and the 2x2 steps pic
        baseName = os.path.splitext(fileName)[0]
        comparisonGrid = makeComparison(roadImage, colorFiltered, cannyEdge, roiEdges)
        cv.imwrite(os.path.join(outputFolder, baseName + "_result.png"), roiEdges)
        cv.imwrite(os.path.join(outputFolder, baseName + "_steps.png"), comparisonGrid)
        print("done:", fileName)

if __name__ == "__main__":
    main()

    #fixes
    # changed saturation at most 25, brightness at least 215 so the sky haze is rejected
    # yellow at least 130 to reject grass which is light.
    # adjusted roi top so the sky isnt covered. 

'''
overlayImage = drawLanes(roadImage, roiEdges)
    cv.imwrite(os.path.join(outputFolder, baseName + "_lanes.png"), overlayImage)

def drawLanes(roadImage, roiEdges):
    # find short straight pieces in the edge pic
    houghLines = cv.HoughLinesP(roiEdges, 1, np.pi / 180, 30, minLineLength=40, maxLineGap=100)
    if houghLines is None:
        return roadImage.copy()
    imageHeight = roadImage.shape[0]
    topY = int(0.62 * imageHeight)
    leftLines, rightLines = [], []
    laneImage = np.zeros_like(roadImage)
    # every row is x1 y1 x2 y2
    for x1, y1, x2, y2 in houghLines.reshape(-1, 4):
        if x1 == x2:
            continue
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        # flat pieces are not lanes
        if abs(slope) < 0.4:
            continue
        # y goes down so left lane has negative slope
        if slope < 0:
            leftLines.append((slope, intercept))
        else:
            rightLines.append((slope, intercept))
    for sideLines in (leftLines, rightLines):
        if len(sideLines) == 0:
            continue
        averageSlope = np.mean([line[0] for line in sideLines])
        averageIntercept = np.mean([line[1] for line in sideLines])
        # from y = m x + b we get x = (y - b) / m
        bottomX = int((imageHeight - averageIntercept) / averageSlope)
        topX = int((topY - averageIntercept) / averageSlope)
        cv.line(laneImage, (bottomX, imageHeight), (topX, topY), (0, 0, 255), 10)
    # blend red lines on the real pic
    return cv.addWeighted(roadImage, 0.8, laneImage, 1.0, 0)
'''