"""Flask front end for the BJT DC bias calculator.

The HTTP layer only parses the form, converts kilo-ohms to ohms, and formats
the numbers for display. All engineering lives in :mod:`dc_bias`.
"""

from flask import Flask, render_template, request

from dc_bias import solve

app = Flask(__name__)

DEFAULTS = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
}


def _parse(form):
    """Read the form and return the seven parameters in SI units."""

    def value(name):
        raw = (form.get(name) or "").strip()
        if not raw:
            raise ValueError(f"กรุณากรอกค่า {name.upper()}")
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"ค่า {name.upper()} ต้องเป็นตัวเลข") from None

    return {
        "vcc": value("vcc"),
        "r1": value("r1") * 1000,  # kΩ -> Ω
        "r2": value("r2") * 1000,
        "rc": value("rc") * 1000,
        "re": value("re") * 1000,
        "beta": value("beta"),
        "vbe": value("vbe"),
    }


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


@app.get("/")
def index():
    return render_template(
        "index.html", form=DEFAULTS, result=None, error=None, warnings=[]
    )


@app.post("/calculate")
def calculate():
    try:
        params = _parse(request.form)
        result = solve(**params)
    except (TypeError, ValueError) as exc:
        return render_template(
            "index.html",
            form=request.form,
            result=None,
            error=f"ข้อผิดพลาด: {exc}",
            warnings=[],
        )

    return render_template(
        "index.html",
        form=request.form,
        result=_display(result),
        error=None,
        warnings=result["warnings"],
    )
