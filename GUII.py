import tkinter as tk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import torch
import voice
import cv2
import time
import cvzone
import threading
import queue
#import requests
#import numpy as np

# Load the model
model = torch.hub.load('ultralytics/yolov5', 'custom', 'last.pt', force_reload=False, trust_repo=True)

# Khởi tạo GUI
top = tk.Tk()
top.geometry('800x600+600+200')
top.title('Nhận dạng biển báo giao thông')
top.configure(background='#ffffff')

label = Label(top, background='#ffffff', font=('arial', 15, 'bold'))
sign_image = Label(top)
classify_b = None  # Khai báo biến nút nhận dạng
cap = None  # Khai báo biến cho webcam

# Cấu hình nút webcam và biến cho video stream từ ESP32-CAM
url = "http://192.168.45.135:81/stream"  # Thay địa_chỉ_IP_ESP32-CAM bằng IP của ESP32

# Khởi tạo hàng đợi và khóa
voice_queue = queue.Queue()
voice_lock = threading.Lock()

def read_ClassNames(file):
    with open(file, 'r', encoding='utf-8') as f:
        lst = f.readlines()
    return lst

def classify(file_path):
    global label
    global ClassNames
    image = Image.open(file_path)
    # Dự đoán các lớp
    results = model(image)
    print(results)
    # Lấy chỉ số lớp
    class_indices = results.pred[0][:, -1].int().tolist()
    # Chuyển đổi chỉ số lớp thành tên lớp bằng cách sử dụng một tập hợp để loại bỏ trùng lắp
    predicted_classes = set(ClassNames[i] for i in class_indices)
    # Chuyển đổi tập hợp các lớp thành một chuỗi
    label_text = ', '.join(predicted_classes)
    results.xyxy[0]
    results.pandas().xyxy[0]

    # Cập nhật giao diện người dùng
    label.configure(foreground='#011638', text=label_text, font=('arial', 20, 'bold'))
    label.update_idletasks()  # Đảm bảo label được cập nhật trước khi phát âm thanh

    # Đọc to label_text
    for i in predicted_classes:
        voice.text_to_speech_gtts(i)

def show_classify_button(show, file_path=None):
    global classify_b
    if show:
        if classify_b is not None:
            classify_b.place_forget()  # Ẩn nút cũ nếu tồn tại
        classify_b = Button(top, text="Nhận dạng", command=lambda: classify(file_path), padx=10, pady=5)
        classify_b.configure(background='#c71b20', foreground='white', font=('arial', 12, 'bold'))
        classify_b.place(relx=0.79, rely=0.46)
    else:
        if classify_b is not None:
            classify_b.place_forget()
            classify_b = None  # Đặt classify_b về None để đánh dấu không còn tồn tại

def upload_image():
    global button_web_camera
    global web_cam_button
    temp_button_web_camera = button_web_camera
    button_web_camera = False
    global cap
    try:
        # Dừng webcam nếu đang chạy
        if cap is not None:
            cap.release()
            #cap = None
        
        file_path = filedialog.askopenfilename()
        uploaded = Image.open(file_path)
        uploaded.thumbnail(((top.winfo_width()/2.25), (top.winfo_height()/2.25)))
        im = ImageTk.PhotoImage(uploaded)
        sign_image.configure(image=im)
        sign_image.image = im
        label.configure(text='')
        show_classify_button(True, file_path)
    except Exception as e:
        print(f"Error: {e}")
        if temp_button_web_camera:
            web_cam()

def task_voice_queue():
    temp = []
    while not voice_queue.empty():
        temp.extend(voice_queue.get())
    temp = list(set(temp))  # Loại bỏ các mục trùng lặp
    return temp

def play_voice(texts):
    with voice_lock:  # Đảm bảo rằng chỉ một luồng xử lý âm thanh tại một thời điểm
        for text in texts:
            voice.text_to_speech_gtts(text)

def process_voice_queue():
    while True:
        if not voice_queue.empty():
            texts = task_voice_queue()
            if texts:
                play_voice(texts)
        # Đảm bảo rằng vòng lặp không chiếm quá nhiều CPU
        time.sleep(5)

def web_cam():
    global button_web_camera
    if button_web_camera:
        return
    button_web_camera = True
    global cap
    global ClassNames
    show_classify_button(False)
    # Dừng webcam nếu đang chạy
    if cap is not None:
        cap.release()
    
    # Xóa văn bản trong label
    label.configure(text='')
    
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Kiểm tra webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Chuyển đổi khung hình từ BGR (OpenCV) sang RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Kết quả nhận dạng
            results = model(frame_rgb)
            predictions = results.xyxy[0]
            index = []
            for *box, conf, cls in predictions:
                cls = cls.item()
                index.append(cls)
                if conf >= 0.7:
                    x1, y1, x2, y2 = map(int, box)
                    # Vẽ bounding box xung quanh các đối tượng được theo dõi
                    w, h = x2 - x1, y2 - y1
                    cvzone.cornerRect(frame_rgb, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))
                    # ID của các đối tượng trên các khung hình
                    cvzone.putTextRect(frame_rgb, f'id {cls}', (max(0, x1), max(35, y1)), scale=1, thickness=2, offset=8)



            # Tạo đối tượng Image từ khung hình
            image = Image.fromarray(frame_rgb)
            # Chuyển đổi Image thành ImageTk
            imgtk = ImageTk.PhotoImage(image=image)
            # Cập nhật widget Label với ảnh mới
            sign_image.imgtk = imgtk
            sign_image.configure(image=imgtk)

            index = set(ClassNames[int(i)] for i in index)
            print("index: ", index)
            print("size_queue:", voice_queue.qsize())
            if index:
                # Đưa nhiệm vụ vào hàng đợi
                voice_queue.put(index)

        # Gọi lại hàm này sau 1 mili giây nếu cap vẫn mở
        if cap is not None and cap.isOpened():
            top.after(1, update_frame)

    # Khởi động luồng xử lý hàng đợi
    threading.Thread(target=process_voice_queue, daemon=True).start()

    # Hiển thị video_label và bắt đầu cập nhật khung hình
    update_frame()

# Đọc ClassNames từ file
ClassNames = read_ClassNames("ClassNames.txt")
button_web_camera = False
button_upload_an_image = False
# Đặt heading luôn ở trên cùng
heading = Label(top, text="Nhận dạng biển báo giao thông", pady=10, font=('arial', 20, 'bold'))
heading.configure(background='#ffffff', foreground='#364156')
heading.pack(side=TOP)

# Điều chỉnh kích thước của Frame chứa các nút
button_frame = tk.Frame(top, width=800, height=100)
button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X, expand=False)

upload = Button(button_frame, text="Upload an image", command=upload_image, padx=10, pady=5)
upload.configure(background='#c71b20', foreground='white', font=('arial', 10, 'bold'))
upload.pack(side=tk.LEFT, padx=10)

web_cam_button = Button(button_frame, text="Web cam", command=web_cam, padx=10, pady=5)
web_cam_button.configure(background='#c71b20', foreground='white', font=('arial', 10, 'bold'))
web_cam_button.pack(side=tk.LEFT, padx=10)

sign_image.pack(side=TOP, expand=True, fill=tk.BOTH)
label.pack(side=BOTTOM, expand=True)

top.mainloop()
