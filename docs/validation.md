# Validation — BJT DC Bias Web App

วันที่ตรวจ: 2026-11-10

## 1. ค่าอ้างอิงทางวิศวกรรม vs ค่าที่เว็บแสดง

ข้อมูลทดลองเริ่มต้น: `VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ, β = 100, VBE = 0.70 V`

ค่าอ้างอิงคำนวณด้วยมือจากสมการ Forward-Active ใน `docs/design-note.md` ข้อ 8

| ปริมาณ | ค่าคำนวณด้วยมือ | ค่าที่เว็บแสดง | ตรงกัน |
|---|---|---|---|
| VB | 1.942167 V | 1.942 V | ✅ |
| VE | 1.242167 V | 1.242 V | ✅ |
| VC | 9.294290 V | 9.294 V | ✅ |
| VCE | 8.052123 V | 8.052 V | ✅ |
| IC | 1.229868 mA | 1.230 mA | ✅ |
| IE | 1.242167 mA | 1.242 mA | ✅ |
| IB | 12.29868 µA | 12.299 µA | ✅ |
| Operating Region | active | active | ✅ |

## 2. การทดสอบอัตโนมัติ

คำสั่ง: `python -m unittest discover -s tests -v`

```
Ran 19 tests in 0.036s
OK
```

| ไฟล์ | จำนวน | ครอบคลุม |
|---|---|---|
| `tests/test_dc_bias.py` | 9 | ค่าอ้างอิง, validation, region (active/cutoff/saturation), การแปลงค่าที่ไม่ใช่ตัวเลข/NaN/Inf |
| `tests/test_web.py` | 10 | GET ฟอร์ม, POST คำนวณ, input ผิด 3 กรณี, ป้ายภาษาไทย, region ภาษาไทย, warning block, IB หน่วย µA, รูปแบบเซลล์ VCE |

## 3. การทดสอบผ่าน HTTP จริง (ไม่ใช่ test client)

รัน `python -m flask --app app run --port 5000` แล้วยิง request จริง

| การทดสอบ | ผล |
|---|---|
| `GET /` | 200 และพบ `name="vcc"` |
| `POST /calculate` (ค่าอ้างอิง) | 200, พบ `8.052` (VCE) และ `1.230` (IC) |
| `POST /calculate` (VCC = 0) | 200 และแสดงข้อความ "ข้อผิดพลาด" |

## 4. กรณีอยู่นอก Forward-Active

| กรณี | อินพุต | ผลที่ได้ |
|---|---|---|
| Cutoff | `R2 = 1 kΩ` (VTH ≈ 0.119 V < VBE) | IC = 0, VCE = 12 V, region = cutoff, มี warning |
| Saturation | `RC = 47 kΩ` (VCE < 0.2 V) | region = saturation, มี warning ว่าใช้ค่าจาก Forward-Active ไม่ได้ |

หมายเหตุ: ค่าที่แสดงในสองกรณีนี้มาจากสมการ Forward-Active เช่นเดิม ตามแนวทาง A
ของ design note — ตัวเลขใช้ดูพฤติกรรมของสมการเท่านั้น ไม่ใช่ค่าที่เชื่อถือได้
