import io
import glob
import time
import http.server
import socketserver

from urllib import request as req
from urllib.parse import urlparse
from urllib.parse import parse_qs

import PIL
import PIL.ImageGrab

def next_image_screenshot():
    while True:
        yield PIL.ImageGrab.grab() # (all_screens=True)

images = next_image_screenshot()

def image_to_bytes(img_src, box=None, new_size=None, save=False):
    if isinstance(img_src, PIL.Image.Image):
        # use
        img = img_src
    else:
        # try to open/load
        img = PIL.Image.open(img_src, mode='r')

    if box is not None:
        print("cropping")
        img = img.crop(box)

    if new_size is not None:
        print("resizing")
        img = img.resize(new_size)

    print("bytestreaming")
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG')

    if save:
        with open(f'./images/img_{time.time()}.jpg', 'wb') as fout:
            img.save(fout, format=img.format)

    return byte_arr.getvalue()


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")
        # TODO: other content type for jpeg?
        # TODO: send size of payload

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        width = 240
        height = 135

        # Extract query param
        # TODO: read requested image size
        #query_components = parse_qs(urlparse(self.path).query)
        #if 'width' in query_components and 'height' in query_components:
        #    width = query_components["width"][0]
        #    height = query_components["height"][0]

        img = next(images)
        print(img)
        img_bytes = image_to_bytes(img, box=(0, 0, 480, 270), new_size=(width, height))

        self.wfile.write(img_bytes)

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8765
my_server = socketserver.TCPServer(("", PORT), MyHttpRequestHandler)
my_server.allow_reuse_address = True

try:
    # Star the server
    my_server.serve_forever()
except KeyboardInterrupt:
    my_server.shutdown()

my_server.shutdown()
