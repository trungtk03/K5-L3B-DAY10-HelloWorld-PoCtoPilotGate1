"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def model_override_rate(trials):
    """Tỉ lệ ticket có sự kiện model_override (model đè ngày trễ của ticket lên DB)."""
    count = sum(any(e.get("type") == "model_override" for e in t.get("events", [])) for t in trials)
    return count / max(1, len(trials))


def tracking_delay_mismatch_rate(trials):
    """Tỉ lệ lần chạy mà độ trễ trợ lý dùng để đề xuất hoàn tiền khác với độ trễ tracking DB."""
    count = 0
    total = 0
    for t in trials:
        events = t.get("events", [])
        prop = next((e for e in events if e.get("type") == "proposal"), None)
        track = next((e for e in events if e.get("type") == "tracking"), None)
        if prop and track:
            total += 1
            if prop.get("delay_days_used") != track.get("db_delay_days"):
                count += 1
    return count / max(1, total)


def gate_denied_rate(trials):
    """Tỉ lệ lệnh ghi bị cổng write_gate chặn (deny)."""
    count = sum(any(e.get("type") == "gate" and e.get("action") == "deny" for e in t.get("events", [])) for t in trials)
    return count / max(1, len(trials))


def queue_stuck_count(trials):
    """Tổng số ca bị ùn tắc hàng chờ quá thời hạn SLA (60 phút)."""
    return float(sum(1 for t in trials if t.get("queue_stuck")))


def high_cost_ticket_rate(trials):
    """Tỉ lệ ticket có chi phí gọi mô hình LLM cao (> 1000đ)."""
    return sum(t.get("cost_vnd", 0) > 1000 for t in trials) / max(1, len(trials))


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "model_override_rate": model_override_rate,
    "tracking_delay_mismatch_rate": tracking_delay_mismatch_rate,
    "gate_denied_rate": gate_denied_rate,
    "queue_stuck_count": queue_stuck_count,
    "high_cost_ticket_rate": high_cost_ticket_rate,
}
STARTER_MONITORS = ("escalation_rate",)
