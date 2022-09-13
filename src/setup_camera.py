#!/usr/bin/env python3

import socket
import json
import cv2
import numpy as np
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt
from matplotlib import animation

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 9091  # The port used by the server
IMG_WIDTH = 600
IMG_HEIGHT = 500

get_version =  \
    {
    "msg_type" : "get_protocol_version" 
    }
set_camera = \
    {
        "msg_type" : "cam_config",
        "fov" : "120", 
        "fish_eye_x" : "0.0",
        "fish_eye_y" : "0.0",
        "img_w" : str(IMG_WIDTH),
        "img_h" : str(IMG_HEIGHT),
        "img_d" : "3",
        "img_enc" : "PNG",
        "offset_x" : "0.0",
        "offset_y" : "3.0",
        "offset_z" : "0.0",
        "rot_x" : "0.0"
    }

control = \
    {
        "msg_type" : "control",
        "steering" : "0.0",
        "throttle" : "0.3",
        "brake" : "0.0"
    }

class TelemetryInterface:

    def __init__(self) -> None:
        self.image_np = np.zeros((IMG_HEIGHT, IMG_WIDTH))
        self.imshow_obj = None

    def get_img_from_telemetry(self, msg) -> np.ndarray:
        img_64 = base64.b64decode(msg['image'])
        pilimg = Image.open(io.BytesIO(img_64))
        img_np = np.array(pilimg)
        return img_np

    def get_fig_init(self):
        def fig_init():
            self.imshow_obj.set_data(self.image_np)
        return fig_init
    
    def get_fig_update(self):
        def fig_update(i):
            self.imshow_obj.set_data(self.image_np)
            plt.draw()
            return self.imshow_obj
        return fig_update

    def main(self) -> None:
        camera_msg = json.dumps(set_camera)
        send_data = json.dumps(control)

        fig = plt.figure()
        ax = fig.gca()
        self.imshow_obj = ax.imshow(self.image_np)
        plt.draw()
        plt.pause(0.01)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
        try:
            s.sendall(bytes(camera_msg, encoding="utf-8"))
            unparsed_str = ""

            while True:
                data = s.recv(1024).decode("utf-8")
                unparsed_str += data
                unparsed_start_idx = 0

                for i in range(len(unparsed_str)):
                    if unparsed_str[i] == '\n':
                        new_obj = json.loads(unparsed_str[unparsed_start_idx:i])
                        unparsed_start_idx = i + 1
                        if 'msg_type' in new_obj:
                            if new_obj['msg_type'] == 'telemetry':
                                self.img_np = self.get_img_from_telemetry(new_obj)
                                print(self.img_np.shape)
                                self.imshow_obj.set_data(self.img_np)
                                # plt.draw()
                                # plt.pause(0.01)

        finally:
            s.close()

if __name__=="__main__":
    interface = TelemetryInterface()
    interface.main()