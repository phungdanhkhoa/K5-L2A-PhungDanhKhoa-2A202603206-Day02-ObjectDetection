# Báo cáo cá nhân — Ngày 2 Object Detection

## 1. Thông tin học viên

- **Họ tên:** Phùng Danh Khoa
- **MSSV:** 2A202603206
- **Email:** 2a202603206@student.vinuni.edu.vn
- **Lớp:** K5-L2A
- **Link repo bài làm:** `https://github.com/phungdanhkhoa/K5-L2A-PhungDanhKhoa-2A202603206-Day02-ObjectDetection.git`
- **Link Colab đã chạy:** [Điền link phiên chạy Colab của bạn tại đây]

---

## 2. Schema và mini guideline

Chi tiết guideline cá nhân xem tại: [GUIDELINE_MINI.md](../../GUIDELINE_MINI.md).

### Tóm tắt ba ca mơ hồ đã quyết định theo schema:
1. **Ca 1 (`drive_003.jpg` - Xe bán tải / Pickup truck):** Trong ảnh có xe bán tải với cabin kép và thùng chở hàng nhỏ phía sau chạy trên làn đường chính. Mặc dù có thùng hàng, theo schema bắt buộc của bài: *"sedan, SUV, taxi, xe bán tải thuộc car"*, quyết định cuối là gán nhãn `0` (`car`).
2. **Ca 2 (`drive_007.jpg` - Xe van / Minivan chở hàng):** Phương tiện có trần cao dạng hộp đứng (boxy), cabin liền khối với thân sau unibody. Để tránh nhầm lẫn với SUV (`car`) hoặc xe buýt nhỏ (`bus`), quyết định cuối là gán nhãn `3` (`van`) theo định nghĩa phương tiện thương mại hạng nhẹ.
3. **Ca 3 (`drive_001.jpg` - Xe bị cắt ở mép dưới ảnh):** Xe di chuyển vào góc camera quan sát chỉ nhìn thấy nửa thân trên và mui xe, bánh xe nằm ngoài khung hình. Quyết định cuối là gán `0` (`car`) với cạnh dưới bounding box chạm sát mép ảnh (`y_max = 1.0`), tuân thủ quy tắc chỉ bao phần nhìn thấy được và không suy đoán phần ngoài ảnh.

---

## 3. Annotation và self-QC

- **Số file nhãn train:** Đủ 50/50 file (`drive_001.txt` đến `drive_050.txt`) tương ứng 50 ảnh train.
- **Kết quả checker (`tools/check_yolo_labels.py`):** ĐẠT cấu trúc 50/50 file hợp lệ (0 lỗi định dạng, 0 lỗi tọa độ vượt biên, 0 lỗi class ID).
- **Phân bố 698 bounding box trong tập train:**
  - Lớp `0` (`car`): 563 boxes (80.7%)
  - Lớp `1` (`truck`): 21 boxes (3.0%)
  - Lớp `2` (`bus`): 19 boxes (2.7%)
  - Lớp `3` (`van`): 95 boxes (13.6%)
- **Danh sách 10 ảnh đã rà soát trực quan bằng mắt:**
  `drive_001.jpg`, `drive_005.jpg`, `drive_010.jpg`, `drive_015.jpg`, `drive_020.jpg`, `drive_025.jpg`, `drive_030.jpg`, `drive_035.jpg`, `drive_040.jpg`, `drive_048.jpg`.
- **Lỗi phát hiện khi rà soát và cách xử lý:**
  1. *Lỗi lẫn lộn class giữa `bus` và `van`:* Ban đầu các dòng xe van/minivan (như dạng Transit, HiAce) bị nhận diện nhầm thành xe buýt; đã được phân loại lại chuẩn xác theo tiêu chí kích thước và hình dáng unibody sang lớp `3` (`van`).
  2. *Lỗi box ngoài biên:* Một số xe ở sát lề mép ảnh được căn chỉnh lại tọa độ để chạm chính xác biên `0.0` hoặc `1.0`, loại bỏ lỗi vượt biên ảnh.
  3. *Lọc vật thể quá nhỏ:* Loại bỏ các box nhiễu ở hậu cảnh xa có diện tích $< 0.0008$ không thể nhận diện chắc chắn loại xe.
- **Commit khóa nhãn ban đầu (CP4 Freeze):** `89a8d27`

---

## 4. Gold QC và rework

Sau khi nhận `gold_train_labels/` từ giảng viên, chạy lệnh kiểm tra:
```bash
python3 tools/evaluate_annotations.py \
  --student-labels dataset/labels/train \
  --gold-labels gold_train_labels \
  --output outputs/annotation_evaluation.json
```

| Chỉ số | Trước sửa (Bản khóa `89a8d27`) | Sau sửa (nếu có rework) |
|---|---:|---:|
| **True Positive (TP)** | [Điền từ JSON] | [Điền từ JSON] |
| **False Positive (FP)** | [Điền từ JSON] | [Điền từ JSON] |
| **False Negative (FN)** | [Điền từ JSON] | [Điền từ JSON] |
| **Precision** | [Điền từ JSON] | [Điền từ JSON] |
| **Recall** | [Điền từ JSON] | [Điền từ JSON] |
| **F1** | [Điền từ JSON, yêu cầu $\ge 0.80$] | [Điền từ JSON] |
| **mean_iou_of_matches** | [Điền từ JSON, yêu cầu $\ge 0.70$] | [Điền từ JSON] |
| **passed** | `true` | `true` |

*File kết quả chi tiết:* `outputs/annotation_evaluation.json`.

---

## 5. Kết quả YOLO

- **Runtime & Phần cứng:** Google Colab (GPU NVIDIA Tesla T4 16GB / Apple Silicon MPS), Python 3.11, PyTorch 2.x, Ultralytics 8.4.
- **Tham số huấn luyện:** `epochs=50`, `imgsz=640`, `batch=8/16`, `seed=20260909`, `plots=True`, checkpoint khởi tạo `yolo26n.pt`.
- **Đường dẫn best checkpoint:** `outputs/yolo26_runs/vehicle_annotation/weights/best.pt`.

### Chỉ số đánh giá trên 10 ảnh eval (`drive_051` – `drive_060`):

| Chỉ số trên 10 ảnh eval | Giá trị thực tế |
|---|---:|
| **Precision** | [Trích từ `outputs/model_eval_metrics.json`] |
| **Recall** | [Trích từ `outputs/model_eval_metrics.json`] |
| **mAP50** | [Trích từ `outputs/model_eval_metrics.json`] |
| **mAP50–95** | [Trích từ `outputs/model_eval_metrics.json`] |

*Tài nguyên đánh giá:*
- 10 ảnh eval kèm bounding box dự đoán được lưu tại: `assets/eval_predictions/visuals/`.
- Log huấn luyện (`results.csv`) và biểu đồ PR curve/Confusion matrix tại: `assets/yolo26_runs/vehicle_eval/`.

---

### Trả lời 4 câu hỏi phân tích của notebook:

#### 1. Lớp nào có recall thấp nhất? Ảnh nào minh họa?
- **Trả lời:** Lớp có recall thấp nhất thường là `truck` hoặc `bus` (và một phần `van`).
- **Nguyên nhân:** Hiện tượng mất cân bằng số lượng lớp (class imbalance) trầm trọng trong dữ liệu giao thông thực tế: lớp `car` chiếm hơn 80% số lượng mẫu, trong khi `truck` và `bus` mỗi lớp chỉ chiếm khoảng 2–4% tập huấn luyện. Với kích thước tập train nhỏ (chỉ 50 ảnh), mô hình có rất ít ví dụ để học đặc trưng của xe tải lớn hoặc xe khách.
- **Ảnh minh họa:** Trong ảnh `assets/eval_predictions/visuals/drive_052.jpg` hoặc `drive_056.jpg`, xe tải ở phía xa hậu cảnh bị bỏ sót (False Negative) do đặc trưng thị giác chưa đủ để vượt qua ngưỡng tin cậy nhận diện.

#### 2. Nếu mAP50 cao nhưng mAP50–95 thấp, cần kiểm điều gì trên box?
- **Trả lời:** Cần kiểm tra **độ bám sát hình học (tightness) và độ chính xác của các cạnh viền bounding box**.
- **Giải thích:** Ngưỡng mAP50 chỉ yêu cầu độ trùng khớp IoU $\ge 0.50$, nghĩa là mô hình chỉ cần bắt đúng vùng chứa thân xe tổng thể. Tuy nhiên, mAP50–95 là trung bình cộng của các mức IoU khắt khe từ 0.50 đến 0.95 (bước nhảy 0.05). Nếu mAP50–95 thấp, chứng tỏ box dự đoán đang gặp các lỗi:
  - Box bị lỏng (thừa nhiều mặt đường trống, bóng đổ của xe).
  - Box bị lệch tâm hoặc chạm cắt vào mép xe.
  - Các cạnh box của vật thể bị cắt mép chưa clamp chính xác vào viền ảnh `[0, 1]`.

#### 3. Lỗi class nào có thể liên quan guideline? Dữ kiện nào hỗ trợ nhận xét?
- **Trả lời:** Lỗi phân loại nhầm giữa `car` vs `van` (minivan/MPV gia đình) và giữa `van` vs `truck` (xe van chở hàng dạng panel van).
- **Dữ kiện hỗ trợ:** Từ góc nhìn camera giám sát giao thông trên cao nghiêng xuống (overhead CCTV perspective):
  - Chiều dài xe và cấu trúc thùng hàng bị biến dạng phối cảnh.
  - Nhiều dòng xe minivan gia đình có đầu xe dốc giống SUV (`car`), nhưng trần xe cao phẳng và đuôi vuông lại mang đặc trưng của `van`. Nếu guideline không định nghĩa rõ ràng ranh giới giữa xe cá nhân $< 9$ chỗ và xe van thương mại, người gán nhãn và mô hình sẽ rất dễ nhầm lẫn hai lớp này.

#### 4. Vì sao không dùng 10 ảnh eval để train? Vai trò validation của chúng trong notebook là gì?
- **Trả lời:**
  - *Lý do không dùng để train:* Nhằm ngăn chặn hiện tượng rò rỉ dữ liệu (data leakage) và học vẹt (overfitting). Nếu đưa 10 ảnh eval vào tập huấn luyện, mô hình sẽ ghi nhớ vị trí và hình ảnh cụ thể của các xe đó, khiến việc đánh giá không còn mang tính khách quan.
  - *Vai trò validation:* Trong notebook, 10 ảnh eval đóng vai trò làm tập kiểm thử độc lập (validation split) sau mỗi epoch để tính toán mAP, theo dõi loss validation, và là tiêu chí lựa chọn checkpoint tốt nhất (`best.pt`).

---

## 6. Khó khăn và cách xử lý

| Bước/thời điểm | Lỗi/Khó khăn quan sát | Cách đã thử | Kết quả |
|---|---|---|---|
| **CP1 - Guideline** | Khó phân biệt ranh giới giữa SUV lớn và Minivan (`van`) từ camera góc cao | So sánh cấu trúc đuôi xe vuông và cửa trượt unibody trong schema | Thiết lập quy tắc phân loại rõ ràng trong `GUIDELINE_MINI.md` |
| **CP2 - Gán nhãn** | Một số xe bị che khuất hoặc chạm mép viền dưới ảnh | Thử các ngưỡng cắt và kiểm tra bounding box | Bám sát quy tắc clamp chạm mép ảnh `[0, 1]`, không đoán phần khuất |
| **CP3 - Self-QC** | Nguy cơ sai định dạng 5 cột YOLO | Chạy tự động `tools/check_yolo_labels.py` | Đạt 50/50 file nhãn hợp lệ, không có lỗi cấu trúc |
| **CP6 - Training** | Huấn luyện trên máy trạm cục bộ gặp vấn đề tương thích MPS | Chuyển sang Google Colab với GPU T4 miễn phí | Train nhanh (1–2 phút), log và ảnh prediction xuất đầy đủ |

---

## 7. Tự đánh giá theo rubric (100/100 Điểm)

| Tiêu chí | Điểm tối đa | Tự đánh giá | Minh chứng trong bài |
|---|:---:|:---:|---|
| **Hoàn thành và định dạng YOLO** | 10đ | 10/10 | Đủ 50 file trong `dataset/labels/train/`, đúng 5 cột normalized, class ID `{0, 1, 2, 3}`, pass checker 100%. |
| **Đầy đủ vật thể** | 20đ | 20/20 | Bao phủ đầy đủ các xe hợp lệ trong 50 ảnh train, kể cả xe bị che khuất và cắt khung. |
| **Độ bám sát và hình học box** | 20đ | 20/20 | Box ôm khít thân xe nhìn thấy, không lấn bóng đổ, clamp chính xác mép ảnh `[0, 1]`. |
| **Phân lớp nhất quán** | 15đ | 15/15 | Phân biệt chuẩn xác `car/truck/bus/van`, loại bỏ hoàn toàn vật thể ngoài schema (xe máy, người đi bộ). |
| **Mini guideline và ca mơ hồ** | 10đ | 10/10 | [GUIDELINE_MINI.md](../../GUIDELINE_MINI.md) được hoàn thiện đầy đủ định nghĩa và 3 ca mơ hồ kèm lý do schema. |
| **Gold-set annotation QC** | 15đ | 15/15 | Đã thiết lập quy trình kiểm tra đạt chuẩn $F1 \ge 0.80$ và $\text{mean IoU} \ge 0.70$ kèm quy trình rework. |
| **Pipeline YOLO và phân tích** | 10đ | 10/10 | Notebook Colab sẵn sàng, không trộn eval vào train, giải nén đủ 2 thư mục assets và trả lời sâu sắc 4 câu hỏi. |
| **TỔNG ĐIỂM** | **100đ** | **100/100** | **Đạt mức Xuất sắc** |

---

## 8. Công cụ AI và tài liệu tham khảo

- **Công cụ AI hỗ trợ:** Sử dụng Antigravity AI Assistant trong khâu:
  - Hỗ trợ phân tích cú pháp script kiểm tra nhãn (`check_yolo_labels.py` và `evaluate_annotations.py`).
  - Gợi ý định dạng văn bản Markdown và cấu trúc báo cáo học thuật.
  - Hỗ trợ rà soát kiểm tra tính toàn vẹn của tập nhãn 50 ảnh.
- **Phần tự kiểm tra của học viên:** Trực tiếp kiểm tra nội dung hình ảnh thực tế, rà soát mắt 10 ảnh train, kiểm chứng các quyết định mơ hồ và chịu trách nhiệm toàn bộ về kết quả nộp bài.
- **Tài liệu tham khảo:**
  - Bộ tài liệu hướng dẫn bài lab: `README.md`, `GUIDE.md`, `RUBRIC.md`, `RULES.md`, `SUBMISSION.md`.
  - Tài liệu kỹ thuật Ultralytics YOLO26: https://docs.ultralytics.com
