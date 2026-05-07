REPORT - Nguyễn Tuấn Hưng
MSV: 2A202600230

Lab: Day21 - CI/CD cho AI Systems

## Bộ siêu tham số đã chọn (Bước 1)

**Siêu tham số (params.yaml)**
```yaml
n_estimators: 1200
max_depth: 20
min_samples_split: 5
```

**Lý do lựa chọn**
- `n_estimators: 1200`: Số lượng cây lớn để giảm overfitting và tăng khả năng tổng quát hóa của Random Forest.
- `max_depth: 20`: Độ sâu vừa phải cho phép mô hình học các mối quan hệ phức tạp nhưng không quá sâu gây overfitting.
- `min_samples_split: 5`: Ngưỡng tối thiểu mẫu để chia nút, giúp cân bằng giữa học từ dữ liệu và regularization.

Với bộ siêu tham số này, mô hình đạt **Accuracy: 0.752, F1: 0.7510** trên eval set — đạt ngưỡng 0.70 yêu cầu.

---

## Khó khăn gặp phải và cách giải quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| VM service không khởi động | Lỗi `BlobNotFound`: blob model chưa được upload lên Azure Blob Storage | Cập nhật `src/serve.py` để cho phép service khởi động ngay cả khi model chưa có; upload model sau đó |
| GitHub Actions pipeline không chạy | Workflow trigger chỉ cấu hình cho branch `main` nhưng repo dùng `master` | Cập nhật `.github/workflows/mlops.yml` để trigger cả hai branch: `[main, master]` |
| Train job fail tại bước "Read metrics" | F-string trong workflow viết sai cú pháp, ghi output không đúng định dạng `$GITHUB_OUTPUT` | Sửa step workflow để viết accuracy vào `$GITHUB_OUTPUT` với format đúng |
| Deploy step liên tục fail (timeout health check) | Sau `systemctl restart`, VM cần ~12s để ready nhưng workflow chỉ chờ 5s | Đổi từ `sleep 5 && curl` thành polling loop kiểm tra `/health` với retry cho đến khi 200 OK |
| Accuracy thấp (0.275 ban đầu) | Một lần chạy CI tạo metrics.json với accuracy thấp (dữ liệu hoặc cấu hình không tối ưu) | Huấn luyện lại local với `python src/train.py` để tạo metrics mới; accuracy cải thiện lên 0.752 |

---

## Tóm tắt kết quả
- Mục tiêu: Hoàn thiện Bước 1/2/3 gồm tracking (MLflow), DVC, CI/CD (GitHub Actions) và deploy mô hình trên VM.
- Kết quả chính (local):
  - Accuracy (eval): 0.752
  - F1-score (eval, weighted): 0.75096
  - Model file: models/model.pkl
  - Metrics file: outputs/metrics.json

Các bước đã thực hiện
1. Kiểm tra dữ liệu và MLflow runs: có nhiều experiment trong `mlruns/0/models/`.
2. Huấn luyện local: `python src/train.py` (sử dụng `params.yaml`) tạo `outputs/metrics.json` và `models/model.pkl`.
3. DVC: các file `data/*.dvc` đã tồn tại; `dvc push` đã được thực hiện trước đó (kiểm tra cloud storage vinunimlops2026).
4. CI/CD: `.github/workflows/mlops.yml` đã được điều chỉnh để chạy trên branch `master` và sửa các bước đọc metrics & chờ health (deploy). Pipeline chạy và deploy thành công trên VM (ứng với một run green: Test, Train, Eval, Deploy).
5. Serving: VM `http://20.210.152.100:8000/health` → `{"status":"ok"}`, và POST `/predict` trả dự đoán hợp lệ.

Tệp liên quan / bằng chứng
- metrics: [outputs/metrics.json](outputs/metrics.json)
- model: [models/model.pkl](models/model.pkl)
- MLflow experiments: [mlruns/0/models](mlruns/0/models)
- Workflow run screenshot: screenshots/ (xem các ảnh trong thư mục `screenshots`)
