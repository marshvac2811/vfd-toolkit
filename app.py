"""
app.py — VFD Toolkit: Energy Savings, Sizing/Derating, Harmonics Screening
Run locally: python app.py  →  http://127.0.0.1:5007
"""
from flask import Flask, render_template, request
import calculator as calc

app = Flask(__name__)

ENERGY_DEFAULTS = {
    "motor_kw": "", "speed_reduction_pct": "", "static_head_fraction": "0",
    "annual_hours": "", "tariff_per_kwh": "",
}
SIZING_DEFAULTS = {
    "motor_kw": "", "ambient_temp_c": "40", "altitude_m": "1000",
}
HARMONICS_DEFAULTS = {
    "total_vfd_kva": "", "transformer_kva": "",
}


@app.route("/", methods=["GET", "POST"])
def energy_savings():
    result, error = None, None
    form_values = dict(ENERGY_DEFAULTS)
    if request.method == "POST":
        for key in form_values:
            form_values[key] = request.form.get(key, "")
        try:
            result = calc.calculate_energy_savings(
                motor_kw=float(form_values["motor_kw"]),
                speed_reduction_pct=float(form_values["speed_reduction_pct"]),
                static_head_fraction=float(form_values["static_head_fraction"] or 0),
                annual_hours=float(form_values["annual_hours"]),
                tariff_per_kwh=float(form_values["tariff_per_kwh"]),
            )
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "Please enter valid numeric values in all fields."
    return render_template("energy.html", form_values=form_values, result=result, error=error, active="energy")


@app.route("/sizing", methods=["GET", "POST"])
def sizing():
    result, error = None, None
    form_values = dict(SIZING_DEFAULTS)
    if request.method == "POST":
        for key in form_values:
            form_values[key] = request.form.get(key, "")
        try:
            result = calc.calculate_sizing(
                motor_kw=float(form_values["motor_kw"]),
                ambient_temp_c=float(form_values["ambient_temp_c"]),
                altitude_m=float(form_values["altitude_m"]),
            )
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "Please enter valid numeric values in all fields."
    return render_template("sizing.html", form_values=form_values, result=result, error=error, active="sizing")


@app.route("/harmonics", methods=["GET", "POST"])
def harmonics():
    result, error = None, None
    form_values = dict(HARMONICS_DEFAULTS)
    if request.method == "POST":
        for key in form_values:
            form_values[key] = request.form.get(key, "")
        try:
            result = calc.screen_harmonics_risk(
                total_vfd_kva=float(form_values["total_vfd_kva"]),
                transformer_kva=float(form_values["transformer_kva"]),
            )
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "Please enter valid numeric values in all fields."
    return render_template("harmonics.html", form_values=form_values, result=result, error=error, active="harmonics")


if __name__ == "__main__":
    app.run(debug=True, port=5007)
