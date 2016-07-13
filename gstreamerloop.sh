

#while true; do
#modprobe mxc_v4l2_capture 
gst-launch -vvv tvsrc device=/dev/video0 ! mfw_ipucsc ! 'video/x-raw-yuv, format=(fourcc)I420, width=(int)1280, height=(int)720, framerate=(fraction)30/1, pixel-aspect-ratio=(fraction)1/1, framed=(boolean)true' ! queue!  vpuenc codec=6  force-framerate=1 gopsize=10 ! rtph264pay config-interval=1 pt=96  ! multiudpsink clients=10.1.1.191:5600,10.1.1.1:5550 sync=false async=false 
#done