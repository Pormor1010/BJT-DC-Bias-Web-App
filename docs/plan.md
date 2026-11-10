# BJT DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เว็บ Flask ที่รับค่า VCC, R1, R2, RC, RE, β, VBE ของวงจร Voltage-Divider Bias แล้วคำนวณ DC Operating Point ด้วย Python พร้อม validation, region warning และ automated tests

**Architecture:** แยก 3 ชั้น — `dc_bias.py` (สมการล้วน, SI units, ไม่รู้จัก Flask), `app.py` (HTTP route + แปลงหน่วย kΩ→Ω + จัดการ error), `templates/index.html` (แสดงผลเท่านั้น) ทุกชั้นมี test ของตัวเอง

**Tech Stack:** Python 3.14.2, Flask, Jinja2, stdlib `unittest`

**Spec:** `docs/design-note.md`

## สถานะการดำเนินการ (อัปเดต 2026-11-10)

- Task 1–7 ดำเนินการครบแล้วด้วยวิธี TDD: เขียนเทสต์ → เห็น fail → เขียนโค้ด → เขียว
- ขั้น "หยุด — ให้ผู้ใช้ commit (C1–C4)" รวมเป็นการ commit ครั้งเดียวตอนจบ
  (`75b43bd`) ตามที่ตกลงกัน จึงไม่ได้หยุด 4 ครั้งตามลำดับในแผน
- ผลทดสอบล่าสุด: `Ran 19 tests ... OK` — บันทึกไว้ที่ `docs/test-log.txt`
- ภาพหน้าจอหลักฐาน: `docs/screenshots/` (ฟอร์ม, ผลลัพธ์, input ผิด, warning)
- checkbox `- [ ]` ด้านล่างคงไว้ตามรูปแบบแผนเดิม เพื่อให้เห็นลำดับงานที่วางไว้

## Global Constraints

- รันด้วย `python -m flask --app app run --debug` → `http://127.0.0.1:5000/`
- `dc_bias.py` ต้องไม่ import flask และไม่รู้จัก HTTP/หน่วย kΩ
- หน่วยภายใน `dc_bias.py`: V, Ω, A (SI ทั้งหมด)
- ฟอร์มรับตัวต้านทานเป็น kΩ — แปลง ×1000 ใน `app.py`
- ค่าคงที่ `VCE_SAT = 0.2` (V) และคลาส `BiasError(ValueError)` อยู่ใน `dc_bias.py`
- Input ผิด → HTTP **200** + ข้อความ error ใต้ฟอร์ม (ห้าม 500/traceback)
- แสดงผล: VB, VE, VC, VCE [V 3dp] · IC, IE [mA 3dp] · IB [µA 3dp] · Region
- ห้ามแสดง VTH/RTH บนหน้าจอ (ใช้ภายใน/test เท่านั้น)
- ภาษา UI: ป้ายไทย + หน่วยอังกฤษ
- Tests: `python -m unittest discover -s tests -v`
- **Commit ผ่าน GitHub Desktop เท่านั้น** — agent ห้ามรัน `git commit`

## Review Focus

- **ช่องว่าง/ไม่ได้กรอก** → ต้องได้ error ภาษาไทย ไม่ใช่ 500 (Task 6)
- **ค่าติดลบหรือศูนย์** (VCC, R, β) → `BiasError` ไม่ใช่ ZeroDivisionError (Task 2)
- **ค่าที่มีตัวอักษรปน** เช่น `abc` → แปลง float ไม่ได้ ต้องได้ error 200 ไม่ใช่ 500 (Task 6)
- **R2 = 0 หรือ R1+R2 = 0** → validation ดักก่อนหาร (Task 2)
- **VBE ≥ VCC** → `BiasError` ไม่ใช่ค่าติดลบเงียบ ๆ (Task 2)

---

### Task 1: โครงโปรเจกต์ + สมการหลัก (Forward-Active)

**Files:**
- Create: `requirements.txt`, `dc_bias.py`, `tests/test_dc_bias.py`

**Interfaces:**
- Produces: `solve(vcc, r1, r2, rc, re, beta, vbe) -> dict` คีย์ `vth, rth, ib, ic, ie, ve, vb, vc, vce, region, warnings` (SI units, float)

- [ ] **Step 1: สร้าง venv และติดตั้ง Flask**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install flask
pip freeze > requirements.txt
```
Expected: `flask` ปรากฏใน `requirements.txt`

- [ ] **Step 2: เขียน test ที่ยังไม่ผ่าน**

`tests/test_dc_bias.py`

```python
import unittest
from dc_bias import solve

class TestReferenceOperatingPoint(unittest.TestCase):
    def test_reference_operating_point(self):
        r = solve(vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70)
        self.assertAlmostEqual(r["vth"], 2.163934, places=4)
        self.assertAlmostEqual(r["rth"], 18032.787, places=2)
        self.assertAlmostEqual(r["ib"], 1.229868e-5, places=7)
        self.assertAlmostEqual(r["ic"], 1.229868e-3, places=6)
        self.assertAlmostEqual(r["ie"], 1.242167e-3, places=6)
        self.assertAlmostEqual(r["ve"], 1.242167, places=4)
        self.assertAlmostEqual(r["vb"], 1.942167, places=4)
        self.assertAlmostEqual(r["vc"], 9.294290, places=4)
        self.assertAlmostEqual(r["vce"], 8.052123, places=4)
```

- [ ] **Step 3: รัน test ให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dc_bias'`

- [ ] **Step 4: เขียน `dc_bias.py`**

ฟังก์ชัน `solve` คำนวณตามลำดับ `vth → rth → ib → ic → ie → ve → vb → vc → vce` ด้วยสมการใน `docs/design-note.md` ข้อ 8 และคืน dict ตาม Interfaces (ใน Task นี้ให้ `region="active"`, `warnings=[]` ไปก่อน)

- [ ] **Step 5: รัน test ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (1 test)

---

### Task 2: Validation (`BiasError`)

**Files:**
- Modify: `dc_bias.py`
- Test: `tests/test_dc_bias.py`

**Interfaces:**
- Produces: `class BiasError(ValueError)`; `solve` raise `BiasError` เมื่อ input ไม่ผ่าน

- [ ] **Step 1: เขียน test ที่ยังไม่ผ่าน**

```python
from dc_bias import BiasError
import math

class TestValidation(unittest.TestCase):
    def _base(self, **kw):
        p = dict(vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70)
        p.update(kw)
        return p

    def test_zero_and_negative_resistance_rejected(self):
        for bad in (dict(r1=0), dict(r2=0), dict(rc=-1), dict(re=0)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))

    def test_invalid_vcc_and_beta_rejected(self):
        for bad in (dict(vcc=0), dict(beta=0), dict(beta=-5), dict(vcc=-12)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))

    def test_vbe_must_be_below_vcc(self):
        for bad in (dict(vbe=0), dict(vbe=12), dict(vbe=13)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))
```

- [ ] **Step 2: รันให้เห็น fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `ImportError: cannot import name 'BiasError'`

- [ ] **Step 3: เพิ่ม validation ใน `dc_bias.py`**

`BiasError(ValueError)` + ฟังก์ชันภายใน `_validate(...)` ตรวจ: ทุกค่าเป็นตัวเลขได้ (`float()`), `vcc > 0`, `r1,r2,rc,re > 0`, `beta > 0`, `0 < vbe < vcc` — ข้อความ error เป็นภาษาไทย ระบุชื่อพารามิเตอร์

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (4 tests)

---

### Task 3: ตรวจ Operating Region (cutoff / saturation)

**Files:**
- Modify: `dc_bias.py`
- Test: `tests/test_dc_bias.py`

- [ ] **Step 1: เขียน test ที่ยังไม่ผ่าน**

```python
class TestOperatingRegion(unittest.TestCase):
    def test_region_active_no_warning(self):
        r = solve(vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70)
        self.assertEqual(r["region"], "active")
        self.assertEqual(r["warnings"], [])

    def test_cutoff_when_vth_below_vbe(self):
        r = solve(vcc=12, r1=100_000, r2=1_000, rc=2_200, re=1_000, beta=100, vbe=0.70)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ic"], 0.0)
        self.assertEqual(r["ie"], 0.0)
        self.assertAlmostEqual(r["vce"], 12.0, places=6)
        self.assertTrue(r["warnings"])

    def test_saturation_warning(self):
        r = solve(vcc=12, r1=100_000, r2=22_000, rc=47_000, re=1_000, beta=100, vbe=0.70)
        self.assertEqual(r["region"], "saturation")
        self.assertLess(r["vce"], 0.2)
        self.assertTrue(any("Saturation" in w for w in r["warnings"]))
```

- [ ] **Step 2: รันให้เห็น fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — region ยังเป็น `"active"` ทุกกรณี

- [ ] **Step 3: เพิ่ม logic ใน `solve`**

หลังคำนวณ `vth`: ถ้า `vth <= vbe` → คืนค่า cutoff (`ib=ic=ie=0`, `ve=0`, `vb=vth`, `vc=vcc`, `vce=vcc`, `region="cutoff"`, warning ภาษาไทย) มิฉะนั้นคำนวณปกติแล้วถ้า `vce < VCE_SAT` → `region="saturation"` + warning ว่าเป็นค่าจากสมการ Forward-Active และไม่น่าเชื่อถือ

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (7 tests)

- [ ] **Step 5: หยุด — ให้ผู้ใช้ commit (C1)**

แจ้งผู้ใช้ commit ใน GitHub Desktop ด้วยข้อความ: `feat: add dc bias calculation module with validation and region checks`
ไฟล์: `dc_bias.py`, `tests/test_dc_bias.py`, `requirements.txt`, `.gitignore`

---

### Task 4: Flask GET / + ฟอร์ม

**Files:**
- Create: `app.py`, `templates/index.html`, `tests/test_web.py`

**Interfaces:**
- Produces: `app` (Flask instance) ที่ `test_web.py` import ได้; template รับ `form`, `result`, `error`, `warnings`

- [ ] **Step 1: เขียน test ที่ยังไม่ผ่าน**

```python
import unittest
from app import app

class TestIndex(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index_shows_form(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', body)
```

- [ ] **Step 2: รันให้เห็น fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: สร้าง `app.py` + `templates/index.html`**

`app.py`: `app = Flask(__name__)`, route `GET /` คืน `render_template("index.html", form=DEFAULTS, result=None, error=None, warnings=[])` โดย `DEFAULTS = {"vcc": "12", "r1": "100", "r2": "22", "rc": "2.2", "re": "1", "beta": "100", "vbe": "0.70"}`

`templates/index.html`: ฟอร์ม `method="post" action="/calculate"` มี input name ครบ 7 ตัว พร้อม label ไทย + หน่วย, ค่า `value="{{ form.vcc }}"` ฯลฯ, ปุ่ม submit "Calculate DC Bias", และ block แสดง `error`/`warnings`/`result` (ว่างเมื่อไม่มีค่า)

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (8 tests)

---

### Task 5: POST /calculate แสดงผล DC Bias

**Files:**
- Modify: `app.py`, `templates/index.html`
- Test: `tests/test_web.py`

- [ ] **Step 1: เขียน test ที่ยังไม่ผ่าน**

```python
class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = dict(vcc="12", r1="100", r2="22", rc="2.2", re="1", beta="100", vbe="0.70")

    def test_post_returns_computed_values(self):
        res = self.client.post("/calculate", data=self.valid)
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("8.052", body)   # VCE
        self.assertIn("1.230", body)   # IC mA
        self.assertIn("1.942", body)   # VB
```

- [ ] **Step 2: รันให้เห็น fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — 404 (ยังไม่มี route)

- [ ] **Step 3: เพิ่ม route + helper แปลงหน่วย**

`app.py`: `POST /calculate` อ่าน `request.form`, แปลง R ×1000, เรียก `solve()`, แปลงผลเป็นหน่วยแสดงผลเป็น **string จัดรูปแล้ว** ใน dict `result` (`vb`, `ve`, `vc`, `vce` = `f"{v:.3f}"`, `ic`, `ie` = `f"{a*1000:.3f}"`, `ib` = `f"{a*1e6:.3f}"`, `region`) แล้ว `render_template(..., result=result, warnings=warnings, form=request.form)`

`templates/index.html`: เพิ่มตารางผลลัพธ์แสดงทีละแถวพร้อมหน่วย

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (9 tests)

- [ ] **Step 5: หยุด — ให้ผู้ใช้ commit (C2)**

ข้อความ: `feat: add flask web app with dc bias calculator form`

---

### Task 6: จัดการ input ผิด (error path)

**Files:**
- Modify: `app.py`
- Test: `tests/test_web.py`

- [ ] **Step 1: เขียน test ที่ยังไม่ผ่าน**

```python
class TestInvalidInput(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = dict(vcc="12", r1="100", r2="22", rc="2.2", re="1", beta="100", vbe="0.70")

    def test_zero_vcc_shows_error(self):
        data = dict(self.valid, vcc="0")
        res = self.client.post("/calculate", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))

    def test_non_numeric_shows_error(self):
        data = dict(self.valid, vcc="abc")
        res = self.client.post("/calculate", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))

    def test_missing_field_shows_error(self):
        data = {k: v for k, v in self.valid.items() if k != "r1"}
        res = self.client.post("/calculate", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("ข้อผิดพลาด", res.get_data(as_text=True))
```

- [ ] **Step 2: รันให้เห็น fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — ได้ 500 หรือไม่พบคำว่า "ข้อผิดพลาด"

- [ ] **Step 3: ครอบ try/except ใน route**

ดัก `KeyError`, `ValueError` (รวม `BiasError` ซึ่งเป็น subclass) → `render_template(..., error=f"ข้อผิดพลาด: {e}", result=None, form=request.form)` ด้วย HTTP 200

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (12 tests)

- [ ] **Step 5: หยุด — ให้ผู้ใช้ commit (C3)**

ข้อความ: `test: cover invalid input handling in web routes`

---

### Task 7: CSS + เอกสาร

**Files:**
- Create: `static/style.css`, `README.md`, `AGENTS.md`, `docs/validation.md`, `docs/reflection.md`
- Modify: `templates/index.html` (ลิงก์ CSS)

- [ ] **Step 1: เพิ่ม `static/style.css` + ลิงก์ใน template**

`<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">` และจัดหน้าให้ฟอร์มกับผลลัพธ์อ่านง่ายบนจอแคบ พร้อมแถบสีสำหรับ error (แดง) และ warning (ส้ม)

- [ ] **Step 2: รันเว็บด้วยมือ**

Run: `.venv\Scripts\Activate.ps1; python -m flask --app app run --debug`
Expected: เปิด `http://127.0.0.1:5000/` เห็นฟอร์ม, กด Calculate เห็นผล VCE 8.052 V, ลอง vcc=0 เห็นแถบ error

- [ ] **Step 3: เขียน `README.md`**

หัวข้อ: Requirements, Setup (venv + pip install), Run, Tests, Project structure, Assumptions & limitations

- [ ] **Step 4: เขียน `AGENTS.md`**

กติกา: สมการอยู่ใน `dc_bias.py` เท่านั้น, ห้าม hardcode ผล, รัน tests ก่อน commit, ห้าม commit `.venv`

- [ ] **Step 5: เขียน `docs/validation.md`**

ตารางค่าอ้างอิง (design-note ข้อ 8) เทียบค่าที่เว็บแสดง + ผลรัน `python -m unittest discover -s tests -v`

- [ ] **Step 6: สร้าง `docs/reflection.md` แบบมีคำถาม**

ใส่หัวข้อให้ **นิสิตเขียนเอง**: เหตุใดเปิด `index.html` ตรง ๆ จึงไม่เท่ากับรัน Flask, ฟอร์มส่งข้อมูลไป Python อย่างไร, แก้สมการใน `dc_bias.py` แล้วต้องแก้ HTML ไหม, ทำไม region ที่แบบจำลองใช้ไม่ได้จึงต้องมี warning

- [ ] **Step 7: รัน test ครั้งสุดท้าย**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` (12 tests)

- [ ] **Step 8: หยุด — ให้ผู้ใช้ commit (C4) + Push**

ข้อความ: `docs: add readme, agents guide, validation and reflection notes`
