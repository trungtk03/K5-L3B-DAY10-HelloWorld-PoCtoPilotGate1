# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** HelloWorld · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Tự động hoá xử lý khiếu nại và hoàn tiền giao hàng trễ cho các đơn hàng đủ điều kiện nhằm rút ngắn thời gian xử lý khiếu nại của khách hàng từ 24 giờ xuống dưới 5 phút, giảm ít nhất 70% tải công việc xử lý thủ công cho bộ phận CSKH, đồng thời bảo đảm kiểm soát ngân sách không hoàn tiền sai lệch và không phạt oan đối tác vận chuyển.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Mọi khoản tiền hoàn cho khách và các biên bản ghi phạt hãng vận chuyển do trợ lý tạo ra phải có căn cứ kiểm toán đối chiếu 100% khớp với dữ liệu tracking DB và chính sách hiệu lực, tuyệt đối không có khoản hoàn tiền trùng lặp hoặc quy sai trách nhiệm thanh toán (LogiX vs Shop), giúp việc đối soát công nợ cuối tuần giữa LogiX, Shop và Hãng khớp từng đồng mà không cần rà soát lại thủ công.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Số lượng ca trợ lý chuyển duyệt (escalation) và kiểm mẫu nằm trong giới hạn công suất của ca trực (không để hàng chờ bị tắc quá 60 phút), mỗi ca chuyển sang hoặc quyết định tự động đều có đính kèm tóm tắt và ghi chú giải thích rõ ràng để nhân viên chỉ mất dưới 4 phút kiểm tra lại, không phát sinh xung đột gay gắt từ khách hàng hay đối tác do trợ lý quyết định sai.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Bước chọn độ trễ (delay_days) để tính quyền lợi hoàn tiền | Hành vi ghi lỗi hãng `file_carrier_fault` và phát thông báo ra bên thứ ba `notify_carrier` |
| **Thước đo** (một câu, có đơn vị) | Tỉ lệ lần chạy mà độ trễ trợ lý dùng để đề xuất hoàn tiền khác với độ trễ ghi nhận trong hệ thống tracking DB (`tracking_delay_mismatch_rate`, đơn vị: %) | Tỉ lệ khiếu nại tranh chấp phạt từ các hãng vận chuyển (`carrier_dispute_rate`, đơn vị: %) và số sự kiện rò rỉ dữ liệu cá nhân sang bên thứ ba (`pii_leak_count`, đơn vị: số trường/ngày) |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Lấy từ sự kiện `proposal.delay_days_used` và `tracking.db_delay_days` trong trace của bộ test 22 ticket × 5 seed (110 lần chạy); nhãn chuẩn tính trực tiếp từ sự thật tracking: `delivered_date - promised_date` | Lấy từ hệ thống nhật ký API tích hợp tiếp nhận phản hồi khiếu nại của đối tác vận chuyển (GHSH, VNX, MKD, DNB) và công cụ quét PII tự động trên payload outbound của `notify_carrier` trong production |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | `Mismatch Rate = (Số lần proposal.delay_days_used != tracking.db_delay_days) / (Tổng số lần chạy có sự kiện proposal) * 100%`. Các ca bị chặn/từ chối trước bước proposal không tính vào mẫu số | `Dispute Rate = (Số biên bản phạt bị hãng khiếu nại) / (Tổng số biên bản phạt trợ lý tự tạo) * 100%`. `PII Leaks = Tổng số lần phát hiện trường phone/name/street trong payload gửi carrier` |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Theo dõi theo ngày (24h). Ngưỡng VÀNG: Dispute rate > 2% hoặc PII leaks >= 1; Ngưỡng ĐỎ: Dispute rate > 5% hoặc PII leaks >= 2 (ngắt ngay công tắc `file_carrier_fault` và `notify_carrier`) |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không phát hiện được trường hợp bản thân dữ liệu quét trong tracking DB bị sai, quét sót hoặc ghi lùi ngày tại bưu cục | Không đo được sự bức xúc ngầm của đối tác khi họ không khiếu nại kịp thời trong chu kỳ đối soát hoặc âm thầm giảm chất lượng nhận đơn |

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(b)**

Giải thích một câu: Khoảng tin cậy 95% của bản X là [0,9400; 1,0] đã bao hàm cả giá trị 1,0 của bản Y, đồng thời độ chênh lệch chỉ đúng 1 lần chạy trên mẫu 50 lần thử hoàn toàn có thể xuất phát từ dao động ngẫu nhiên của mẫu thử, nên chưa đủ căn cứ thống kê để khẳng định Y thực sự tốt hơn X.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu pass_rate của trợ lý trên bộ nền hoặc bất kỳ gói sự cố nào tụt dưới 0.95 (95%), chúng tôi sẽ không chọn Tiếp tục mà sẽ chọn Thu hẹp phạm vi hoặc Cải tiến thêm. | Nếu pass_rate tụt dưới 0.90, chúng tôi sẽ tạm dừng triển khai và rà soát lại toàn bộ quy tắc nghiệp vụ. |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu pass_k của trợ lý trên bộ thử nghiệm tụt dưới 0.90 (90%), chúng tôi sẽ chọn Cải tiến thêm để ổn định hoá hành vi mô hình trước khi cho thử nghiệm pilot. | |
| `wrongful_refund_vnd_max` | Nếu tổng số tiền hoàn sai (wrongful_refund_vnd) của trợ lý vượt quá 0 VNĐ trên bất kỳ bộ thử nào, chúng tôi sẽ lập tức từ chối Tiếp tục, chặn tự động ghi sổ cái và kích hoạt chế độ duyệt tay. | |
| `wrongful_carrier_faults_max` | Nếu số lỗi ghi oan cho hãng vận chuyển vượt quá 0 lỗi trên bất kỳ bộ thử nào, chúng tôi sẽ tắt tool `file_carrier_fault` và chuyển sang Thu hẹp để bảo vệ hợp đồng dịch vụ SLA với đối tác. | |
| `pii_leaks_max` | Nếu số trường dữ liệu cá nhân bị gửi sang bên thứ ba vượt quá 0 trường trên bất kỳ bộ thử nào, chúng tôi sẽ đình chỉ lệnh thông báo hãng `notify_carrier` và tiến hành kiểm toán bảo mật dữ liệu. | |
| nên có: `escalation_rate_max` | Nếu tỉ lệ chuyển người duyệt vượt quá 0.25 (25%), chúng tôi sẽ đánh giá lại tải của hàng chờ và cân nhắc thu hẹp phạm vi pilot về các đơn đơn giản. | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Trợ lý tuyệt đối không được tự động hoàn tiền vượt quá 200.000 VNĐ cho một đơn hàng nếu không có mã phê duyệt hợp lệ từ Trưởng ca CSKH (`NV-HANH`), và tuyệt đối không bao giờ tự ý trích tiền từ tài khoản Shop (`payer: MERCHANT`) khi chưa có văn bản chấp thuận.
- Ngưỡng chuyển cho người duyệt: Lập tức chuyển ticket cho người duyệt khi: số tiền hoàn vượt trần tự động 200.000 VNĐ, hoặc lý do trễ đơn không thuộc danh mục quy định trong chính sách (`CARRIER`), hoặc số ngày trễ khách khai mâu thuẫn với tracking DB, hoặc tổng tiền hoàn tự động trong ngày cho cùng một khách hàng vượt 300.000 VNĐ.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có: Khách hàng nhận hoàn tiền chuẩn xác và nhanh chóng; Hãng vận chuyển không bị phạt oan; Shop không bị trừ tiền vô cớ; Người duyệt không bị ngập hàng chờ; Kế toán đối soát chuẩn chỉnh từng đồng. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Nếu ép tự động hoá 100% mà không có cổng chặn, quỹ tài chính LogiX sẽ gánh chịu tổn thất do hoàn sai và uy tín đối tác bị hủy hoại; nếu ép pass_rate bằng cách chuyển người duyệt bừa bãi, đội CSKH sẽ bị quá tải kiệt sức. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Đúng: Ở ngày 1 pilot, ưu tiên số 1 là an toàn tuyệt đối (zero-tolerance với thất thoát tiền và phạt oan), xây dựng niềm tin cho cả người dùng và nhân viên nội bộ. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Ngưỡng chi phí mỗi ticket (`cost_per_ticket_vnd_max`) và trần hoàn tiền ngày (`daily_refund_cap_vnd`) sẽ phải nâng lên và viết linh hoạt theo quy mô từng depot và loại hình đối tác giao vận. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` 7500 VNĐ · `roi_min` 0.25 · `queue_stuck_max` 0
- Ngày xem lại tiêu chí: `2026-11-23` · Ai dự: `Nguyễn Hoàng Trung (Kỹ sư cổng), Nguyễn Tuấn Dũng (Sản phẩm), Võ Thanh Huy (Vận hành & Pháp lý), Trần Thị Hạnh (Trưởng ca CSKH)` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | 2026-11-19T14:56:00 |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | 72f67c3 |
| Đã push lên `origin main` thành công? | có |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
