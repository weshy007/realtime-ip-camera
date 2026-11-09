A small security team wants a lightweight desktop viewer for the cameras on its office network; no vendor software, just Python. 

Te application connects to an authorized IP camera, or a smartphone running a camera app such as IP Webcam, over your local network and shows its live video. On top of the stream it must:

- process every frame (resize it and overlay a timestamp, the camera's name, the resolution and an estimated FPS);
- capture a screenshot when you press S;
- start and stop a video recording when you press R;
- survive real network problems — a wrong URL, a camera that is off, a connection that drops mid-stream and always shut down cleanly.