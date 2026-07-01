
def classify(desc, amount):
    desc = desc.upper()

    # ✅ เงินเข้า (สำคัญมาก)
    if any(x in desc for x in [
        "PPSDTR",       # โอนเข้า
        "MOSD",         # ฝากผ่าน MyMo
        "ATSDC",        # ฝากเงินสด (ตัวนี้แหละพัง!!)
        "รับ",          # เผื่อภาษาไทย
    ]):
        return amount, 0

    # ✅ เงินออก
    if any(x in desc for x in [
        "MPPOFF",       # โอนออก
        "MASWC",        # ATM ถอน
        "ถอน",
        "PAYMENT",
    ]):
        return 0, amount

    # ✅ default fallback
    return 0, amount
