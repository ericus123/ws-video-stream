import asyncio
import cv2
import websockets
import sys

# Maintain a dictionary to store video capture instances for each client
video_captures = {}

async def stream_video(websocket, path):
    if len(sys.argv) < 2:
        print("Please provide the path to the video file as a command-line argument.")
        return

    video_path = sys.argv[1]  # Get the video file path from the command-line arguments

    try:
        # Create a new video capture instance for this client
        vid = cv2.VideoCapture(video_path)
        video_captures[websocket] = vid

        # Get the actual frame rate of the video
        frame_rate = vid.get(cv2.CAP_PROP_FPS)

        while vid.isOpened():
            _, frame = vid.read()

            # Convert the frame to JPEG format
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]
            _, jpg_data = cv2.imencode('.jpg', frame, encode_param)

            # Send the JPEG data to the client
            await websocket.send(jpg_data.tobytes())

            # Introduce a delay to achieve the desired frame rate
            delay = 1 / frame_rate
            await asyncio.sleep(delay)

    except websockets.exceptions.ConnectionClosed:
        # Handle close initiated by the client
        if websocket in video_captures:
            vid = video_captures[websocket]
            vid.release()
            del video_captures[websocket]

start_server = websockets.serve(stream_video, "0.0.0.0", 4200)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()