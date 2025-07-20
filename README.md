
# 🚦 Trích xuất biển báo giao thông bằng thiết bị IoT

Dự án này sử dụng mô hình YOLOv5 để huấn luyện và nhận diện các biển báo giao thông trong ảnh và video, ứng dụng vào hệ thống hỗ trợ giao thông thông minh.

## 📌 Giới thiệu

- Thu thập và xử lý dữ liệu là bước quan trọng để đảm bảo hiệu quả nhận diện.
- Dữ liệu gồm ảnh biển báo được chụp hoặc thu thập từ Internet (Google, Kanggle, Roboflow,...).
- Sau khi thu thập, ảnh được gán nhãn và xử lý theo định dạng YOLOv5.

## 🧹 Xử lý dữ liệu

- **Resize ảnh** về kích thước chuẩn.
- **Chuẩn hóa pixel** về khoảng [0, 1].
- **Chia dữ liệu**: 
  - Train: 83%
  - Validation: 10%
  - Test: 7%
- **Chuyển đổi định dạng**: tất cả ảnh được lưu về PNG, nhãn theo định dạng YOLO.

## ⚙️ Cấu hình huấn luyện YOLOv5

- Mô hình sử dụng: `YOLOv5s`
- Epochs: 200
- Learning rate: 0.001
- Batch size: 4
- Clone YOLO từ GitHub, cài requirements, dùng GPU nếu có.

Lệnh huấn luyện mẫu:

```bash
python train.py --img 640 --batch 4 --epochs 200 --data data.yaml --weights yolov5s.pt --device 0
```

## 🔍 Phát hiện đối tượng

Lệnh nhận diện ảnh:

```bash
python detect.py --source yolov5/data/trafficsign/test/images --weights last.pt --conf 0.7 --data data.yaml
```

Lệnh đánh giá mô hình:

```bash
python val.py --weights last.pt --data data.yaml --verbose
```

## 📈 Kết quả đánh giá

- Các biểu đồ loss (`box_loss`, `obj_loss`, `cls_loss`) đều giảm dần.
- Các chỉ số `precision`, `recall`, `mAP_0.5`, `mAP_0.5:0.95` đều cải thiện dần theo thời gian.

## 🖼️ Giao diện và Demo

- Chạy GUI:

```bash
python GUI.py
```

- Giao diện gồm các chức năng:
  - Upload ảnh để nhận dạng
  - Hiển thị kết quả trên ảnh
  - Phát âm tên biển báo
  - Kết nối ESP32-CAM để hiển thị video trực tiếp và nhận diện

## 📁 Cấu trúc thư mục

```
project/
├── yolov5/
├── runs/
├── data.yaml
├── GUI.py
├── README.md
└── data/
    ├── train/
    ├── val/
    └── test/
```

## 📌 Lưu ý

- Đảm bảo cài đủ thư viện từ `requirements.txt`
- Sử dụng GPU giúp huấn luyện nhanh và hiệu quả hơn

## 📬 Liên hệ

> Email: hungtvt218@gmail.com

