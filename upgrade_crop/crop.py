import pyrealsense2 as rs
import time
import numpy as np
import cv2




pipeline = rs.pipeline()


points = rs.points()

config = rs.config()
config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: " , depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1 #1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

def crop_center_color(img,cropx,cropy):
    x,y,c = img.shape
    print(x)
    print(y)
    startx = x//2 - cropx//2
    starty = y//2 - cropy//2
    return img[startx:startx+cropx, starty:starty+cropy,  :]

def crop_center_depth(img,cropx,cropy):
    x,y = img.shape
    startx = x//2 - cropx//2
    starty = y//2 - cropy//2
    return img[startx:startx+cropx, starty:starty+cropy]

index = 0
try:

    while 1:  #added this
        time.sleep(1)
        # Wait for the next set of frames from the camera
        frames = pipeline.wait_for_frames()

        aligned_frames = align.process(frames)

        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        print(depth_image.shape)

        depth_image = crop_center_depth(depth_image, 300, 200);

        color_image = crop_center_color(color_image, 300, 200);

        print(color_image.shape)



        grey_color = 153
        depth_image_3d = np.dstack(
            (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))
        print(type(images))
        print(images)
        cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Align Example', images)
        cv2.imwrite("0.png", images)

        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break

finally:
    pipeline.stop()