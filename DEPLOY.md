# Deploy & Build Guide (fast + cached pip) 

Mục tiêu: build image `spark-worker` nhanh, tái sử dụng cache pip và dùng mirror PyPI (Tsinghua) để tăng tốc tại châu Á.

1) Kiểm tra
- Đảm bảo `requirements.txt` chứa các package cần thiết.
- Nếu cần nhiều wheels offline, xem phần Wheelhouse.

2) Build & up (PowerShell, khuyến nghị)

Bật BuildKit và build + up:

```powershell
$env:DOCKER_BUILDKIT = "1"; .\build_images.ps1
```

Lệnh này:
- Dùng BuildKit để cache pip downloads
- Build image `spark-worker` dựa trên `Dockerfile.spark-worker`
- Tạo volume `pip-cache` để lưu cache pip

3) Các lệnh thường dùng

- Kiểm tra status:
```powershell
docker-compose ps
```

- Xem logs:
```powershell
docker-compose logs -f spark-worker
```

- Nếu cần cài gói tạm trong container:
```powershell
docker exec -it spark-worker python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --prefer-binary <package>
```

- Nếu muốn xóa volumes (thao tác destructive):
```powershell
docker-compose down -v
```
Chỉ dùng khi bạn muốn xóa cache pip hoặc reset hoàn toàn.

4) Wheelhouse (tùy chọn)
- Để build offline hoặc mạng rất chậm, tải wheel trên máy có mạng tốt:

```bash
pip download -r requirements.txt -d wheelhouse -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

- Sau đó COPY `wheelhouse` vào repo và chỉnh Dockerfile để `pip install --no-index --find-links=/opt/wheelhouse -r /opt/requirements.txt`.

5) Troubleshooting
- Nếu build lỗi do thiếu thư viện hệ thống (ví dụ lỗi khi cài Pillow, matplotlib), mở `Dockerfile.spark-worker` và thêm package hệ thống tương ứng (ví dụ libjpeg-dev).
- Kiểm tra container bằng:
```powershell
docker exec spark-worker python3 -c "import matplotlib; print(matplotlib.__version__)"
```

6) Ghi chú
- Mình đã cấu hình Dockerfile để đặt pip mirror mặc định (Tsinghua) và cài một số thư viện hệ thống thông dụng. Thực tế các package yêu cầu có thể khác nhau; nếu bạn gặp lỗi build, gửi log lỗi và mình sẽ điều chỉnh `Dockerfile.spark-worker`.
