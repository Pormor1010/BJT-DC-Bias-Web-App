# AGENTS.md — กติกาสำหรับ AI coding agent

โปรเจกต์: BJT DC Bias Web App (ENG29 2121 Lab 02)

## สถาปัตยกรรม

| ไฟล์ | หน้าที่ | ห้ามทำ |
|---|---|---|
| `dc_bias.py` | สมการ DC bias, validation, region detection | ห้าม import Flask, ห้ามรู้จัก HTTP หรือหน่วย kΩ |
| `app.py` | HTTP route, แปลงหน่วย kΩ→Ω, จัดการ error | ห้ามมีสมการไฟฟ้า |
| `templates/index.html` | แสดงผลเท่านั้น | ห้ามคำนวณหรือมีสมการ |
| `tests/` | unittest | ห้ามแก้Production code เพื่อให้ test ผ่านโดยไม่จำเป็น |

## กติกา

1. หน่วยภายใน `dc_bias.py` เป็น SI ทั้งหมด (V, Ω, A) — การแปลง kΩ ทำที่ `app.py`
2. ห้าม hardcode ผลลัพธ์ใน template หรือ JavaScript
3. เพิ่ม/แก้สมการ → ต้องมี test ใน `tests/test_dc_bias.py` ก่อน
4. เพิ่ม/แก้ route → ต้องมี test ใน `tests/test_web.py`
5. รัน `python -m unittest discover -s tests -v` ให้เขียวก่อนทุกครั้งที่ commit
6. ห้าม commit `.venv/`, `.env`, `__pycache__/`, API key
7. ข้อความ error/warning ที่ผู้ใช้เห็นต้องเป็นภาษาไทยและบอกสาเหตุ
8. อยู่นอกขอบเขต: AC, Transient, Bode, Signal Generator, SPICE, Bias ชนิดอื่น

## คำสั่งที่ใช้บ่อย

```powershell
python -m unittest discover -s tests -v
python -m flask --app app run --debug
```
