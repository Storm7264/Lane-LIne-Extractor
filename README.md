# Lane-LIne-Extractor
 What the program does

You put road photos in a folder. The program goes through each photo and:

Keeps only the white and yellow pixels (lane paint colors).
Blurs the image a little to remove noise.
Finds the edges (outlines) of what is left.
Hides everything outside a trapezoid in front of the car, so only the road area is looked at.
Saves the final edge picture, plus a 2x2 picture showing the steps.
Requirements
Python 3
OpenCV and NumPy
pip install opencv-python numpy
How to run
Put your road images (.jpg, .jpeg or .png) in a folder called test_images.
Run:
python task2.py
Look in the output folder (it is created automatically).

For every input image, e.g. road.jpg, you get:

File	What it is
road_result.png	The final lane edges only
road_steps.png	A 2x2 picture of all the steps
How it works, step by step
1. Load the image (loadImage)

Reads the picture from disk. If a file can't be read, the program prints a message and skips it.

2. Color filter (filterColor)

The image is converted from normal BGR colors to HSV (hue, saturation, value). HSV makes it much easier to pick colors.

White = very low saturation (not colorful) and very bright: S <= 25, V >= 215.
Yellow = hue between 15 and 35, and strongly colored: S >= 130.

Both masks are joined, and only the pixels that match are kept from the real picture. Everything else turns black.

3. Gaussian blur (applyGaussianBlur)

The filtered picture is turned gray (Canny needs a gray image) and blurred with a 5x5 Gaussian blur. This removes tiny speckles so they don't become fake edges.

4. Canny edge detection (applyCannyEdge)

Finds the outlines of the white and yellow shapes.

Edges weaker than 50 are thrown away.
Edges stronger than 150 are definitely kept.
5. Region of interest (applyRoiMask)

A trapezoid shape in front of the car is drawn on a black canvas. Only edges inside the trapezoid are kept. This removes signs, cars, trees and the sky, which are not part of the road.

6. Steps picture (makeComparison)

Stacks the pictures into one 2x2 image so you can see every stage:

+-----------------+-----------------+
| Original image  | Color filtered  |
+-----------------+-----------------+
| Canny edges     | Final (ROI)     |
+-----------------+-----------------+
Results
Input images

These are the plain road photos that go into the program (from test_images).

Input: straight highway with a yellow line on the left and white dashes on the right

Input - straight highway

Input: curved highway with a white line on the right and dashed lines on the left

Input - curved highway

Output BEFORE the bug fix

On the curved highway the first version of the filter was too loose. You can see in the color-filtered picture that the hazy sky near the horizon and the dry grass on the right were wrongly picked up as white/yellow. This caused lots of fake edges in the Canny and final pictures.

Output before fix

Output AFTER the bug fix

After tightening the color limits and moving the top of the trapezoid, the sky and grass are gone. Only the real lane lines (and a couple of small yellow road signs, which are outside the road area) are left. The final picture shows just the clean lane edge.

Curved highway, fixed:

Output after fix - curved highway

Straight highway, fixed (the yellow line and the white dashes are both detected):

Output after fix - straight highway

Bonus: lane lines drawn on the road

The commented-out code at the bottom of task2.py (drawLanes) goes one step further. It finds straight pieces with the Hough transform, averages them into one left line and one right line, and draws them in red on the original photo. This is what it looks like:

Lane lines drawn in red

The bug fixes in detail
Problem seen	Fix
Hazy sky was detected as white	White must now have saturation at most 25 and brightness at least 215
Dry grass was detected as yellow	Yellow must now have saturation at least 130, because grass is pale
The trapezoid covered the sky	The top of the trapezoid was moved down to 62% of the image height
Limits
It works best in clear daylight. Shadows, night or rain would need different color limits.
The trapezoid is fixed, so it assumes the camera is mounted in the middle of the car, looking straight ahead.
Small yellow signs can still show up in the color-filtered step, but the road mask removes them from the final result.
