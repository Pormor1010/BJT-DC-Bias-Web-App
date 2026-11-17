"""Flask front end for the BJT DC bias calculator.

The HTTP layer only parses the form, converts kilo-ohms to ohms, picks the
function that matches the selected circuit and formats the numbers for
display. All engineering lives in :mod:`dc_bias`.
"""

from flask import Flask, render_template, request

from dc_bias import BiasError, emitter_bias, fixed_bias, solve

app = Flask(__name__)

KILO = 1000.0  # kΩ -> Ω

DEFAULTS = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "rb": "1000",
    "beta": "100",
    "vbe": "0.70",
}

# Field metadata: label, unit shown on the form and the Thai hint under it.
FIELDS = {
    "vcc": {"label": "VCC", "unit": "V", "hint": "แรงดันไฟเลี้ยง"},
    "rc": {"label": "RC", "unit": "kΩ", "hint": "ตัวต้านทานขา Collector"},
    "beta": {"label": "β (hFE)", "unit": "", "hint": "อัตราขยายกระแสตรง"},
    "vbe": {"label": "VBE", "unit": "V", "hint": "แรงดัน Base–Emitter"},
    "r1": {"label": "R1", "unit": "kΩ", "hint": "ตัวต้านทานขา Base ด้านบน"},
    "r2": {"label": "R2", "unit": "kΩ", "hint": "ตัวต้านทานขา Base ด้านล่าง"},
    "re": {"label": "RE", "unit": "kΩ", "hint": "ตัวต้านทานขา Emitter"},
    "rb": {"label": "RB", "unit": "kΩ", "hint": "ตัวต้านทานขา Base"},
}

COMMON_FIELDS = ("vcc", "rc", "beta", "vbe")

MODES = {
    "divider": {
        "label": "Voltage Divider Bias",
        "hint": "R1 จาก VCC ไป Base · R2 จาก Base ลงกราวด์ · "
        "RE จาก Emitter ลงกราวด์",
        "resistors": ("r1", "r2", "re"),
    },
    "fixed": {
        "label": "Fixed Bias",
        "hint": "RB จาก VCC ไป Base · Emitter ต่อลงกราวด์โดยตรง",
        "resistors": ("rb",),
    },
    "emitter": {
        "label": "Emitter Bias",
        "hint": "RB จาก VCC ไป Base · RE จาก Emitter ลงกราวด์",
        "resistors": ("rb", "re"),
    },
}


def _unknown_mode(mode):
    return (
        f"ข้อผิดพลาด: ไม่รู้จักโหมดวงจร “{mode}” — "
        "ต้องเป็น divider, fixed หรือ emitter"
    )


def _parse(form, mode):
    """Read only the fields the selected mode needs and return SI units."""

    def number(name):
        raw = (form.get(name) or "").strip()
        if not raw:
            raise ValueError(f"กรุณากรอกค่า {name.upper()}")
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"ค่า {name.upper()} ต้องเป็นตัวเลข") from None

    values = {
        "vcc": number("vcc"),
        "rc": number("rc") * KILO,
        "beta": number("beta"),
        "vbe": number("vbe"),
    }
    for name in MODES[mode]["resistors"]:
        values[name] = number(name) * KILO

    return values


def _solve(mode, values):
    """Pick the model that matches the selected circuit."""
    if mode == "divider":
        return solve(**values)
    if mode == "fixed":
        return fixed_bias(**values)
    if mode == "emitter":
        return emitter_bias(**values)
    raise BiasError(f"ไม่รู้จักโหมดวงจร {mode!r}")


def _display(result):
    """Format SI results for the page: volts, milliamps, microamps."""
    regions = {
        "active": "Active (ทำงานปกติ)",
        "saturation": "Saturation (อิ่มตัว)",
        "cutoff": "Cutoff (ตัดการนำ)",
    }
    return {
        "vb": f"{result['vb']:.3f}",
        "ve": f"{result['ve']:.3f}",
        "vc": f"{result['vc']:.3f}",
        "vce": f"{result['vce']:.3f}",
        "ic": f"{result['ic'] * 1000:.3f}",
        "ie": f"{result['ie'] * 1000:.3f}",
        "ib": f"{result['ib'] * 1e6:.3f}",
        "region": regions.get(result["region"], result["region"]),
    }


def _render(mode, form, result=None, error=None, warnings=None):
    ui_mode = mode if mode in MODES else "divider"
    return render_template(
        "index.html",
        mode=ui_mode,
        modes=MODES,
        fields=FIELDS,
        common_fields=COMMON_FIELDS,
        form=form,
        result=result,
        error=error,
        warnings=warnings or [],
    )


@app.get("/")
def index():
    mode = request.args.get("mode", "divider")
    if mode not in MODES:
        return _render(mode, DEFAULTS, error=_unknown_mode(mode)), 400
    return _render(mode, DEFAULTS)


@app.post("/calculate")
def calculate():
    mode = (request.form.get("mode") or "").strip()
    if mode not in MODES:
        return _render(mode, request.form, error=_unknown_mode(mode)), 400

    try:
        params = _parse(request.form, mode)
        result = _solve(mode, params)
    except (TypeError, ValueError) as exc:
        return _render(mode, request.form, error=f"ข้อผิดพลาด: {exc}")

    return _render(
        mode,
        request.form,
        result=_display(result),
        warnings=result["warnings"],
    )
