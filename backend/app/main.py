"""FastAPI entry point: /api/health and /api/compute (SPEC Section 4).

Errors return HTTP 400 with {"error": "message"}.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import engine, predict, transit

app = FastAPI(title="Astro-app")


class ComputeRequest(BaseModel):
    year: int = Field(ge=1800, le=2200)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    tz_offset: float = Field(default=5.5, ge=-12, le=14)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    e = exc.errors()[0]
    field = ".".join(str(p) for p in e["loc"] if p != "body")
    return JSONResponse(status_code=400,
                        content={"error": f"{field or 'body'}: {e['msg']}"})


class CanTradeRequest(BaseModel):
    birth: ComputeRequest
    year: int = Field(ge=1800, le=2200)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    tz_offset: float = Field(default=5.5, ge=-12, le=14)


# Gochara verdict from the janma rasi (Moon-sign count, whole sign):
# 5/8/12 = avoid (Astro Class 4 @ 19:03, Class 11 @ 06:00);
# 2/6/11 = favourable (HALF COURSE notes). The Moon stays ~2.5 days per
# rasi, so an avoid window has a concrete end time.
AVOID_COUNTS = {5, 8, 12}
GOOD_COUNTS = {2, 6, 11}


@app.post("/api/can-trade")
def can_trade(req: CanTradeRequest):
    try:
        b = req.birth
        # KP, like the rest of the prediction path (see RULES-SOURCES.md).
        # Only the /api/compute display endpoints stay Lahiri per SPEC §5.
        # Cast time stays 09:15 — this is a "can I trade today" gochara
        # read, so market open is the relevant moment; the sunrise cast
        # used by graph.cast_chart belongs to the panchang day, not here.
        birth_chart = engine.compute(b.year, b.month, b.day, b.hour,
                                     b.minute, b.tz_offset, b.lat, b.lon,
                                     ayanamsa_mode=engine.KP)
        today_chart = engine.compute(req.year, req.month, req.day, 9, 15,
                                     req.tz_offset, b.lat, b.lon,
                                     ayanamsa_mode=engine.KP)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    def moon(chart):
        return next(g for g in chart["grahas"] if g["name"] == "Moon")

    b_moon, t_moon = moon(birth_chart), moon(today_chart)
    count = (t_moon["sign"] - b_moon["sign"]) % 12 + 1
    # guide §2.1: count from the birth LAGNA as well as the rasi
    lagna_count = (t_moon["sign"] - birth_chart["lagna"]["sign"]) % 12 + 1
    # guide §2.2: transit Moon over the NATAL Rahu/Ketu → avoid
    natal = {g["name"]: g for g in birth_chart["grahas"]}
    over_node = [n for n in ("Rahu", "Ketu")
                 if natal[n]["sign"] == t_moon["sign"]]

    if over_node:
        verdict, note = "AVOID", (
            f"Transit Moon sits on your natal {'/'.join(over_node)} — "
            f"extreme whipsaw risk; strictly avoid trading.")
    elif count in AVOID_COUNTS or lagna_count in AVOID_COUNTS:
        which = f"{count} from your janma rasi" \
            if count in AVOID_COUNTS else f"{lagna_count} from your lagna"
        verdict, note = "AVOID", (
            f"Transit Moon is {which} — the teacher says do not trade or "
            f"take predictions on such days.")
    elif count in GOOD_COUNTS:
        verdict, note = "FAVOURABLE", (
            f"Transit Moon is {count} from your janma rasi — a good day; "
            f"still confirm the entry with prasanam.")
    else:
        verdict, note = "OK", (
            f"Transit Moon is {count} from your janma rasi — neutral; "
            f"confirm the entry with prasanam.")

    return {
        "lagna_count": lagna_count,
        "over_natal_node": over_node,
        "birth_rasi": {"en": b_moon["rasi"], "ta": b_moon["rasi_ta"]},
        "transit_rasi": {"en": t_moon["rasi"], "ta": t_moon["rasi_ta"]},
        "count": count,
        "verdict": verdict,
        "note": note,
        "rasi_until": transit.moon_rasi_exit(req.year, req.month, req.day,
                                             req.tz_offset),
        "source": "Astro Class 4 @ 19:03 + Class 11 @ 06:00 + HALF COURSE",
    }


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/compute")
def compute(req: ComputeRequest):
    try:
        result = engine.compute(req.year, req.month, req.day, req.hour,
                                req.minute, req.tz_offset, req.lat, req.lon)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    result["prediction"] = predict.run(result)
    return result


@app.post("/api/panchang-chart")
def panchang_chart(req: ComputeRequest):
    """compute() plus the KP day-chart tables (author's panchang chart)."""
    try:
        result = engine.compute(req.year, req.month, req.day, req.hour,
                                req.minute, req.tz_offset, req.lat, req.lon)
        result["kp"] = transit.day_chart(req.year, req.month, req.day,
                                         req.tz_offset)
        pp = transit.planet_position(
            req.year, req.month, req.day, req.hour, req.minute,
            req.tz_offset, req.lat, req.lon)
        # the ruling chain always comes from the sunrise cast so it agrees
        # with the prediction chain (the displayed-time chain can flip on
        # Moon-star boundary days)
        rc = transit.ruling_chain(req.year, req.month, req.day,
                                  req.tz_offset, req.lat, req.lon)
        pp["chain"] = {"x": rc["x"], "y": rc["y"]}
        pp["chain_text"] = rc["chain_text"]
        pp["cast"] = rc["cast"]
        result["kp"]["planet_position"] = pp
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    result["prediction"] = predict.run(result)
    return result
