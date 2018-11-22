import pyrealsense2 as rs

# Declare pointcloud object, for calculating pointclouds and texture mappings
pc = rs.pointcloud()
# We want the points object to be persistent so we can display the last cloud when a frame drops
points = rs.points()

# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()
#Start streaming with default recommended configuration
pipe.start();
index = 0
try:
    while(True):
        # Wait for the next set of frames from the camera
        frames = pipe.wait_for_frames()
        # Fetch color and depth frames
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()

        # Tell pointcloud object to map to this color frame
        pc.map_to(color)

        # Generate the pointcloud and texture mappings
        points = pc.calculate(depth)

        print("Saving to %d.ply..." %index)
        points.export_to_ply("%d.ply" %index, color)
        print("Done")
        index +=1
finally:
    pipe.stop()