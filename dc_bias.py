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


def _common_inputs(vcc, rc, beta, vbe):
    """Validate the four inputs shared by every bias topology."""
    vcc = _to_float("VCC", vcc)
    rc = _to_float("RC", rc)
    beta = _to_float("Beta", beta)
    vbe = _to_float("VBE", vbe)

    if vcc <= 0:
        raise BiasError("VCC ต้องมากกว่า 0 V")
    if rc <= 0:
        raise BiasError("ค่าความต้านทาน RC ต้องมากกว่า 0 Ω")
    if beta <= 0:
        raise BiasError("Beta ต้องมากกว่า 0")
    if vbe <= 0 or vbe >= vcc:
        raise BiasError("VBE ต้องมากกว่า 0 และน้อยกว่า VCC")

    return vcc, rc, beta, vbe


def _resistor(name, value):
    """Return ``value`` in ohms, rejecting non-positive or non-finite inputs."""
    value = _to_float(name, value)
    if value <= 0:
        raise BiasError(f"ค่าความต้านทาน {name} ต้องมากกว่า 0 Ω")
    return value


def _operating_point(ib, beta, rc, re, vcc, vbe):
    """Build the result mapping from IB using the shared DC equations.

    ``re`` is 0 for Fixed Bias, which makes VE 0 V. The returned mapping uses
    the same key names and SI units as :func:`solve`.
    """
    ic = beta * ib
    ie = (beta + 1) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    region = "active"
    warnings = []
    if ib <= 0:
        region = "cutoff"
        warnings.append(
            "IB ที่คำนวณได้ ≤ 0 A — วงจรอาจอยู่ในช่วง Cutoff: "
            "แบบจำลอง Forward-Active ใช้ตัดสินผลไม่ได้"
        )
    elif vce < VCE_SAT:
        region = "saturation"
        warnings.append(
            "VCE ต่ำกว่า VCE(sat) = 0.2 V — วงจรอยู่ใน Saturation: "
            "ค่าที่แสดงมาจากสมการ Forward-Active จึงไม่น่าเชื่อถือ "
            "ควรยืนยันด้วยการวัดวงจรจริง หรือปรับค่า RC/RE ใหม่"
        )

    return {
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


def fixed_bias(vcc, rb, rc, beta, vbe):
    """Return the DC operating point of a fixed-bias BJT.

    ``rb`` connects VCC to the base and the emitter is grounded, so ``VE`` is
    0 V. Inputs are in volts (``vcc``, ``vbe``) and ohms (``rb``, ``rc``).

    The returned mapping holds ``ib``, ``ic``, ``ie``, ``ve``, ``vb``, ``vc``,
    ``vce`` (SI units) plus ``region`` and ``warnings``.
    """
    vcc, rc, beta, vbe = _common_inputs(vcc, rc, beta, vbe)
    rb = _resistor("RB", rb)

    ib = (vcc - vbe) / rb
    return _operating_point(ib, beta, rc, 0.0, vcc, vbe)


def emitter_bias(vcc, rb, rc, re, beta, vbe):
    """Return the DC operating point of a single-supply emitter-bias BJT.

    ``rb`` connects VCC to the base and ``re`` connects the emitter to ground,
    which makes the base current depend on ``(beta + 1) * re``. Inputs are in
    volts (``vcc``, ``vbe``) and ohms (``rb``, ``rc``, ``re``).

    The returned mapping holds ``ib``, ``ic``, ``ie``, ``ve``, ``vb``, ``vc``,
    ``vce`` (SI units) plus ``region`` and ``warnings``.
    """
    vcc, rc, beta, vbe = _common_inputs(vcc, rc, beta, vbe)
    rb = _resistor("RB", rb)
    re = _resistor("RE", re)

    ib = (vcc - vbe) / (rb + (beta + 1) * re)
    return _operating_point(ib, beta, rc, re, vcc, vbe)
