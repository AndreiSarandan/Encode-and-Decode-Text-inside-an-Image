import time
import cv2
import numpy as np
from PIL import Image
import pytesseract

COMPRESSED_FORMAT = True
cap = cv2.VideoCapture(0)
print("Opened Camera")


fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30
duration = 3 
dimensions = (640,  480)

out = cv2.VideoWriter('original_video.avi', fourcc, fps, dimensions)
if(cap.isOpened()):
    t = time.time()
    while( (time.time() - t) < duration ):
        ret, frame = cap.read()
        if not ret:
            break
        
        out.write(frame)

cap.release()
out.release()
print("Video Saved")

pytesseract.pytesseract.tesseract_cmd = '\Tesseract\Tesseract-OCR\\tesseract.exe'

img = Image.open('image.png')
text = pytesseract.image_to_string(img)
print(text)

file_object = open('message.txt', 'a')
file_object.write(text)
file_object.close()


frames=[2,4,6,8,10,12,14,16,18,20]
print(len(text)/10)
print(type(text))
initial_message=text
text=text+'@#$%^&'
split=text.split(None,9)
print(len(split))
print(split)


def get_binary(message):
    if( type(message) == str ):
        binary_message = ( char.split('b')[1] for char in map(bin,bytearray(message,'utf8')) )
        binary_message_8b = []
        for binary_char in binary_message:
            to_fill = ''.join('0' for l in range(len(binary_char), 8))
            binary_message_8b.append((to_fill + binary_char))
        return ''.join(binary_message_8b)
    elif( type(message) == np.uint8 or type(message) == int  ):
        binary_message = bin(message).split('b')[1]
        to_fill = ''.join('0' for l in range(len(binary_message), 8))
        return to_fill + binary_message
    elif( type(message) == np.ndarray ):
        binary_message_8b = []
        for value in message:
            binary_message = bin(value).split('b')[1]
            to_fill = ''.join('0' for l in range(len(binary_message), 8))
            binary_message_8b.append(to_fill + binary_message)
        return ''.join(binary_message_8b)


def encode_frame(frame, message):
    end_of_message_string = '@#$%^&'

    message = message + end_of_message_string
    binary_message = get_binary(message)

    max_bytes_to_encode = ((frame.shape[0] * frame.shape[1] * 3) // 8) * 2
    if max_bytes_to_encode > len(message):
        index = 1
        for row in frame:
            for pixel in row:
                b = get_binary(pixel[0])
                g = get_binary(pixel[1])
                r = get_binary(pixel[2])

                if index < len(binary_message):
                    b_steg = binary_message[index-1] + binary_message[index]
                    pixel[0] = int(b[0:-2] + b_steg, 2)
                    index += 2
                else:
                    return frame
                if index < len(binary_message):
                    g_steg = binary_message[index-1] + binary_message[index]
                    pixel[1] = int(g[0:-2] + g_steg, 2)
                    index += 2
                else:
                    return frame
                if index < len(binary_message):
                    r_steg = binary_message[index-1] + binary_message[index]
                    pixel[2] = int(r[0:-2] + r_steg, 2)
                    index += 2
                else:
                    return frame
        return frame
    else:
        print("Message is too large to be encoded!")
        return np.zeros(frame.shape, dtype=np.uint8)
    
video_capture = cv2.VideoCapture('original_video.avi')
final_message=''
items=[]
fps = 30.0
dimensions = (640,  480)

output_video = cv2.VideoWriter('encoded_video.avi', cv2.VideoWriter_fourcc(*'mp4v'), fps, dimensions)
frames = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
messages=split
frame_counter = 0  
while True:
    ret, frame = video_capture.read()

    if not ret:
        break

    frame_counter += 1

    if frame_counter in frames:
        index = frames.index(frame_counter)

        message = messages[index]

        encoded_frame = encode_frame(frame, message)

        output_video.write(encoded_frame)

    else:
        output_video.write(frame)

video_capture.release()
output_video.release()
final_message=' '.join(items)
