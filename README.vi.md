# CKD Cohort Lab

[English](README.md) · **Tiếng Việt** · [日本語](README.ja.md) · [中文](README.zh.md) · [Français](README.fr.md)

**Kiểm tra dữ liệu bệnh thận trước khi phân tích, rồi xác định ai thật sự cần xét nghiệm albumin niệu.**

CKD Cohort Lab gồm một công cụ chạy trên trình duyệt và bộ script Python đi kèm bản thảo *“One value or a distribution? Routine urine dipsticks to target albuminuria testing for kidney failure risk”* (đã nộp). Nghiên cứu gồm 129 bệnh nhân ngoại trú mắc bệnh thận mạn (CKD) G3–G5 tại Bệnh viện Đa khoa Lãnh Binh Thăng, Thành phố Hồ Chí Minh, Việt Nam.

- **Công cụ trực tuyến:** https://ckdco.netlify.app/?lang=vi
- **Mã nguồn:** https://github.com/lamkienthanh92/ckdcohortlab
- **Lưu trữ và trích dẫn:** https://doi.org/10.5281/zenodo.24189503 (phiên bản 1.2.0; trang Zenodo liệt kê mọi phiên bản)

> Công cụ dùng cho nghiên cứu và giảng dạy, không phải thiết bị y tế. Phương trình nguy cơ suy thận (KFRE) chưa được kiểm định ở bệnh nhân Việt Nam.

## Công cụ làm gì

Giao diện có 5 ngôn ngữ: tiếng Anh, tiếng Việt, tiếng Nhật, tiếng Trung và tiếng Pháp. Chọn ngôn ngữ ở thanh trên cùng, hoặc thêm `?lang=en`, `vi`, `ja`, `zh` hay `fr` vào địa chỉ; mặc định là tiếng Anh, và trình duyệt sẽ ghi nhớ lựa chọn.

1. **Nạp dữ liệu:** file Excel (.xlsx, .xls, .ods) hoặc CSV, mỗi dòng một bệnh nhân. Có thể ghép thêm một file thứ hai (ví dụ kết quả tổng phân tích nước tiểu) theo mã bệnh nhân. Tên cột thông dụng (tiếng Anh) được khớp tự động và có thể chỉnh tay; cột đơn vị đặt tên “Unit <tên cột>” (ví dụ “Unit PRO”) được đọc theo từng dòng.
2. **Kiểm tra phân bố:** mọi cột được tóm tắt trước khi tính: độ đầy đủ, phân bố, giá trị bị Excel lưu thành ngày, giá trị ngoài khoảng, mã trùng, ACR nhập so với albumin ÷ creatinin, eGFR nhập so với CKD-EPI 2021. Có thể tải dữ liệu đã làm sạch dạng CSV.
3. **Kết quả:** KFRE (4 biến, hiệu chỉnh ngoài Bắc Mỹ), phân loại KDIGO 2024, độ chính xác của que thử so với ACR (chung và theo từng máy), và cách phân loại theo phân bố:
   - chỉ bỏ qua ACR xét nghiệm khi toàn bộ khoảng dự báo của KFRE nằm về một phía của ngưỡng (5 năm ≥3% và >5%; 2 năm >10% và >40%);
   - so sánh với cách quy đổi que thử thành một giá trị ACR;
   - chọn khoảng 80/90/95/99%, có hoặc không có biến loại máy;
   - kiểm định bằng chia ngẫu nhiên 70/30 và chéo giữa các máy;
   - chi phí xét nghiệm trực tiếp, sửa được giá;
   - so sánh KFRE 5 năm ở mức quần thể và từng bệnh nhân;
   - albumin niệu nằm ngoài khoảng 99%, để kiểm tra lại đúng mẫu.

**Bảo mật:** file chỉ được đọc trong trình duyệt. Không có gì được tải lên hay lưu trên máy chủ; đóng trang là dữ liệu bị xóa. Hãy bỏ tên và thông tin định danh trước khi nạp.

Có thể thử với `examples/example_synthetic.csv` (140 bệnh nhân giả lập, không phải dữ liệu thật).

## Tái lập các phân tích của bản thảo

```bash
cd analysis
pip install -r requirements.txt
python triage_analysis.py --data ../examples/example_synthetic.csv --out results
python make_figures.py   --data ../examples/example_synthetic.csv --out figures
```

Trên dữ liệu nghiên cứu, các script cho đúng các con số đã báo cáo (ví dụ: với khoảng 90%, 66/129 bệnh nhân cần ACR xét nghiệm, 2 bệnh nhân có quyết định sai, 25 bệnh nhân sai khi quy đổi một giá trị). Dữ liệu nghiên cứu không kèm theo; xem mục *Dữ liệu*. Định dạng đầu vào và các tùy chọn được mô tả (bằng tiếng Anh) trong `analysis/README.md`.

## Phương pháp tóm tắt

Log ACR được dự đoán bằng hồi quy bình phương tối thiểu từ tuổi, giới, eGFR và đái tháo đường (mô hình lâm sàng), cộng thêm mức protein que thử, tỷ trọng và loại máy (mô hình que thử), theo kiểm định chéo bỏ-từng-ca. Khoảng dự báo là giá trị dự đoán ± z·s·√(1 + x′(X′X)⁻¹x). Vì KFRE tăng theo ACR, KFRE được tính ở hai đầu khoảng; một ngưỡng chỉ được quyết định mà không cần ACR xét nghiệm khi cả hai đầu nằm cùng một phía.

## Cấu trúc kho mã

| Đường dẫn | Nội dung |
|---|---|
| `index.html` | Công cụ trên trình duyệt (một file, không cần bước build) |
| `vendor/` | React 18.3.1 và SheetJS 0.18.5, đóng gói sẵn để không phụ thuộc máy chủ script bên ngoài |
| `examples/` | Dữ liệu mẫu giả lập và script tạo ra nó |
| `analysis/` | Script Python tái lập bảng và hình của bản thảo |
| `netlify.toml` | Thiết lập Netlify (trang tĩnh, không build) |
| `CITATION.cff`, `.zenodo.json` | Thông tin trích dẫn cho GitHub và Zenodo |

## Dữ liệu

Kho mã không chứa dữ liệu bệnh nhân. Bộ dữ liệu nghiên cứu đã khử định danh có thể được cung cấp theo yêu cầu hợp lý gửi tác giả liên hệ, sau khi được Hội đồng Đạo đức của Bệnh viện Đa khoa Lãnh Binh Thăng chấp thuận.

## Trích dẫn

> Nguyen ATT, Pham TA, Phan HD, Phan TC, Lam TH, Huynh NH, Tran HNT, Lam TK, Le CV. CKD Cohort Lab: browser tool and analysis code for distribution-based albuminuria triage (version 1.3.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24189503

## Giấy phép

Mã nguồn: MIT (xem `LICENSE`). Các thành phần của bên thứ ba giữ giấy phép riêng (xem `ATTRIBUTION.md`).
