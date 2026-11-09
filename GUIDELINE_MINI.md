# Mini guideline — bài làm cá nhân

> Điền nội dung này trước khi bắt đầu gán nhãn. Giữ lại các quyết định sau khi self-QC.

## Định nghĩa lớp

| Lớp | Định nghĩa của bạn | Ví dụ/điểm phân biệt |
| --- | --- | --- |
| `car` | Phương tiện cơ giới chở người từ 4 đến 9 chỗ ngồi (sedan, SUV, hatchback, crossover, taxi) và xe bán tải (pickup truck). | Thân xe thấp hoặc trung bình; xe bán tải có cabin đơn/kép gắn liền thùng hở nhỏ phía sau; không dùng để chở hàng chuyên dụng khối lượng lớn. Phân biệt với `truck` vì không có chassis tải nặng tách rời. |
| `truck` | Phương tiện cơ giới chuyên dụng chở hàng hóa hạng trung và nặng, xe tải thùng kín/hở, xe đầu kéo kéo sơ-mi rơ-moóc, xe ben, xe bồn. | Khung gầm chassis tải nặng, khoang chở hàng hoặc thùng xe có kích thước lớn tách biệt rõ với buồng lái cabin. Phân biệt với `van` vì van có thân vỏ liền khối, và phân biệt với `car` (không bao gồm xe bán tải cỡ nhỏ). |
| `bus` | Phương tiện vận tải hành khách công cộng hoặc du lịch cỡ lớn, thiết kế chở trên 10 người (xe buýt nội đô, xe khách liên tỉnh, xe đưa đón học sinh/minibus lớn). | Thân xe dài, trần cao, nhiều hàng cửa sổ kính lớn dọc hai bên sườn xe cho hành khách. Phân biệt với `van` chở người cỡ nhỏ (như HiAce, Solati dưới 16 chỗ) ở chiều dài và dung tích chuyên chở. |
| `van` | Phương tiện thương mại hạng nhẹ dạng hình hộp chữ nhật (boxy), cabin điều khiển và khoang chở hàng/chở người liền một khối thống nhất (monovolume / unibody / panel van), bao gồm cả minivan gia đình và xe tải van giao hàng. | Đuôi xe vuông đứng, cửa lùa trượt ở sườn hoặc cửa đôi mở ngang phía sau; trần xe cao hơn đáng kể so với sedan/hatchback nhưng thân xe ngắn và thấp hơn xe buýt (`bus`). Điển hình: Toyota HiAce, Ford Transit, Hyundai Starex. |

## Quy tắc chung

- **Box bám sát vật thể nghĩa là:** Bounding box phải ôm khít các pixel rìa ngoài cùng của thân xe thực tế nhìn thấy được (đèn, gương chiếu hậu, cản trước/sau, lốp xe tiếp đất). Không lấy thêm phần bóng đổ (shadow) trên mặt đường, không mở rộng lấn sang mặt đường trống, bầu trời hoặc lấn sang xe bên cạnh.
- **Vật thể bị che khuất:** Vẽ box bao quanh **toàn bộ phần nhìn thấy được (visible body)** của xe bị che nếu phần nhìn thấy còn đủ đặc trưng để nhận diện chắc chắn loại xe. Nếu vật thể bị che khuất quá mức (> 80-85%) chỉ còn một mẩu nhỏ không thể xác định loại xe thì không gán nhãn để tránh gây nhiễu cho mô hình. Nếu hai xe che khuất nhau, vẽ 2 box riêng biệt ôm sát phần nhìn thấy của từng xe, tuyệt đối không gộp hai xe vào một box.
- **Vật thể bị cắt bởi rìa ảnh:** Khi xe đang đi vào hoặc đi ra khỏi góc camera quan sát, cạnh của bounding box phải tiếp xúc chính xác tại rìa ảnh (tọa độ giới hạn chặt chẽ ở `0.0` hoặc `1.0`), không cố gắng phỏng đoán hoặc vẽ bù phần xe nằm ngoài khung hình. Chỉ gán nếu phần xuất hiện trong ảnh đủ nhận diện lớp xe.
- **Vật thể rất nhỏ/mơ hồ:** Những xe ở quá xa hậu cảnh (kích thước quá nhỏ, chiều rộng hoặc chiều cao < 10-15 pixel) hoặc bị mờ nhòe không thể phân biệt giữa car/van/truck thì không gán nhãn, nhằm đảm bảo độ tin cậy và chất lượng ground truth cao nhất cho việc huấn luyện.

## Ghi lại quyết định cho ít nhất ba ca mơ hồ

| Ảnh | Tình huống | Quyết định cuối | Lý do theo schema |
| --- | --- | --- | --- |
| `drive_003.jpg` | Xe bán tải (pickup truck) có thùng hở nhỏ phía sau chạy trên làn đường chính, dễ gây phân vân giữa `car` và `truck`. | Gán nhãn `0` (`car`) | Schema quy định rõ ràng: "sedan, SUV, taxi, xe bán tải thuộc car". Xe bán tải chỉ được xếp vào `truck` nếu là xe tải chở hàng chuyên dụng cỡ lớn có cabin tách rời thùng hàng hạng nặng. |
| `drive_007.jpg` | Xe minivan / xe van giao hàng nhỏ với trần cao và đuôi vuông đứng, ranh giới mập mờ giữa SUV/crossover cỡ lớn (`car`) và `van`. | Gán nhãn `3` (`van`) | Thiết kế xe có dạng hình hộp (boxy), trần phẳng kéo dài ra sau đuôi đứng, khoang cabin và thân sau liền khối unibody đặc trưng của dòng van chở hàng/chở khách. Schema nêu rõ: "xe van, minivan chở hàng hoặc chở người thuộc van". |
| `drive_001.jpg` | Xe chạy sát lề dưới của ảnh, bị mép camera cắt ngang chỉ còn nhìn thấy 50% phần nóc và thân trên, phần lốp xe và cản trước nằm ngoài khung hình. | Gán nhãn `0` (`car`) với cạnh dưới box chạm đúng biên ảnh `y_max = 1.0` | Phần thân trên và kính lái vẫn đủ đặc trưng để nhận diện rõ ràng là xe con. Theo quy tắc hình học: ôm sát phần nhìn thấy và chạm mép ảnh, không phỏng đoán phần bánh xe nằm ngoài ảnh. |
