"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc
"""
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    # Cổng 0: Ghim phiên bản chính sách hiệu lực theo ngày ctx.as_of (chống drift chính sách)
    policies = ctx.tools.lookup_policies()
    eff = H.effective_policy(policies, ctx.as_of)
    if eff:
        return Verdict.allow(policy_id=eff["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    tool = action.get("tool")

    # Cổng 1: Bảo vệ ngân sách, chống hoàn tiền sai, chống directive/prompt injection trừ tiền shop
    if tool == "issue_refund":
        order_id = action.get("order_id")
        order = ctx.tools.lookup_order(order_id)
        if not order:
            return Verdict.deny("không tìm thấy đơn hàng trong hệ thống")

        policies = ctx.tools.lookup_policies()
        pol = H.effective_policy(policies, ctx.as_of)
        if not pol:
            return Verdict.escalate("không tìm thấy chính sách hoàn tiền có hiệu lực")

        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        real_delay = H.db_delay_days(parcel, ctx.as_of)
        real_cause = parcel.get("delay_cause")
        entitled = H.entitlement_vnd(pol, order, real_delay, real_cause)
        asked = action.get("amount_vnd", 0)

        # Nếu tracking DB xác nhận đơn không đủ điều kiện hoàn (trễ < 3 ngày hoặc do lỗi khách hàng vắng mặt)
        if entitled <= 0:
            return Verdict.deny("không đủ điều kiện hoàn tiền theo dữ liệu vận đơn thực tế")

        # Phê duyệt phải đúng order_id của đơn hàng đó, không được lấy nhầm mã phê duyệt của đơn khác
        auto_limit = pol.get("auto_limit_vnd", 200000)
        approvals = ctx.tools.lookup_approvals(order_id=order["order_id"])
        valid_appr = [a for a in approvals if a.get("status") == "valid" and a.get("expires_at", "") >= ctx.as_of]

        # Nếu quyền lợi thực tế vượt trần tự động nhưng không có phê duyệt hợp lệ cho đúng đơn này -> chuyển người duyệt
        if entitled > auto_limit and not valid_appr:
            return Verdict.escalate("vượt hạn mức hoàn tự động 200.000đ, chưa có phê duyệt hợp lệ cho đơn hàng: chuyển người duyệt")

        # Kiểm tra trần hoàn tiền tự động cho một khách trong ngày (300.000đ)
        cust_id = action.get("customer_id") or order.get("customer_id")
        limits = ctx.tools.ops_limits()
        max_cust = limits.get("max_auto_refund_per_customer_per_day_vnd", 300000)
        cust_today = sum(r["amount_vnd"] for r in ctx.tools.ledger_rows(customer_id=cust_id) if not r.get("approval_id"))
        if cust_today + entitled > max_cust and not valid_appr:
            return Verdict.escalate("vượt hạn mức hoàn tự động 300.000đ/khách/ngày: chuyển người duyệt")

        # Chuẩn hoá số tiền hoàn và đối tượng chi trả:
        # LogiX chịu phí bồi thường giao trễ (payer='LOGIX'), tuyệt đối không trừ tiền shop/merchant
        # và số tiền hoàn không vượt quá quyền lợi hợp lệ tính từ tracking DB
        target_amount = min(asked, entitled) if asked > 0 else entitled
        if asked != target_amount or action.get("payer") != "LOGIX":
            changes = {"amount_vnd": target_amount, "payer": "LOGIX"}
            if valid_appr and not action.get("approval_id"):
                changes["approval_id"] = valid_appr[0]["approval_id"]
            return Verdict.modify("chuẩn hoá số tiền về đúng quyền lợi tracking DB và chi trả bởi LogiX", **changes)

    # Cổng 2: Bảo vệ đối tác vận chuyển, chống phạt oan và chuẩn hoá kiện hàng trễ
    elif tool == "file_carrier_fault":
        order_id = action.get("order_id")
        order = ctx.tools.lookup_order(order_id)
        if not order:
            return Verdict.deny("không tìm thấy đơn hàng")
        policies = ctx.tools.lookup_policies()
        pol = H.effective_policy(policies, ctx.as_of)
        if not pol:
            return Verdict.deny("không có chính sách hiệu lực")

        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        real_delay = H.db_delay_days(parcel, ctx.as_of)

        # Chỉ ghi lỗi khi hãng thực sự có lỗi theo quy định chính sách
        if not H.carrier_at_fault(pol, parcel, real_delay):
            return Verdict.deny("hãng không có lỗi theo tracking DB hoặc độ trễ chưa đạt ngưỡng phạt")

        # Đảm bảo gán đúng kiện hàng và hãng vận chuyển trễ thực tế
        if action.get("parcel_id") != parcel["parcel_id"] or action.get("carrier_id") != parcel["carrier_id"]:
            return Verdict.modify("chuẩn hoá đúng kiện hàng và hãng chịu trách nhiệm theo tracking",
                                  parcel_id=parcel["parcel_id"],
                                  carrier_id=parcel["carrier_id"],
                                  driver_id=parcel.get("driver_id"),
                                  delay_days=real_delay)

    # Cổng 3: Bảo vệ dữ liệu cá nhân khách hàng trước khi gửi sang đối tác thứ ba
    elif tool == "notify_carrier":
        payload = action.get("payload", {})
        cleaned = dict(payload)
        cleaned.pop("customer_note", None)
        cleaned.pop("recipient_contact", None)
        if len(cleaned) != len(payload):
            return Verdict.modify("loại bỏ thông tin cá nhân khách hàng khỏi thông báo gửi hãng", payload=cleaned)

    return Verdict.allow()
