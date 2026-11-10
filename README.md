# BJT DC Bias Web App

เว็บแอปพลิเคชันสำหรับคำนวณ **DC Operating Point** ของวงจรขยาย BJT Common-Emitter
แบบ **Voltage-Divider Bias** พัฒนาด้วย Python + Flask สำหรับรายวิชา ENG29 2121 Lab 02

หน้าเว็บรับค่า `VCC, R1, R2, RC, RE, β, VBE` ส่งไปให้ Python Backend คำนวณ
แล้วแสดง `VB, VE, VC, VCE, IC, IE, IB` พร้อมหน่วยและสถานะการทำงาน (Operating Region)
ผลลัพธ์ทุกค่าคำนวณสดจากสมการ ไม่ได้ฝังไว้ใน HTML

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

- `tests/test_dc_bias.py` — สมการ, validation, การตรวจ region
- `tests/test_web.py` — HTTP route ผ่าน Flask test client

## Project structure

```
app.py                  Flask routes + แปลงหน่วย kΩ -> Ω + จัดการ error
dc_bias.py              สมการ DC bias + validation + region detection
templates/index.html    ฟอร์มและตารางผลลัพธ์ (Jinja2)
static/style.css        รูปแบบหน้าเว็บ
tests/                  unittest
docs/                   design note, validation log, test log, reflection, screenshots
```

## Assumptions & limitations

- ตัวต้านทานทั้งสี่ช่องกรอกเป็น **kΩ** (หน้าเว็บแปลงเป็น Ω ก่อนคำนวณ)
- ใช้สมการ Forward-Active: β คงที่, VBE คงที่, ไม่คิด Early effect และอุณหภูมิ
- ค่า VCE ต่ำกว่า 0.2 V ถือว่าเข้า Saturation และ VTH ≤ VBE ถือว่า Cutoff —
  ทั้งสองกรณีหน้าเว็บจะแสดง warning ว่าแบบจำลองนี้ใช้ตัดสินใจไม่ได้
- ไม่รองรับ AC, Transient, Bode plot หรือ SPICE (อยู่นอกขอบเขต Lab 02)
