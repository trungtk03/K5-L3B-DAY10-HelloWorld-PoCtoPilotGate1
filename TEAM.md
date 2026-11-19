# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): HelloWorld
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-HelloWorld-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S2

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Nguyễn Hoàng Trung | 2A202603826 | Kỹ sư cổng | x |
|   2 | Nguyễn Tuấn Dũng | 2A202603859 | Sản phẩm và kinh doanh | |
|   3 | Võ Thanh Huy | 2A202603879 | Vận hành và pháp lý | |
|   4 | | | | |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên:
`["NguyenHoangTrung-2A202603826", "NguyenTuanDung-2A202603859", "VoThanhHuy-2A202603879"]`

## Cá nhân

## NguyenHoangTrung-2A202603826

### Phần việc phụ trách

- Vai: Kỹ sư cổng, Trưởng nhóm.
- Phụ trách câu 1.3 (Phiếu A mục A2), câu 2.1, 2.2, 2.6, 2.7, 2.8 (Phiếu B mục B0, B1, B2, B7.1, B7.2, B7.3), câu 3.1 trace, câu 3.5, 3.6 (Phiếu C mục C2, C7, C8).
- File code chính: `lab10/guards.py`, `lab10/monitors.py`.
- Thực hiện chạy các lệnh eval, gate, trace, criteria sign, checkpoint, grade, check_submission.

### Đóng góp cụ thể

- Thiết kế offline metric cho bước chọn độ trễ và tính toán tiền hoàn.
- Dò trace ca lỗi `T-002@55`, phát hiện lỗi chìm do model override độ trễ dựa trên lời khai khách hàng thay vì tra cứu tracking DB.
- Cài đặt 3 cổng phòng ngừa trong `lab10/guards.py`: ghim chính sách hiệu lực qua `pre_guard`, đối chiếu số tiền hoàn với `entitlement_vnd` từ DB sự thật, kiểm tra điều kiện ghi lỗi hãng `carrier_at_fault` và đối chiếu tracking trong `write_gate`.
- Viết 2 behavioral test (ticket hiểm) kiểm tra tính chất bảo vệ chống gian lận độ trễ và chống directive bồi thường toàn bộ sai quy định.
- Thêm chỉ số theo dõi mới trong `lab10/monitors.py`.

### Bằng chứng

- Commit ký tiêu chí, commit chốt vòng 1.
- Các mã lần chạy trong `runs/` (baseline, after, prepared).
- Các dòng trace `T-002@55` và behavioral test adhoc.

### Exit ticket

- Một điều học được: Cổng an toàn cấp hệ thống (system-level guard) nằm ngoài model/prompt là phòng tuyến quyết định bảo vệ doanh nghiệp trước prompt injection, model hallucination và dữ liệu sai lệch.
- Một điều còn chưa chắc: Cách cân bằng tối ưu giữa việc chuyển người duyệt (escalate) để đảm bảo 100% an toàn và chi phí vận hành hàng chờ khi khối lượng giao dịch đột biến gấp nhiều lần.

---

## NguyenTuanDung-2A202603859

### Phần việc phụ trách

- Vai: Sản phẩm và kinh doanh.
- Phụ trách câu 1.1, 1.6 (Phiếu A mục A1, A4), câu 2.3, 2.9 (Phiếu B mục B3, B7.4, B8 - quyết định v1), câu 3.2, 3.5 (Phiếu C mục C5, C7, C12 - quyết định v2).
- File cấu hình: `config/acceptance_criteria.json`, `config/operating_gates.json` (mục `business`).

### Đóng góp cụ thể

- Xác định mục tiêu cấp hệ thống của trợ lý gắn liền với chi phí, thời gian hoàn trả và trải nghiệm khách hàng.
- Xây dựng bản tiêu chí chấp nhận với đầy đủ các ngưỡng bắt buộc (`pass_rate_min`, `pass_k_min`, `wrongful_refund_vnd_max=0`, `wrongful_carrier_faults_max=0`, `pii_leaks_max=0`), ngưỡng `business_ops` (`cost_per_ticket_vnd_max`, `roi_min`, `queue_stuck_max=0`) và quy tắc ra quyết định 4 nhánh.
- Lập bản đồ dữ liệu và phân tích hiện tượng drift chính sách (chuyển đổi sang `REFUND-v4` từ 01/12/2026).
- Thiết lập các cổng kinh doanh trong `config/operating_gates.json`: `daily_refund_cap_vnd`, `cost_budget_per_ticket_vnd`, `pilot_scope`, `roi_min` dựa trên dữ liệu vận hành từ `data/world.json`.
- Cùng bàn thảo luận và chốt quyết định Gate 1 v1 và v2 dựa trên bằng chứng đo lường.

### Bằng chứng

- File `config/acceptance_criteria.json` và mã hash khóa `acceptance_criteria.lock`.
- Mục `business` trong `config/operating_gates.json`.
- Các mục A1, A4 trong Phiếu A, B3, B7.4, B8 trong Phiếu B, C5, C12 trong Phiếu C.

### Exit ticket

- Một điều học được: Một sản phẩm AI không chỉ được đánh giá bằng độ chính xác (accuracy/pass rate) mà phải đo lường bằng bài toán ROI, chi phí biên trên mỗi ticket và giới hạn thiệt hại tài chính tối đa.
- Một điều còn chưa chắc: Chiến lược mở rộng quy mô (scale-up) pilot từ 2 kho lên toàn quốc khi các kho vệ tinh có đối tác vận chuyển địa phương với chất lượng dịch vụ rất khác nhau.

---

## VoThanhHuy-2A202603879

### Phần việc phụ trách

- Vai: Vận hành và pháp lý.
- Phụ trách câu 1.2, 1.4 (Phiếu A mục A1, A2), câu 2.4, 2.10 (Phiếu B mục B4, B5, B7.5, B7.6), câu 3.1, 3.3, 3.7 (Phiếu C mục C4, C5, C9, C10, C11).
- File cấu hình và bài nộp: `config/operating_gates.json` (mục `operations`, `legal`), `submission/submission.json`.
- Soạn thảo Runbook phần 1–3, mục Giờ cao điểm, và Runbook phần 4–5.

### Đóng góp cụ thể

- Xác định mục tiêu từ góc nhìn của kế toán đối soát (chị Oanh) và trưởng ca CSKH (chị Hạnh).
- Thiết kế telemetry production giám sát rò rỉ dữ liệu cá nhân (PII) và tỷ lệ khiếu nại từ hãng vận chuyển.
- Thực hiện phân tích HAZOP mở rộng trên tool ghi `issue_refund` và các thành phần ngoài kỹ thuật (người duyệt, ngân sách, bên thứ ba).
- Hoàn thiện checklist go-live 9 nhóm việc có đầy đủ PIC cụ thể.
- Cấu hình các cổng vận hành và pháp lý (`operations.pic`, `approver_id`, `reviewers_on_shift`, `pii_fields_blocked_to_third_party`, `carrier_fault_requires_recorded_cause`).
- Soạn thảo runbook chi tiết về quy trình ứng phó sự cố, phân định thẩm quyền và quy trình xử lý giờ cao điểm.

### Bằng chứng

- File `config/operating_gates.json` (mục `operations`, `legal`).
- Nội dung Runbook và Checklist trong Phiếu B (B4, B5, B7.5, B7.6) và Phiếu C (C4, C11).
- File `submission/submission.json`.

### Exit ticket

- Một điều học được: Trách nhiệm pháp lý và bảo vệ dữ liệu cá nhân (tránh gửi PII cho hãng vận chuyển) cùng với việc bảo vệ quyền lợi đối tác thứ ba là điều kiện tiên quyết để hệ thống AI được vận hành ngoài đời thực.
- Một điều còn chưa chắc: Cách ứng phó pháp lý khi có sự bất đồng dữ liệu giữa tracking của đơn vị vận chuyển bên ngoài và khiếu nại thực tế từ phía người nhận hàng quà tặng.
