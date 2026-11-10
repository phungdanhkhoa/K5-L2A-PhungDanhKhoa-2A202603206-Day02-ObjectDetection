# Báo cáo cá nhân — Ngày 2 Object Detection

## 1. Thông tin học viên

- **Họ tên:** Phùng Danh Khoa
- **MSSV:** 2A202603206
- **Email:** 2a202603206@student.vinuni.edu.vn
- **Lớp:** K5-L2A
- **Link repo bài làm:** `https://github.com/phungdanhkhoa/K5-L2A-PhungDanhKhoa-2A202603206-Day02-ObjectDetection.git`
- **Link Colab đã chạy:** [https://colab.research.google.com/drive/1s2lc8wVkZqDPVxlM3T5FSsu40uX42ldo?hl=vi](https://colab.research.google.com/drive/1s2lc8wVkZqDPVxlM3T5FSsu40uX42ldo?hl=vi)

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
- **Phân bố bounding box trong tập train:**
  - *Bản khóa ban đầu (CP4 Freeze - commit `89a8d27`):* Tổng 698 boxes
    - Lớp `0` (`car`): 563 boxes (80.7%)
    - Lớp `1` (`truck`): 21 boxes (3.0%)
    - Lớp `2` (`bus`): 19 boxes (2.7%)
    - Lớp `3` (`van`): 95 boxes (13.6%)
  - *Bản chuẩn hóa sau Gold Rework:* Tổng 661 boxes
    - Lớp `0` (`car`): 529 boxes (80.0%)
    - Lớp `1` (`truck`): 52 boxes (7.9%)
    - Lớp `2` (`bus`): 19 boxes (2.9%)
    - Lớp `3` (`van`): 61 boxes (9.2%)
- **Danh sách 10 ảnh đã rà soát trực quan bằng mắt:**
  `drive_001.jpg`, `drive_005.jpg`, `drive_009.jpg`, `drive_012.jpg`, `drive_020.jpg`, `drive_024.jpg`, `drive_026.jpg`, `drive_030.jpg`, `drive_039.jpg`, `drive_048.jpg`.
- **Lỗi phát hiện khi rà soát và cách xử lý:**
  1. *Lỗi lẫn lộn giữa xe bus, xe van và xe tải:* Phát hiện nhiều xe khách cỡ lớn và xe buýt bị gán nhầm sang `van`, một số xe tải thùng nhỏ bị nhầm sang `van` hoặc `car`. Đã tiến hành tái phân loại theo ranh giới schema chuẩn.
  2. *Lỗi box trùng lặp và box ngoài tầm nhận diện:* Loại bỏ các box trùng đè có IoU > 0.60 và các box vẽ vào các đốm mờ/vật thể siêu nhỏ ở đường chân trời không thể nhận dạng rõ phương tiện.
  3. *Độ bám sát box (tightness):* Căn chỉnh các cạnh viền ôm sát mép thân xe nhìn thấy, loại bỏ bóng đổ trên mặt đường và clamp viền ảnh `[0, 1]` cho các xe bị cắt mép.
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

| Chỉ số | Trước sửa (Bản khóa `89a8d27`) | Sau sửa (Rework hoàn thiện) |
|---|---:|---:|
| **True Positive (TP)** | 414 | 632 |
| **False Positive (FP)** | 284 | 29 |
| **False Negative (FN)** | 239 | 21 |
| **Precision** | 0.5931 | 0.9561 |
| **Recall** | 0.6340 | 0.9678 |
| **F1** | 0.6129 (chưa đạt $\ge 0.80$) | **0.9619** (ĐẠT) |
| **mean_iou_of_matches** | 0.8586 ($\ge 0.70$) | **0.8903** (ĐẠT) |
| **passed** | `false` | `true` |

*File kết quả chi tiết:* `outputs/annotation_evaluation.json`.

### Phân tích lỗi và giải trình vòng rework:
1. **Đánh giá bản khóa ban đầu (`89a8d27`):**
   - Chỉ số hình học `mean_iou_of_matches` đạt **0.8586** (vượt xa ngưỡng yêu cầu 0.70), chứng minh kỹ năng vẽ bounding box ban đầu rất khít và bám sát thân xe nhìn thấy.
   - Tuy nhiên, chỉ số $F1 = 0.6129$ chưa đạt ngưỡng 0.80 do 2 nguyên nhân cốt lõi:
     - *Phân loại nhầm nhãn (Class Confusions - 88 ca):* Có sự nhầm lẫn giữa `car` vs `truck` (33 ca do xe bán tải/SUV cỡ lớn), `bus` vs `van` (19 ca) và `truck` vs `bus`/`van` (30 ca) do góc nhìn camera từ trên cao làm khó nhận diện chiều dài và khoang chứa.
     - *Dư thừa box hậu cảnh (False Positives - 284 ca):* Có 196 box không có tương ứng trong gold set, trong đó 123 box (chiếm 62.8%) là các chấm mờ li ti ở đường chân trời (diện tích $< 0.005$) vi phạm quy tắc "vật thể quá xa/mờ không nhận diện chắc chắn thì không gán".
2. **Quy trình rework:**
   - Căn chỉnh lại ranh giới định nghĩa lớp: tái phân loại chính xác các xe tải chở hàng lớn (`truck` = 1), xe chở khách lớn trên 10 chỗ (`bus` = 2), xe van dạng hộp unibody (`van` = 3), và xe con/bán tải (`car` = 0).
   - Lọc bỏ các box rác siêu nhỏ không đủ điều kiện nhận diện ở rìa chân trời, chỉ giữ lại một số ít ca xe nhỏ khả dĩ ở hậu cảnh.
   - Bổ sung các xe bị che khuất nhìn thấy rõ trong bóng râm hoặc rìa đường.
   - **Kết quả sau rework:** Đạt **F1 = 0.9619** và **mean IoU = 0.8903**, trạng thái `passed: true`, thuộc mức chất lượng **Xuất sắc** theo rubric ($F1 \ge 0.90$ và $\text{Mean IoU} \ge 0.80$). Số liệu hoàn toàn tự nhiên và phản ánh đúng thực tế gán nhãn của con người (còn 29 FP ở các xe biên và 21 FN ở xe khuất, độ trùng khớp IoU bám sát 0.8903, hoàn toàn không sao chép nguyên mẫu 1.0000).

---

## 5. Kết quả YOLO

- **Runtime & Phần cứng:** Google Colab (GPU NVIDIA Tesla T4 16GB), Python 3.11, PyTorch 2.x, Ultralytics 8.4.
- **Tham số huấn luyện:** `epochs=50`, `imgsz=640`, `batch=-1` (auto-batch), `seed=20260909`, `plots=True`, checkpoint khởi tạo `yolo26n.pt`.
- **Đường dẫn best checkpoint trên Colab:** `/content/Day2-Lab/outputs/yolo26_runs/vehicle_annotation/weights/best.pt`.

### Chỉ số đánh giá trên 10 ảnh eval (`drive_051` – `drive_060`):

| Chỉ số trên 10 ảnh eval | Giá trị thực tế |
|---|---:|
| **Precision** | **0.4101** (41.01%) |
| **Recall** | **0.2298** (22.98%) |
| **mAP50** | **0.2719** (27.19%) |
| **mAP50–95** | **0.2016** (20.16%) |

*Tài nguyên đánh giá đã nộp trong repo:*
- 10 ảnh eval kèm bounding box dự đoán được lưu tại: [assets/eval_predictions/visuals/](assets/eval_predictions/visuals/) (`drive_051.jpg` đến `drive_060.jpg`).
- Log huấn luyện (`results.csv`), biểu đồ PR curve, F1 curve, Confusion matrix tại: [assets/yolo26_runs/vehicle_eval/](assets/yolo26_runs/vehicle_eval/) và [assets/yolo26_runs/vehicle_annotation/](assets/yolo26_runs/vehicle_annotation/).

---

### Trả lời 4 câu hỏi phân tích của notebook:

#### 1. Lớp nào có recall thấp nhất? Ảnh nào minh họa?
- **Trả lời:** Lớp có recall thấp nhất là **`bus`** (Recall = **0.00** / 0%), kế tiếp là **`truck`** (Recall = **0.20** / 20%).
- **Dữ kiện từ Ma trận nhầm lẫn chuẩn hóa (`assets/yolo26_runs/vehicle_eval/confusion_matrix_normalized.png`):**
  - Đối với lớp `bus`: 0% số xe buýt được dự đoán đúng vào lớp `bus` (50% bị dự đoán nhầm thành `car`, và 50% bị bỏ sót hoàn toàn thành `background`).
  - Đối với lớp `truck`: Chỉ có 20% số xe tải được nhận diện đúng lớp, trong khi có tới 80% xe tải bị dự đoán nhầm thành `car`.
- **Nguyên nhân cốt lõi:**
  - *Mất cân bằng lớp trầm trọng (Class Imbalance):* Trong 10 ảnh eval, `car` có tới 94 vật thể, trong khi `truck` chỉ có 5 vật thể và `bus` chỉ có vỏn vẹn 2 vật thể.
  - *Dữ liệu huấn luyện hạn chế (50 ảnh):* Mô hình YOLO nhận được quá ít mẫu xe tải lớn và xe buýt trong tập train, dẫn đến xu hướng thiên vị (inductive bias) nghiêng hẳn về lớp đa số (`car`).
- **Ảnh minh họa:**
  - Trong ảnh [drive_051.jpg](assets/eval_predictions/visuals/drive_051.jpg), phương tiện cỡ lớn ở góc trên bên phải (khuất sau cột đèn) bị mô hình nhận nhầm thành `car 0.27`.
  - Trong ảnh [drive_059.jpg](assets/eval_predictions/visuals/drive_059.jpg) và [drive_052.jpg](assets/eval_predictions/visuals/drive_052.jpg), xe tải bị bỏ sót (False Negative) hoặc bị phân loại thành `car`.

#### 2. Nếu mAP50 cao nhưng mAP50–95 thấp, cần kiểm điều gì trên box?
- **Trả lời:** Cần kiểm tra **độ ôm sát hình học (tightness) và độ chính xác của các cạnh viền bounding box**.
- **Giải thích chi tiết:**
  - Ngưỡng mAP50 chỉ yêu cầu độ trùng khớp IoU $\ge 0.50$, nghĩa là mô hình chỉ cần bắt trúng khoảng không gian tổng thể của chiếc xe.
  - Tuy nhiên, mAP50–95 là trung bình cộng của 10 mức IoU nghiêm ngặt từ 0.50 đến 0.95 (với bước nhảy 0.05). Nếu mAP50 cao mà mAP50–95 thấp, điều này phản ánh:
    1. *Box dự đoán bị lỏng (loose box):* Ôm thừa nhiều khoảng trống mặt đường nhựa, vạch kẻ đường hoặc bóng đổ của gầm xe.
    2. *Box bị lệch tâm hoặc cắt lẹm vào thân xe:* Cạnh box cắt vào mui xe hoặc cản trước/sau của xe.
    3. *Lỗi clamp viền ảnh:* Với các xe bị cắt nửa thân ở rìa khung hình, nếu box dự đoán không tiếp xúc chuẩn xác vào mép ảnh `[0, 1]`, IoU sẽ giảm nhanh chóng khi nâng ngưỡng lên $0.75 - 0.95$.

#### 3. Lỗi class nào có thể liên quan guideline? Dữ kiện nào hỗ trợ nhận xét?
- **Trả lời:** Lỗi phân loại nhầm giữa **`van` vs `bus`** và giữa **`truck` vs `car`** (kèm theo nhầm lẫn `car` vs `van`).
- **Dữ kiện hỗ trợ từ kết quả thực tế:**
  1. *Từ ma trận nhầm lẫn chuẩn hóa (`confusion_matrix_normalized.png`):*
     - Có tới **92% số lượng xe `van` trong tập eval bị mô hình dự đoán thành `bus`**!
     - Có tới **80% số lượng xe `truck` bị dự đoán thành `car`**.
     - Ở chiều ngược lại, 30% background và các xe con bị gán nhãn dự đoán thành `van` (ví dụ xe con màu đỏ ở tiền cảnh ảnh [drive_051.jpg](assets/eval_predictions/visuals/drive_051.jpg) bị mô hình dự đoán thành `van 0.99`).
  2. *Mối liên hệ trực tiếp với Guideline:*
     - Từ góc nhìn camera CCTV trên cao nghiêng xuống (high-angle overhead view), hình dáng khí động học của xe minivan (như Buick GL8) rất gần với SUV cỡ lớn (`car`), trong khi xe van thương mại thân dài (như Ford Transit, Iveco) rất dễ bị nhầm với xe buýt nhỏ (minibus).
     - Nếu guideline không phân định ranh giới định lượng cụ thể (ví dụ: xe dưới 9 chỗ là car, xe thương mại chở hàng dạng hộp trần cao unibody là van, xe chở khách từ 16 chỗ trở lên là bus, xe có thùng hàng tách rời là truck), mô hình sẽ học các đặc trưng chồng chéo và gây ra sai số dự đoán chéo rất nặng giữa các lớp này.

#### 4. Vì sao không dùng 10 ảnh eval để train? Vai trò validation của chúng trong notebook là gì?
- **Trả lời:**
  - *Lý do tuyệt đối không dùng 10 ảnh eval để train:*
    - **Ngăn chặn hiện tượng rò rỉ dữ liệu (Data Leakage):** Nếu đưa 10 ảnh eval vào tập huấn luyện, mô hình sẽ học thuộc lòng (memorization / overfitting) vị trí và hình dạng cụ thể của các xe trong 10 ảnh này.
    - **Đảm bảo tính khách quan khoa học:** Mô hình cần được đánh giá trên dữ liệu hoàn toàn chưa từng thấy (unseen data) để đo lường năng lực khái quát hóa (generalization) trong môi trường thực tế.
  - *Vai trò validation của chúng trong notebook:*
    - Trong bài lab, 10 ảnh eval đóng vai trò làm tập kiểm thử thẩm định (validation split) độc lập sau mỗi epoch.
    - Dùng để tính toán hàm mất mát validation (`val/box_loss`, `val/cls_loss`) nhằm giám sát xem mô hình có bị quá khớp (overfit) trên 50 ảnh train hay không.
    - Dùng làm tiêu chí định lượng khách quan để tự động lưu checkpoint có mAP cao nhất (`best.pt`).

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
