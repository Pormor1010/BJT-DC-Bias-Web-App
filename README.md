# BJT DC Bias Web App

เว็บแอปพลิเคชันสำหรับคำนวณ **DC Operating Point** ของวงจรขยาย BJT Common-Emitter
พัฒนาด้วย Python + Flask — ต่อยอดจาก Lab 02 (Voltage Divider Bias) มาเป็น Lab 03
ที่เลือกวงจรไบอัสได้สามแบบ

หน้าเว็บรับค่าที่ใช้ร่วมกัน (`VCC, RC, β, VBE`) และค่าตัวต้านทานตามวงจรที่เลือก
ส่งไปให้ Python Backend คำนวณ แล้วแสดง `VB, VE, VC, VCE, IC, IE, IB`
พร้อมหน่วยและสถานะการทำงาน (Operating Region)
ผลลัพธ์ทุกค่าคำนวณสดจากสมการ ไม่ได้ฝังไว้ใน HTML

## โหมดที่รองรับ

| โหมด | อินพุตเพิ่ม | ตัวต้านทานในวงจร | ฟังก์ชัน |
|---|---|---|---|
| Voltage Divider Bias | R1, R2, RE | R1 จาก VCC ไป Base · R2 จาก Base ลงกราวด์ · RE จาก Emitter ลงกราวด์ | `solve()` |
| Fixed Bias | RB | RB จาก VCC ไป Base · Emitter ลงกราวด์โดยตรง | `fixed_bias()` |
| Emitter Bias | RB, RE | RB จาก VCC ไป Base · RE จาก Emitter ลงกราวด์ | `emitter_bias()` |

เลือกโหมดจาก dropdown แล้วกด "เปลี่ยนโหมด" — ฟอร์มจะแสดงเฉพาะช่องที่โหมดนั้นใช้
(ทำงานฝั่ง Flask ไม่ต้องใช้ JavaScript)

## สมการ

| โหมด | IB |
|---|---|
| Fixed | `(VCC − VBE) / RB` |
| Emitter | `(VCC − VBE) / [RB + (β+1)·RE]` |
| Voltage Divider | `(VTH − VBE) / [RTH + (β+1)·RE]` โดย `VTH = VCC·R2/(R1+R2)`, `RTH = R1·R2/(R1+R2)` |

จาก IB: `IC = β·IB`, `IE = (β+1)·IB`, `VE = IE·RE` (Fixed → `VE = 0`),
`VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

## Requirements

- Python 3.10 ขึ้นไป (พัฒนาบน 3.14.2)
- Flask 3.1 (ดู `requirements.txt`)

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # Linux / macOS
python -m pip install -r requirements.txt
```

## Run

```powershell
python -m flask --app app run --debug
```

เปิดเบราว์เซอร์ที่ <http://127.0.0.1:5000/>

> ต้องเปิดผ่าน Flask Server เท่านั้น การ double-click เปิด `templates/index.html`
> ด้วย `file://` จะไม่ได้ผล เพราะไม่มี Python คำนวณและไม่มี HTTP request

## Tests

```powershell
python -m unittest discover -s tests -v
```

- `tests/test_dc_bias.py` — สมการทั้งสามโหมด, validation, การตรวจ region
- `tests/test_web.py` — HTTP route ผ่าน Flask test client, การเลือกโหมด, ช่องที่ไม่ใช้

ผลรันล่าสุด: **39 tests OK**

## ค่าตรวจรับ (VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V)

| กรณี | โหมดและอินพุต | IC | VCE | สถานะ |
|---|---|---|---|---|
| A1 | Divider · R1 100 kΩ, R2 22 kΩ, RE 1 kΩ | 1.230 mA | 8.052 V | PASS |
| A2 | Fixed · RB 1 MΩ | 1.130 mA | 9.514 V | PASS |
| A3 | Emitter · RB 1 MΩ, RE 1 kΩ | 1.026 mA | 8.705 V | PASS |
| A4 | Emitter · RB 1 MΩ, RE 2 kΩ | 0.940 mA (ลดลง) | 8.033 V | PASS |
| A5 | Fixed · RB = 0 | error "ค่าความต้านทาน RB ต้องมากกว่า 0 Ω" | — | PASS |

รายละเอียด อินพุต/ค่าคาดหมาย/หลักฐาน อยู่ใน `docs/validation.md` ข้อ 6–7

## Project structure

```
app.py                  Flask routes + เลือกโหมด + แปลงหน่วย kΩ -> Ω + จัดการ error
dc_bias.py              สมการ DC bias ทั้งสามวงจร + validation + region detection
templates/index.html    ฟอร์มเลือกโหมดและตารางผลลัพธ์ (Jinja2)
static/style.css        รูปแบบหน้าเว็บ
tests/                  unittest
docs/                   design note, validation log, test log, reflection, screenshots
```

## Assumptions & limitations

- ตัวต้านทานทุกช่องกรอกเป็น **kΩ** (หน้าเว็บแปลงเป็น Ω ก่อนคำนวณ)
- ใช้สมการ Forward-Active: β คงที่, VBE คงที่, ไม่คิด Early effect และอุณหภูมิ
- ค่า VCE ต่ำกว่า 0.2 V ถือว่าเข้า Saturation และ VTH ≤ VBE ถือว่า Cutoff —
  ทั้งสองกรณีหน้าเว็บจะแสดง warning ว่าแบบจำลองนี้ใช้ตัดสินใจไม่ได้
- ไม่รองรับ AC, Transient, Bode plot หรือ SPICE (อยู่นอกขอบเขต Lab 03)

## ส่วนที่ AI ช่วยพัฒนา (Lab 03)

- เพิ่ม `fixed_bias()` และ `emitter_bias()` ใน `dc_bias.py` พร้อม helper ที่ใช้ร่วมกัน
- เพิ่มการเลือกโหมด (`if/elif`) และการอ่านเฉพาะช่องที่โหมดต้องใช้ใน `app.py`
- ปรับ `templates/index.html` ให้มี dropdown เลือกโหมดและซ่อนช่องที่ไม่ใช้
- เขียน test ใหม่ก่อนแก้ production code และปรับ `docs/validation.md`
- นักศึกษาตรวจสมการ เทียบค่ากับการคำนวณมือ และรันกรณี A1–A5 ผ่านเบราว์เซอร์เอง
