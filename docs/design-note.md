# Design Note — BJT DC Bias Web App (ENG29 2121 Lab 02)

วันที่: 2026-11-10
ขอบเขต: อ้างอิงเอกสาร Lab 02 section 03 (Deliverable), 06 (Engineering Requirements), 09 (Acceptance Tests) เท่านั้น

## 1. โจทย์

พัฒนา Flask Web Application สำหรับวงจรขยาย BJT Common-Emitter แบบ Voltage-Divider Bias
รับค่า `VCC, R1, R2, RC, RE, β, VBE` ผ่านหน้าเว็บ ให้ Python Backend คำนวณ DC Operating Point
แล้วส่งค่ากลับมาแสดงใน Browser พร้อมหน่วย, validation และ warning เมื่ออยู่นอก Forward-Active

## 2. Goals (ตามเอกสาร Lab)

- G1 เปิดผ่าน `http://127.0.0.1:5000/` เห็น Input Form (HTTP 200)
- G2 POST แล้ว Python คำนวณจริง ไม่ใช่ค่าคงที่ใน HTML
- G3 แสดง VB, VE, VC, VCE, IC พร้อมหน่วย (และ IB/IE ตามที่เอกสารระบุว่า "ควรแสดงได้ด้วย")
- G4 Validation: R ≤ 0, β ≤ 0, VCC ≤ 0, ค่าหาย/ไม่ใช่ตัวเลข → Error ชัดเจน หน้าไม่ล้ม
- G5 Warning เมื่อ Cutoff หรือ Saturation ไม่รายงานว่า approximation ใช้ได้
- G6 Automated Tests ≥3 ตัวสำหรับ Engineering Math และ ≥1 ตัวผ่าน Flask test client
- G7 README ที่ clone แล้วติดตั้ง/รันเว็บ/รัน tests ได้

## 3. Non-goals (เอกสาร Lab ระบุว่าตัดออกจาก Week 2)

AC, Transient, Bode Plot, Signal Generator, Overlay Animation, SPICE Solver,
Bias ชนิดอื่น, FET, DC Load Line, Graph, ฐานข้อมูล, login, deploy

## 4. Anti-goals

- ฝังผลลัพธ์ตายตัวใน template หรือคำนวณใน JavaScript
- ให้ `templates/index.html` มีสมการไฟฟ้า (สมการอยู่ที่ `dc_bias.py` เท่านั้น)
- `dc_bias.py` import Flask หรือรู้จัก HTTP
- แสดงตัวเลขโดยไม่มีหน่วย หรือไม่มี warning ตอนอยู่นอก active region
- commit `.venv/`, `.env`, `__pycache__/`

## 5. Constraints

- Windows + Python 3.14.2 + Flask + `unittest` (stdlib)
- รันด้วย `python -m flask --app app run --debug` ที่ `http://127.0.0.1:5000/`
- โครงสร้างไฟล์ multi-file ตามเอกสาร Lab
- Commit/Push ผ่าน GitHub Desktop

## 6. Approaches ที่พิจารณา

| ทางเลือก | ข้อดี | ข้อเสีย | สรุป |
|---|---|---|---|
| **A) โชว์ค่าตามสมการ + warning** | อยู่ในขอบเขตเวลา, ตรงถ้อยคำ handout, test ง่าย | ตัวเลขอาจดูสมเหตุสมผลทั้งที่ผิด | **เลือก** |
| B) คำนวณซ้ำแบบอิ่มตัว (ตรึง VCE=0.2V) | ใกล้ความจริงกว่า | เกินขอบเขต DC Bias approximation ที่เอกสารกำหนด | ไม่เลือก |
| C) ไม่โชว์ตัวเลข | ปลอดภัยสุด | ขัด A2 ที่ต้องเห็นผล DC Bias | ไม่เลือก |

## 7. การตัดสินใจ

| หัวข้อ | ข้อสรุป |
|---|---|
| Framework | Flask + Jinja2 (ไม่ใช้ JS) |
| หน่วยอินพุต R | ฟอร์มรับ **kΩ** → route แปลงเป็น Ω ก่อนเรียก `dc_bias` |
| หน่วยภายใน `dc_bias.py` | SI: Ω, V, A |
| Route | `GET /` ฟอร์ม, `POST /calculate` คำนวณและแสดงผล |
| ผลลัพธ์บนหน้าจอ | VB, VE, VC, VCE [V] · IC, IB, IE [mA] · Operating Region |
| ค่า VTH/RTH | ใช้ภายในโมดูล (สำหรับ test) ไม่แสดงบนหน้าจอ |
| Cutoff (VTH ≤ VBE) | IB=IC=IE=0, VE=0, VB=VTH, VC=VCC, VCE=VCC, region=cutoff |
| Saturation | VCE < 0.2 V → region=saturation |
| Active | VTH > VBE และ VCE ≥ 0.2 V |
| Input ผิด | HTTP 200 + error block ใต้ฟอร์ม |
| ค่าที่ผิด | R ≤ 0, β ≤ 0, VCC ≤ 0, VBE ≤ 0, VBE ≥ VCC, ค่าว่าง, แปลง float ไม่ได้ |
| การปัดเศษ | แรงดัน 3 ตำแหน่งทศนิยม (V), IC/IE 3 ตำแหน่ง (mA), **IB 3 ตำแหน่ง (µA)** |
| ภาษา UI | ป้ายไทย + หน่วยอังกฤษ |
| ค่าเริ่มต้นฟอร์ม | VCC=12, R1=100, R2=22, RC=2.2, RE=1, β=100, VBE=0.70 |
| Tests | `unittest`, `python -m unittest discover -s tests -v` |

## 8. สมการ (ตามเอกสาร Lab ข้อ 06)

```
VTH = VCC * R2 / (R1 + R2)
RTH = R1 * R2 / (R1 + R2)
IB  = (VTH - VBE) / (RTH + (beta + 1) * RE)
IC  = beta * IB
IE  = (beta + 1) * IB
VE  = IE * RE
VB  = VE + VBE
VC  = VCC - IC * RC
VCE = VC - VE
```

สมมติฐาน: Forward-Active, β คงที่, VBE คงที่ (ไม่คิด Early effect/อุณหภูมิ)

### ค่าอ้างอิงสำหรับตรวจ (ข้อมูลทดลองเริ่มต้นของเอกสาร)
Input: VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

| ปริมาณ | ค่า |
|---|---|
| VTH | 2.163934 V |
| RTH | 18.032787 kΩ |
| IB | 12.29868 µA |
| IC | 1.229868 mA |
| IE | 1.242167 mA |
| VE | 1.242167 V |
| VB | 1.942167 V |
| VC | 9.294290 V |
| VCE | 8.052123 V |
| Region | active |

Tolerance: `assertAlmostEqual(..., places=4)`

## 9. โครงสร้างไฟล์ (ตรงตามเอกสาร Lab)

```
app.py                  # Flask routes + แปลงหน่วย + จัดการ error
dc_bias.py              # สมการ + validation + region (ไม่ import Flask)
templates/index.html    # ฟอร์ม + ผลลัพธ์ + error/warning (Jinja)
static/style.css
tests/test_dc_bias.py
tests/test_web.py
requirements.txt
README.md
AGENTS.md
docs/
├── design-note.md      # เอกสารนี้
├── validation.md       # ผลตรวจค่าอ้างอิง + test log
└── reflection.md       # สิ่งที่เรียนรู้
```

## 10. Data contract

```python
class BiasError(ValueError): ...

VCE_SAT = 0.2  # V

def solve(vcc, r1, r2, rc, re, beta, vbe) -> dict:
    # รับ SI (V, Ω), คืน dict ของ float (V, Ω, A) + region + warnings
    # raise BiasError เมื่อ input ไม่ผ่าน validation
```

Route `POST /calculate`: อ่าน form → แปลง float → คูณ R ด้วย 1000 → `solve()` →
แปลงหน่วยแสดงผล → render `index.html` (error → 200 + error block)

## 11. Test plan

`tests/test_dc_bias.py`
1. `test_reference_operating_point` — ตรงตารางข้อ 8
2. `test_region_active_no_warning` — region=active, warnings=[]
3. `test_cutoff` — VTH ≤ VBE → IC=0, region=cutoff
4. `test_saturation_warning` — RC สูง (47 kΩ) → VCE<0.2, warnings ไม่ว่าง
5. `test_invalid_inputs` — R≤0, β≤0, VCC≤0, VBE≥VCC → BiasError

`tests/test_web.py`
1. `test_get_index` — 200 + มี name="vcc"
2. `test_post_computes` — POST ค่าอ้างอิง → 200 + มี `8.052` และ `1.230`
3. `test_post_invalid` — VCC=0 → 200 + error
4. `test_post_non_numeric` — vcc="abc" → 200 + error

## 12. ตรวจรับ A1–A7

| # | วิธีพิสูจน์ |
|---|---|
| A1 | GET / → 200 + เห็นฟอร์ม |
| A2 | POST /calculate → มีค่าคำนวณใน HTML |
| A3 | ตรงตารางข้อ 8 |
| A4 | test_post_invalid, test_post_non_numeric |
| A5 | test_cutoff, test_saturation_warning + แถบ warning |
| A6 | engineering 5 ตัว + Flask client 4 ตัว |
| A7 | README ครบขั้นตอน |

## 13. สิ่งที่เหลือให้ผู้สร้างตัดสินใจ

- โทนสี/ฟอนต์/ระยะห่างใน `style.css`
- ถ้อยคำข้อความ error/warning ภาษาไทย
- ลำดับแถวในตารางผลลัพธ์

## 14. เอกสารประกอบ (ตามเอกสาร Lab ข้อ 04 และ Rubric ข้อ 5)

| ไฟล์ | เนื้อหา | ใครเขียน |
|---|---|---|
| `README.md` | วิธีติดตั้ง/รันเว็บ/รัน tests | ผู้สร้าง |
| `AGENTS.md` | กติกาโค้ดสำหรับ AI | ผู้สร้าง |
| `docs/design-note.md` | เอกสารนี้ + เหตุผลของแบบจำลอง | ผู้สร้าง |
| `docs/validation.md` | ตารางค่าอ้างอิง vs ค่าที่เว็บให้ + test log | ผู้สร้าง (กรอกผลจริง) |
| `docs/reflection.md` | สิ่งที่นิสิตเรียนรู้ | **นิสิตเขียนเอง** (ผู้สร้างใส่หัวข้อ/คำถามให้) |

## 15. หลักฐานส่งงาน (เอกสาร Lab ข้อ 10)

Repository URL + Commit SHA + ภาพหน้าจอเว็บที่คำนวณสำเร็จ + Test Log
(รวบรวมตอนท้าย ไม่ใช่ส่วนของโค้ด)

