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
Ran 39 tests in 0.043s
OK
```

| ไฟล์ | จำนวน | ครอบคลุม |
|---|---|---|
| `tests/test_dc_bias.py` | 17 | ค่าอ้างอิงทั้งสามโหมด, validation, region (active/cutoff/saturation), การแปลงค่าที่ไม่ใช่ตัวเลข/NaN/Inf, RE ที่มากขึ้นต้องลด IC |
| `tests/test_web.py` | 22 | GET ฟอร์ม, POST คำนวณทั้งสามโหมด, input ผิด, โหมดที่ไม่รู้จัก, ช่องที่ไม่ใช้ไม่ถูกบังคับ, ป้ายภาษาไทย, region ภาษาไทย, warning block, IB หน่วย µA, รูปแบบเซลล์ VCE |

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

## 5. หลักฐานประกอบการส่ง

รันเว็บด้วย `python -m flask --app app run --port 5000` แล้วจับภาพหน้าจอจริง
จากเบราว์เซอร์ (ขนาดเต็มหน้า)

| ไฟล์ | เนื้อหา |
|---|---|
| `docs/screenshots/01-form.jpeg` | หน้าแรก แสดงฟอร์ม 7 ช่อง พร้อมคำอธิบายภาษาไทยและปุ่ม "คำนวณ DC Bias" |
| `docs/screenshots/02-result.jpeg` | ผลลัพธ์ค่าอ้างอิง: VB 1.942 V · VE 1.242 V · VC 9.294 V · VCE 8.052 V · IC 1.230 mA · IE 1.242 mA · IB 12.299 µA · Active (ทำงานปกติ) |
| `docs/screenshots/03-invalid-input.jpeg` | กรอก VCC = 0 → แถบ error "ข้อผิดพลาด: VCC ต้องมากกว่า 0 V" (HTTP 200) |
| `docs/screenshots/04-saturation-warning.jpeg` | ตั้ง RC = 47 kΩ → region = Saturation (อิ่มตัว) พร้อม warning |

`docs/test-log.txt` เก็บผลรัน `python -m unittest discover -s tests -v`
จากเครื่องที่พัฒนา (39 tests, OK) เพื่อใช้อ้างอิงคู่กับตารางข้อ 2

## 6. Lab 03 — ตารางตรวจรับ A1–A5

ใช้ร่วมกันทุกกรณี: `VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V`
เกณฑ์: IC คลาดเคลื่อน ≤ 0.01 mA · VCE ≤ 0.02 V เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ

ค่าอ้างอิงของโหมดใหม่คำนวณด้วยมือ (ไม่ใช้ผลจากโปรแกรม):

- **A2 Fixed Bias** (RB = 1 MΩ): `IB = (12 − 0.7)/1,000,000 = 11.300 µA` ·
  `IC = 100 × IB = 1.130 mA` · `IE = 101 × IB = 1.141 mA` · `VE = 0 V` ·
  `VB = 0.700 V` · `VC = 12 − 1.130 mA × 2.2 kΩ = 9.514 V` · `VCE = 9.514 V`
- **A3 Emitter Bias** (RB = 1 MΩ, RE = 1 kΩ): `IB = 11.3/(1,000,000 + 101 × 1,000) = 10.263 µA` ·
  `IC = 1.0263 mA` · `VE = 101 × IB × 1 kΩ = 1.0366 V` · `VB = 1.7366 V` ·
  `VC = 12 − 1.0263 mA × 2.2 kΩ = 9.7421 V` · `VCE = 8.7054 V`
- **A4 Emitter Bias** (เหมือน A3 แต่ RE = 2 kΩ): `IB = 11.3/1,202,000 = 9.401 µA` ·
  `IC = 0.9401 mA` (ลดลงจาก A3) · `VCE = 8.0328 V`

| กรณี | โหมดและอินพุต | คาดหมายก่อนรัน | เห็นจริง | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 | Divider · R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ | ผลเดิมของ Lab 02: IC 1.230 mA · VCE 8.052 V | IC 1.230 mA · VCE 8.052 V · VB 1.942 V · VE 1.242 V · VC 9.294 V · Active | OpenCode Browser | PASS |
| A2 | Fixed · RB = 1 MΩ (1000 kΩ) | IC 1.130 mA · VCE 9.514 V (ไม่ต้องกรอก RE) | IC 1.130 mA · VCE 9.514 V · VB 0.700 V · VE 0.000 V · IB 11.300 µA | OpenCode Browser | PASS |
| A3 | Emitter · RB = 1 MΩ, RE = 1 kΩ | IC 1.0263 mA · VCE 8.7054 V | IC 1.026 mA · VCE 8.705 V · VE 1.037 V · IB 10.263 µA | OpenCode Browser | PASS |
| A4 | Emitter · เหมือน A3 แต่ RE = 2 kΩ | ทำนาย: IC ลดลง เพราะ RE มากขึ้นทำให้ IB = (VCC−VBE)/(RB+(β+1)RE) ลดลง | IC 0.940 mA (ลดจาก 1.026 mA) · VCE 8.033 V · VE 1.899 V | OpenCode Browser | PASS |
| A5 | Fixed · RB = 0 | มีข้อความให้แก้ RB เว็บไม่ล่ม และไม่แสดงผลรอบก่อน | "โหมด: Fixed Bias — ข้อผิดพลาด: ค่าความต้านทาน RB ต้องมากกว่า 0 Ω" ไม่มีตารางผลลัพธ์ | OpenCode Browser | PASS |

หมายเหตุวิธีตรวจ: ตรวจผ่านเบราว์เซอร์ของ OpenCode Desktop (แท็บ Review) ด้วยการเลือกโหมด
กรอกค่าในฟอร์มจริง แล้วกดปุ่ม "คำนวณ DC Bias" ไม่ได้ใช้ `curl` หรืออ่านโค้ดแทน

## 7. หลักฐาน Lab 03

| ไฟล์ | เนื้อหา |
|---|---|
| `docs/screenshots/05-fixed-mode.png` | A2 · Fixed Bias, RB = 1000 kΩ → IC 1.130 mA · VCE 9.514 V · โหมดระบุบนหัวตารางผล |
| `docs/screenshots/06-invalid-rb.png` | A5 · Fixed Bias, RB = 0 → error ภาษาไทย ระบุโหมด และไม่มีตารางผลค้างจากรอบก่อน |
