from flask import Flask, render_template, Response
from PIL import Image
import io
import time
import os


DEBUG = False


import logging
log = logging.getLogger('werkzeug')

if(DEBUG):
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.ERROR)

class WebServer:
    def __init__(self):
        '''
        Initialize the web server
        '''
        self.app = Flask(__name__)
        self.img = None
        self.old_img = None
        self.setup_routes()

    def setup_routes(self):
        '''
        Config the routes
        '''
        
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)

    def capture_image(self):
        '''
        Capture the image to display
        '''
        self.img = Image.open("PiPerW/tmp/display.png")

    def generate_frames(self):
        '''
        Generate the frames to display
        '''
        while True:
            # Check if the image has changed
            if os.path.exists("PiPerW/tmp/display.png"):
                if self.img is None or os.path.getmtime("PiPerW/tmp/display.png") != self.old_img:
                    self.capture_image()
                    self.old_img = os.path.getmtime("PiPerW/tmp/display.png")

            # Check if the image is not None
            if self.img is not None:
                buf = io.BytesIO()
                self.img.save(buf, format='JPEG')
                frame = buf.getvalue()

                # Yield the frame in byte format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Opcional: Añadir un pequeño retraso
            time.sleep(0.1)

    def video_feed(self):
        '''
        Display the video feed
        '''
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def index(self):
        '''
        Display the index page
        '''
        return render_template('index.html')

    def run(self):
        '''
        Run the web server
        '''
        self.app.run(debug=DEBUG)


# Start the web server
web_server = WebServer()
