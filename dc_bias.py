"""DC bias calculations for a BJT common-emitter voltage-divider bias circuit.

All values use SI base units: volts, ohms and amperes. This module knows
nothing about HTTP, HTML or kilo-ohms; callers convert units before calling
``solve``.
"""

VCE_SAT = 0.2  # Collector-emitter voltage at the edge of saturation [V]


class BiasError(ValueError):
    """Raised when an input parameter is missing, non-numeric or out of range."""


def _to_float(name, value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise BiasError(f"ค่าของ {name} ต้องเป็นตัวเลข") from None
    if number != number or number in (float("inf"), float("-inf")):
        raise BiasError(f"ค่าของ {name} ต้องเป็นจำนวนจริงที่จำกัด")
    return number


def _validate(vcc, r1, r2, rc, re, beta, vbe):
    """Return the seven inputs as floats, raising ``BiasError`` when invalid."""
    vcc = _to_float("VCC", vcc)
    r1 = _to_float("R1", r1)
    r2 = _to_float("R2", r2)
    rc = _to_float("RC", rc)
    re = _to_float("RE", re)
    beta = _to_float("Beta", beta)
    vbe = _to_float("VBE", vbe)

    if vcc <= 0:
        raise BiasError("VCC ต้องมากกว่า 0 V")
    for label, value in (("R1", r1), ("R2", r2), ("RC", rc), ("RE", re)):
        if value <= 0:
            raise BiasError(f"ค่าความต้านทาน {label} ต้องมากกว่า 0 Ω")
    if beta <= 0:
        raise BiasError("Beta ต้องมากกว่า 0")
    if vbe <= 0 or vbe >= vcc:
        raise BiasError("VBE ต้องมากกว่า 0 และน้อยกว่า VCC")

    return vcc, r1, r2, rc, re, beta, vbe


def solve(vcc, r1, r2, rc, re, beta, vbe):
    """Return the DC operating point of a voltage-divider biased BJT.

    Inputs are in volts (``vcc``, ``vbe``), ohms (``r1``, ``r2``, ``rc``,
    ``re``) and dimensionless ``beta``.

    The returned mapping holds ``vth``, ``rth``, ``ib``, ``ic``, ``ie``,
    ``ve``, ``vb``, ``vc``, ``vce`` (SI units) plus ``region`` and
    ``warnings``.
    """
    vcc, r1, r2, rc, re, beta, vbe = _validate(vcc, r1, r2, rc, re, beta, vbe)

    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    if vth <= vbe:
        return {
            "vth": vth,
            "rth": rth,
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "ve": 0.0,
            "vb": vth,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "warnings": [
                "วงจรอยู่ในช่วง Cutoff (VTH ≤ VBE): ทรานซิสเตอร์ไม่นำกระแส "
                "จึงไม่มี DC Bias ให้ใช้งาน"
            ],
        }

    ib = (vth - vbe) / (rth + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    region = "active"
    warnings = []
    if vce < VCE_SAT:
        region = "saturation"
        warnings.append(
            "VCE ต่ำกว่า VCE(sat) = 0.2 V — วงจรอยู่ใน Saturation: "
            "ค่าที่แสดงมาจากสมการ Forward-Active จึงไม่น่าเชื่อถือ "
            "ควรยืนยันด้วยการวัดวงจรจริง หรือปรับค่า RC/RE ใหม่"
        )

    return {
        "vth": vth,
        "rth": rth,
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "ve": ve,
        "vb": vb,
        "vc": vc,
        "vce": vce,
        "region": region,
        "warnings": warnings,
    }
