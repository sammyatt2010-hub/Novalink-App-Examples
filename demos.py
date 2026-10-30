"""
Novalink Bespoke Apps - demo engines.

Everything here runs on FICTITIOUS data generated on the fly.
No external APIs, no customer data, nothing stored.
Each demo returns a plain dict the UI (app.py) knows how to draw,
plus a PDF report builder shared by all demos.
"""
from __future__ import annotations

import hashlib
import html as html_lib
from datetime import date, datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Industry profiles - tune the "feel" of each generated dataset
# ---------------------------------------------------------------------------
INDUSTRIES = {
    "Dental & healthcare": dict(
        vol=70, ext=["Reception 1", "Reception 2", "Treatment Co-ord", "Practice Manager", "Accounts"],
        enquiry_value=180, deal_avg=4200,
        deal_types=["Implant plan", "Aligner course", "Practice membership", "Cosmetic plan"],
        words=["Dental", "Smile Studio", "Clinic", "Health Centre"]),
    "Estate & lettings": dict(
        vol=90, ext=["Sales", "Lettings", "Valuations", "Property Mgmt", "Reception"],
        enquiry_value=450, deal_avg=3800,
        deal_types=["Sole agency instruction", "Lettings management", "Block management", "Valuation"],
        words=["Estates", "Property", "Homes", "Lettings"]),
    "Legal services": dict(
        vol=60, ext=["Reception", "Conveyancing", "Family", "Litigation", "Accounts"],
        enquiry_value=650, deal_avg=5200,
        deal_types=["Conveyancing", "Commercial lease", "Employment matter", "Probate"],
        words=["Legal", "Solicitors", "Law", "Chambers"]),
    "Manufacturing": dict(
        vol=75, ext=["Sales desk", "Customer service", "Purchasing", "Despatch", "Accounts"],
        enquiry_value=1200, deal_avg=18500,
        deal_types=["Supply contract", "Framework order", "Custom fabrication", "Spares agreement"],
        words=["Engineering", "Fabrications", "Manufacturing", "Components"]),
    "Hospitality": dict(
        vol=110, ext=["Front desk", "Reservations", "Events", "Kitchen", "Manager"],
        enquiry_value=140, deal_avg=2600,
        deal_types=["Corporate event", "Wedding package", "Group booking", "Conference day"],
        words=["Hotel", "Inn", "Restaurant", "Venues"]),
    "IT & professional services": dict(
        vol=55, ext=["Helpdesk", "Sales", "Projects", "Accounts", "Director"],
        enquiry_value=800, deal_avg=9800,
        deal_types=["Managed service", "Project", "Support contract", "Licensing"],
        words=["IT", "Consulting", "Solutions", "Digital"]),
}
SIZES = {"Small": 0.5, "Medium": 1.0, "Large": 2.0}

_PREFIX = ["Oak", "Harbour", "Kestrel", "Brindley", "Summit", "Riverside", "Northgate", "Elm",
           "Beacon", "Foxley", "Ashdown", "Larch", "Granite", "Meadow", "Copper", "Weston",
           "Halden", "Marlow", "Sterling", "Thornbury", "Bramley", "Wren", "Calder", "Fenwick",
           "Ivybridge", "Lockwood", "Moorside", "Pennine", "Quayside", "Redfern"]
_SUFFIX = ["Ltd", "Group", "& Co", "Partners", "Services", "Holdings", "Logistics", "Retail",
           "Interiors", "Motors", "Foods", "Construction", "Leisure", "Print", "Training"]


def seed_for(*parts) -> int:
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


def fake_companies(rng, n):
    names = set()
    while len(names) < n:
        names.add(f"{rng.choice(_PREFIX)} {rng.choice(_SUFFIX)}")
    return sorted(names)


def pl(n, word, plural=None):
    return f"{n} {word if n == 1 else (plural or word + 's')}"


def gbp(x, dp=0):
    sign = "-" if x < 0 else ""
    return f"{sign}£{abs(x):,.{dp}f}"


# ===========================================================================
# 1. CALL INSIGHTS (CDR analysis)
# ===========================================================================
_HOURS = list(range(8, 18))
_HOUR_W = np.array([3, 9, 10, 8, 6, 5, 7, 8, 6, 3], dtype=float)
_HOUR_W /= _HOUR_W.sum()


def generate_cdr(industry, size, seed):
    rng = np.random.default_rng(seed)
    prof = INDUSTRIES[industry]
    vol = prof["vol"] * SIZES[size]
    exts = prof["ext"]
    ext_w = np.array([0.34, 0.24, 0.18, 0.14, 0.10])[: len(exts)]
    ext_w /= ext_w.sum()
    pool = [f"01632 96{n:04d}" for n in rng.choice(10000, int(vol * 7) + 50, replace=False)]

    end = date.today() - timedelta(days=1)
    days = [end - timedelta(days=i) for i in range(29, -1, -1)]
    rows = []
    for d in days:
        wd = d.weekday()
        lam = vol * (1.0 if wd < 5 else 0.10) * (1.15 if wd == 0 else 1.0)
        for _ in range(rng.poisson(lam)):
            hr = int(rng.choice(_HOURS, p=_HOUR_W))
            ts = datetime(d.year, d.month, d.day, hr, int(rng.integers(0, 60)), int(rng.integers(0, 60)))
            ext = str(rng.choice(exts, p=ext_w))
            num = str(rng.choice(pool))
            if rng.random() < 0.72:
                p_miss = 0.07 + (0.16 if hr in (12, 13) else 0) + (0.07 if hr in (9, 10) else 0) \
                         + (0.05 if wd == 0 else 0) + (0.12 if wd >= 5 else 0)
                missed = rng.random() < p_miss
                rows.append(dict(ts=ts, direction="Inbound", ext=ext, number=num,
                                 status="Missed" if missed else "Answered",
                                 ring=int(rng.gamma(4, 6)) + (12 if missed else 0),
                                 duration=0 if missed else int(rng.gamma(2.2, 95)) + 15))
                if missed:
                    r = rng.random()
                    if r < 0.30:  # caller tries again shortly and gets through
                        rows.append(dict(ts=ts + timedelta(minutes=int(rng.integers(3, 50))), direction="Inbound",
                                         ext=ext, number=num, status="Answered", ring=int(rng.gamma(3, 5)),
                                         duration=int(rng.gamma(2, 90)) + 15))
                    elif r < 0.68:  # business calls back
                        rows.append(dict(ts=ts + timedelta(minutes=int(rng.exponential(170)) + 4), direction="Outbound",
                                         ext=ext, number=num, status="Answered", ring=0,
                                         duration=int(rng.gamma(2, 80)) + 15))
            else:
                ok = rng.random() < 0.82
                rows.append(dict(ts=ts, direction="Outbound", ext=ext, number=num,
                                 status="Answered" if ok else "No answer", ring=0,
                                 duration=int(rng.gamma(2, 85)) + 10 if ok else 0))
    df = pd.DataFrame(rows).sort_values("ts").reset_index(drop=True)
    return df


def analyse_cdr(df, industry, company):
    prof = INDUSTRIES[industry]
    inbound = df[df.direction == "Inbound"]
    missed = inbound[inbound.status == "Missed"]
    answered_in = inbound[inbound.status == "Answered"]

    # recovery check: did the caller get through, or did we call back, within 24h?
    by_num_in = answered_in.groupby("number")["ts"].apply(list).to_dict()
    out = df[df.direction == "Outbound"]
    by_num_out = out.groupby("number")["ts"].apply(list).to_dict()
    recovered, cb_delays = [], []
    for _, m in missed.iterrows():
        lim = m.ts + timedelta(hours=24)
        later_in = [t for t in by_num_in.get(m.number, []) if m.ts < t <= lim]
        later_out = [t for t in by_num_out.get(m.number, []) if m.ts < t <= lim]
        recovered.append(bool(later_in or later_out))
        if later_out and not later_in:
            cb_delays.append((min(later_out) - m.ts).total_seconds() / 60)
    missed = missed.assign(recovered=recovered, day=missed.ts.dt.date)
    true_missed = missed[~missed.recovered].drop_duplicates(["number", "day"])

    total = len(df)
    ans_rate = len(answered_in) / max(len(inbound), 1) * 100
    value_risk = len(true_missed) * 0.25 * prof["enquiry_value"]
    median_cb = float(np.median(cb_delays)) if cb_delays else 0

    # heatmap of missed % (weekdays x hours)
    wk = inbound[inbound.ts.dt.weekday < 5].copy()
    wk["wd"] = wk.ts.dt.weekday
    wk["hr"] = wk.ts.dt.hour
    wk["m"] = (wk.status == "Missed").astype(int)
    heat = wk.pivot_table(index="wd", columns="hr", values="m", aggfunc="mean").reindex(
        index=range(5), columns=_HOURS).fillna(0) * 100
    heat.index = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    hourly = inbound.assign(hr=inbound.ts.dt.hour).groupby(["hr", "status"]).size().unstack(fill_value=0) \
        .reindex(_HOURS, fill_value=0)
    daily = inbound.assign(d=inbound.ts.dt.date).groupby(["d", "status"]).size().unstack(fill_value=0)

    ext_tbl = []
    for e in prof["ext"]:
        di = inbound[inbound.ext == e]
        do = out[out.ext == e]
        a = (di.status == "Answered").sum()
        ext_tbl.append({"Extension": e, "Inbound": len(di), "Answered": int(a),
                        "Missed": int((di.status == "Missed").sum()),
                        "Answer rate": f"{a / max(len(di), 1) * 100:.0f}%",
                        "Outbound": len(do),
                        "Avg talk (m:s)": _mmss(di[di.status == "Answered"].duration.mean())})
    ext_df = pd.DataFrame(ext_tbl)

    busiest_hr = int(hourly.sum(axis=1).idxmax())
    hr_rate = (hourly.get("Missed", 0) / hourly.sum(axis=1).replace(0, np.nan) * 100).fillna(0)
    worst_hr = int(hr_rate.idxmax())
    lunch_rate = hr_rate.loc[[12, 13]].mean()
    other_rate = hr_rate.drop([12, 13]).mean()
    worst_ext = ext_df.assign(r=ext_df.Missed / ext_df.Inbound.replace(0, 1)).sort_values("r").iloc[-1]
    weekend_in = inbound[inbound.ts.dt.weekday >= 5]

    obs = [
        ("bad", f"{pl(len(true_missed), 'caller')} never got through and were not called back within 24 hours. "
                f"At a 25% conversion rate and ~{gbp(prof['enquiry_value'])} per enquiry, that is roughly "
                f"{gbp(value_risk)} of potential business at risk this month."),
        ("warn", f"The {worst_hr}:00 hour has the highest missed-call rate ({hr_rate[worst_hr]:.0f}%). "
                 f"Lunchtime (12:00-14:00) averages {lunch_rate:.0f}% missed vs {other_rate:.0f}% the rest of the day, "
                 f"which points to a cover gap rather than a volume problem."),
        ("accent", f"Busiest hour is {busiest_hr}:00. Missed calls that were returned took a median of "
                   f"{median_cb / 60:.1f} hours to call back."),
        ("warn", f"'{worst_ext.Extension}' misses the highest share of its calls ({worst_ext['Answer rate']} answered). "
                 f"Worth checking hunt-group order or adding an overflow."),
        ("good", f"Overall {ans_rate:.0f}% of inbound calls were answered first time."),
    ]
    if len(weekend_in):
        obs.append(("accent", f"{len(weekend_in)} calls arrived at weekends with no planned cover. "
                              f"A call-answering or voicemail-to-email rule would capture these."))
    recs = [
        "Stagger lunch breaks or add an overflow to a second group between 12:00 and 14:00.",
        "Send a daily 'unreturned missed calls' list to the team at 4pm so nothing rolls over.",
        "Set a callback target of under one hour and track it weekly with this report.",
        "Consider an out-of-hours / overflow answering service for peaks and weekends.",
    ]
    kpis = [
        ("Total calls", f"{total:,}", "Last 30 days"),
        ("Answer rate", f"{ans_rate:.0f}%", "Inbound, first time"),
        ("True missed calls", f"{len(true_missed)}", "Not recovered in 24h"),
        ("Value at risk", gbp(value_risk), "Estimated, this month"),
    ]
    raw = df.rename(columns={"ts": "Date/Time", "direction": "Direction", "ext": "Extension", "number": "Number",
                             "status": "Status", "ring": "Ring (s)", "duration": "Duration (s)"})
    tm_tbl = true_missed[["ts", "number", "ext"]].rename(
        columns={"ts": "Missed at", "number": "Caller", "ext": "Rang to"}).sort_values("Missed at", ascending=False)
    tm_tbl["Missed at"] = tm_tbl["Missed at"].dt.strftime("%a %d %b %H:%M")
    return dict(kpis=kpis, heat=heat, hourly=hourly, daily=daily, ext_df=ext_df, obs=obs, recs=recs,
                raw=raw, true_missed=tm_tbl, period=f"{df.ts.min():%d %b} - {df.ts.max():%d %b %Y}")


def _mmss(sec):
    if pd.isna(sec):
        return "-"
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


# ===========================================================================
# 2. CALL QUALITY ANALYSER (simulated AI assessment)
# ===========================================================================
# Each line: speaker, good wording, weak wording, category (agent lines) or
# sentiment after a good / weak agent turn (customer lines).
SCRIPTS = {
    "Billing complaint": [
        ("A", "Good morning, {co}, you're speaking with {agent}. How can I help today?", "{co}, hello.", "Opening"),
        ("C", "Hi. I've had my invoice and it's nearly double what I normally pay. I'm not happy.", None, (-0.6, -0.65)),
        ("A", "I'm sorry to hear that, I can see why that's worrying. Let's get to the bottom of it together. Can I take the account name first?",
              "Right. Account name?", "Empathy"),
        ("C", "It's {cust}.", None, (-0.35, -0.55)),
        ("A", "Thank you. For security, could you confirm the first line of the address?", "OK, I've got you up.", "Compliance"),
        ("C", "14 Station Road.", "Uh, OK.", (-0.3, -0.5)),
        ("A", "I can see the increase. It's calls to an international mobile on the 12th. Does that ring a bell?",
              "There's loads of call charges on here, that's why.", "Clarity"),
        ("C", "Oh, that'll be our engineer calling a supplier abroad. I didn't realise it cost that much.",
              "Well nobody told me calls would cost that. This is ridiculous.", (0.0, -0.75)),
        ("A", "That's understandable. I can add an international bundle that would have covered most of that, and I'll ask accounts about a goodwill credit.",
              "I can't do anything about it, it's what you used.", "Resolution"),
        ("C", "That would be great, thank you.", "Then I want to speak to a manager.", (0.5, -0.85)),
        ("A", "You're welcome. You'll get an email confirmation within the hour. Is there anything else I can help with?",
              "I'll pass it on.", "Close"),
        ("C", "No, that's everything. Thanks for sorting it.", "Fine.", (0.75, -0.6)),
    ],
    "New sales enquiry": [
        ("A", "Thanks for calling {co}, this is {agent}. How can I help?", "Hello, {co}.", "Opening"),
        ("C", "Hi, I'm looking for a quote. We're opening a second site next month.", None, (0.2, 0.15)),
        ("A", "Congratulations, that's exciting. So I give you the right options, can I ask a few quick questions about the new site?",
              "OK. What do you need?", "Listening"),
        ("C", "Sure, go ahead.", "Er, just a price really.", (0.3, -0.05)),
        ("A", "How many staff will be there, and what matters most to you: cost, speed of setup, or flexibility?",
              "We've got a package at the standard price, I'll send it over.", "Listening"),
        ("C", "About twelve people. Speed matters most, we open on the 1st.",
              "I'd rather know it fits what we need first.", (0.4, -0.3)),
        ("A", "Twelve people opening on the 1st is very doable. I'd suggest our quick-start option. I'll explain exactly what's included.",
              "It should be fine, most people go for it.", "Clarity"),
        ("C", "That sounds ideal.", "Hmm, I'll probably get a few quotes.", (0.6, -0.25)),
        ("A", "Great. I'll email the proposal today and book a 15-minute call on Thursday to go through it. Does 10am work?",
              "I'll send something over at some point.", "Close"),
        ("C", "Thursday at 10 is perfect, thanks {agent}.", "OK, thanks.", (0.8, -0.1)),
    ],
    "Appointment change": [
        ("A", "Good afternoon, {co}, {agent} speaking. How can I help?", "Yeah, {co}.", "Opening"),
        ("C", "Hi, I need to move my appointment on Friday. Something's come up at work.", None, (-0.1, -0.15)),
        ("A", "No problem at all, these things happen. Can I confirm your name and date of birth so I can find the booking?",
              "What's the name?", "Compliance"),
        ("C", "{cust_person}, 3rd of March.", "{cust_person}.", (0.0, -0.2)),
        ("A", "Thanks. I've got you on Friday at 2pm. I have Tuesday at 9 or Wednesday at 4. Would either suit?",
              "Next one I've got is in three weeks.", "Resolution"),
        ("C", "Wednesday at 4 is perfect.", "Three weeks? That's no good at all.", (0.5, -0.7)),
        ("A", "Lovely, that's booked. You'll get a text confirmation in the next few minutes.",
              "OK, done.", "Clarity"),
        ("C", "Brilliant, thank you.", "Right.", (0.65, -0.45)),
        ("A", "My pleasure. Is there anything else I can do for you today?", "Bye then.", "Close"),
        ("C", "No that's all, have a good day.", None, (0.8, -0.35)),
    ],
}
CATEGORIES = ["Opening", "Empathy", "Listening", "Clarity", "Resolution", "Compliance", "Close"]
COACHING = {
    "Opening": "Open with the business name, your name and an offer to help. It sets a professional tone in the first five seconds.",
    "Empathy": "Acknowledge the customer's feeling before moving to process. One sentence of empathy lowers tension measurably.",
    "Listening": "Ask open questions before offering a solution so the recommendation fits the need.",
    "Clarity": "Explain the 'why' in plain language and check understanding instead of using vague statements.",
    "Resolution": "Offer at least one concrete option, even when the answer is 'no'. Customers react to choices, not refusals.",
    "Compliance": "Always complete identity / data checks before discussing an account. This is a regulatory risk if skipped.",
    "Close": "Summarise next steps with a time commitment and ask if there's anything else. It is the last impression.",
}
WEAK_IDX = {  # which agent turns are delivered weakly at each performance level
    "Strong": set(),
    "Average": {"Compliance", "Close", "Listening"},
    "Needs coaching": set(CATEGORIES),
}


def analyse_call(scenario, level, company, agent, seed):
    rng = np.random.default_rng(seed)
    script = SCRIPTS[scenario]
    weak = WEAK_IDX[level]
    cust = rng.choice(_PREFIX) + " " + rng.choice(_SUFFIX)
    person = rng.choice(["Alex Morgan", "Jamie Patel", "Chris Hughes", "Sam Rowe", "Taylor Reid"])
    fill = dict(co=company, agent=agent, cust=cust, cust_person=person)

    lines, t, last_weak = [], 0.0, False
    cat_hits = {}
    wpm = {"Strong": 146, "Average": 161, "Needs coaching": 184}[level] + rng.normal(0, 4)
    for spk, good, bad, meta in script:
        if spk == "A":
            is_weak = meta in weak
            text = (bad if is_weak else good).format(**fill)
            cat_hits.setdefault(meta, []).append(not is_weak)
            last_weak = is_weak
            sent = None
        else:
            text = ((bad if (last_weak and bad) else good)).format(**fill)
            target = meta[1] if last_weak else meta[0]
            prev = next((l["sentiment"] for l in reversed(lines) if l["sentiment"] is not None), target)
            sent = target if prev is target else 0.45 * prev + 0.55 * target  # customers' mood carries over
            sent = float(np.clip(sent + rng.normal(0, 0.04), -1, 1))
        words = len(text.split())
        dur = words / (wpm if spk == "A" else 150) * 60 + rng.uniform(0.6, 2.2)
        lines.append(dict(t=t, speaker="Agent" if spk == "A" else "Customer", text=text, sentiment=sent,
                          good=None if spk == "C" else not is_weak, cat=meta if spk == "A" else None))
        t += dur

    scores = {}
    for c in CATEGORIES:
        hits = cat_hits.get(c)
        if hits is None:  # not exercised in this call - infer from overall level
            base = {"Strong": 88, "Average": 76, "Needs coaching": 58}[level]
        else:
            base = 91 if all(hits) else (52 if not any(hits) else 70)
        scores[c] = int(np.clip(base + rng.normal(0, 3.5), 25, 99))
    overall = int(round(np.mean(list(scores.values()))))
    agent_words = sum(len(l["text"].split()) for l in lines if l["speaker"] == "Agent")
    all_words = sum(len(l["text"].split()) for l in lines)
    talk = agent_words / all_words * 100
    end_sent = [l["sentiment"] for l in lines if l["sentiment"] is not None][-1]
    start_sent = [l["sentiment"] for l in lines if l["sentiment"] is not None][0]

    strengths = [c for c in CATEGORIES if scores[c] >= 82]
    coaching = []
    for l in lines:
        if l["speaker"] == "Agent" and l["good"] is False:
            good_line = next(g for s, g, b, m in script if s == "A" and m == l["cat"]
                             and b.format(**fill) == l["text"]).format(**fill)
            coaching.append(dict(cat=l["cat"], said=l["text"], tip=COACHING[l["cat"]], try_saying=good_line,
                                 at=l["t"]))
    verdict = ("Excellent call. Use as a training example." if overall >= 85 else
               "Solid call with clear coaching opportunities." if overall >= 68 else
               "Call needs review. Customer left less satisfied than they arrived.")
    pace_note = ("Ideal" if wpm < 155 else "Slightly fast" if wpm < 170 else "Too fast")
    kpis = [
        ("Overall score", f"{overall}/100", verdict.split(".")[0]),
        ("Customer sentiment", f"{start_sent:+.1f} → {end_sent:+.1f}", "Start → end of call"),
        ("Speaking pace", f"{wpm:.0f} wpm", pace_note),
        ("Agent talk time", f"{talk:.0f}%", "Ideal 40-55%"),
    ]
    obs = []
    delta = end_sent - start_sent
    any_weak = any(l["good"] is False for l in lines)
    if end_sent < -0.2:
        obs.append(("bad", f"Customer ended the call unhappy ({start_sent:+.1f} → {end_sent:+.1f}). "
                           f"Risk of complaint or churn. Flag for a manager callback."))
    elif delta >= 0.8:
        obs.append(("good", f"Customer sentiment improved strongly ({start_sent:+.1f} → {end_sent:+.1f}): the call turned a "
                            f"negative or neutral start into a positive outcome."))
    elif delta >= 0.25 and not any_weak:
        obs.append(("good", f"Customer sentiment improved ({start_sent:+.1f} → {end_sent:+.1f}) and the call finished on a positive note."))
    elif delta >= 0.25:
        obs.append(("accent", f"Customer sentiment improved ({start_sent:+.1f} → {end_sent:+.1f}), but weaker moments "
                              f"held it back from a genuinely positive finish."))
    elif delta <= -0.25:
        obs.append(("bad", f"Customer sentiment fell during the call ({start_sent:+.1f} → {end_sent:+.1f}). "
                           f"Risk of complaint or churn. Flag for a manager callback."))
    else:
        obs.append(("warn", f"Customer sentiment stayed broadly flat ({start_sent:+.1f} → {end_sent:+.1f}). The call was handled but the customer wasn't 'won'."))
    if scores["Compliance"] < 60:
        obs.append(("bad", "Identity / data protection check was skipped. Compliance risk."))
    obs.append(("accent" if wpm < 170 else "warn", f"Pace of {wpm:.0f} words per minute ({pace_note.lower()})."))
    if talk > 60:
        obs.append(("warn", f"Agent spoke {talk:.0f}% of the time. More questions, less telling."))
    if strengths:
        obs.append(("good", "Strengths: " + ", ".join(strengths) + "."))
    duration = lines[-1]["t"] + 3
    return dict(kpis=kpis, lines=lines, scores=scores, overall=overall, talk=talk, wpm=wpm, obs=obs,
                coaching=coaching, verdict=verdict, duration=duration, customer=cust)


# ===========================================================================
# 3. BILL RUN & PROFIT / LOSS
# ===========================================================================
CATALOGUE = [
    ("Hosted seat licence", "Voice", 6.50, 12.00, (2, 40)),
    ("SIP channel", "Voice", 3.20, 7.50, (2, 20)),
    ("Call recording add-on", "Voice", 1.50, 4.00, (2, 30)),
    ("FTTP 900 broadband", "Connectivity", 38.00, 65.00, (1, 1)),
    ("FTTC 80 broadband", "Connectivity", 19.50, 35.00, (1, 2)),
    ("Leased line 100Mb", "Connectivity", 210.00, 345.00, (1, 1)),
    ("Business mobile 30GB", "Mobile", 6.80, 15.00, (1, 25)),
    ("Handset lease", "Hardware", 4.10, 9.50, (1, 30)),
    ("Call answering bundle", "Services", 42.00, 79.00, (1, 1)),
]


def generate_bills(size, seed):
    rng = np.random.default_rng(seed)
    n_cust = int(40 * SIZES[size])
    customers = fake_companies(rng, n_cust)
    sup, bil = [], []
    for c in customers:
        prods = rng.choice(len(CATALOGUE), size=int(rng.integers(2, 6)), replace=False)
        for i in prods:
            name, cat, cost, price, (lo, hi) = CATALOGUE[i]
            qty = int(rng.integers(lo, hi + 1))
            r = rng.random()
            s_qty, b_qty, b_price = qty, qty, price * rng.choice([1, 1, 1, 0.95, 1.05])
            if r < 0.05:
                b_qty = 0                       # unbilled
            elif r < 0.10 and qty > 2:
                b_qty = qty - int(rng.integers(1, max(2, qty // 3) + 1))  # under-billed qty
            elif r < 0.13:
                b_price = cost * rng.uniform(0.7, 0.95)  # priced below cost
            elif r < 0.16:
                s_qty = 0                       # billed but not supplied
            if s_qty:
                sup.append(dict(Customer=c, Product=name, Category=cat, Qty=s_qty, UnitCost=cost,
                                Cost=round(s_qty * cost, 2)))
            if b_qty:
                bil.append(dict(Customer=c, Product=name, Category=cat, Qty=b_qty, UnitPrice=round(b_price, 2),
                                Billed=round(b_qty * b_price, 2)))
        u_cost = round(float(rng.gamma(2, 25)), 2)
        mark = rng.choice([1.45, 1.5, 1.55, 1.0]) if rng.random() > 0.06 else 0.9
        sup.append(dict(Customer=c, Product="Call usage", Category="Usage", Qty=1, UnitCost=u_cost, Cost=u_cost))
        bil.append(dict(Customer=c, Product="Call usage", Category="Usage", Qty=1, UnitPrice=round(u_cost * mark, 2),
                        Billed=round(u_cost * mark, 2)))
    return pd.DataFrame(sup), pd.DataFrame(bil)


def analyse_bills(sup, bil):
    list_price = {n: p for n, _, _, p, _ in CATALOGUE}
    m = sup.merge(bil, on=["Customer", "Product", "Category"], how="outer", suffixes=("_s", "_b"))
    m[["Qty_s", "Qty_b", "Cost", "Billed"]] = m[["Qty_s", "Qty_b", "Cost", "Billed"]].fillna(0)
    ex = []
    for _, r in m.iterrows():
        lp = list_price.get(r.Product, r.UnitPrice if pd.notna(r.UnitPrice) else 0)
        if r.Qty_s > 0 and r.Qty_b == 0:
            ex.append(dict(Customer=r.Customer, Product=r.Product, Issue="Not billed", Supplier_qty=int(r.Qty_s),
                           Billed_qty=0, Impact=round(r.Qty_s * lp, 2), kind="unbilled"))
        elif r.Qty_b > 0 and r.Qty_s == 0:
            ex.append(dict(Customer=r.Customer, Product=r.Product, Issue="Billed, not supplied", Supplier_qty=0,
                           Billed_qty=int(r.Qty_b), Impact=-round(r.Billed, 2), kind="refund"))
        elif r.Qty_b < r.Qty_s:
            ex.append(dict(Customer=r.Customer, Product=r.Product, Issue="Under-billed quantity",
                           Supplier_qty=int(r.Qty_s), Billed_qty=int(r.Qty_b),
                           Impact=round((r.Qty_s - r.Qty_b) * lp, 2), kind="qty"))
        elif r.Billed < r.Cost - 0.01:
            fix = (r.Qty_s * lp - r.Billed) if r.Product != "Call usage" else (r.Cost * 1.5 - r.Billed)
            ex.append(dict(Customer=r.Customer, Product=r.Product, Issue="Sold below cost",
                           Supplier_qty=int(r.Qty_s), Billed_qty=int(r.Qty_b), Impact=round(fix, 2), kind="price"))
    ex = pd.DataFrame(ex)
    revenue, cost = bil.Billed.sum(), sup.Cost.sum()
    profit = revenue - cost
    gain = {k: ex.loc[ex.kind == k, "Impact"].sum() if len(ex) else 0 for k in ["unbilled", "qty", "price", "refund"]}
    recover = gain["unbilled"] + gain["qty"] + gain["price"]

    cat = pd.DataFrame({"Revenue": bil.groupby("Category").Billed.sum(), "Cost": sup.groupby("Category").Cost.sum()}) \
        .fillna(0)
    cat["Profit"] = cat.Revenue - cat.Cost
    cat["Margin"] = cat.Profit / cat.Revenue.replace(0, np.nan) * 100
    cat = cat.sort_values("Revenue", ascending=False)
    cust = pd.DataFrame({"Revenue": bil.groupby("Customer").Billed.sum(), "Cost": sup.groupby("Customer").Cost.sum()}) \
        .fillna(0)
    cust["Profit"] = cust.Revenue - cust.Cost
    cust["Margin %"] = (cust.Profit / cust.Revenue.replace(0, np.nan) * 100).round(1)
    loss_makers = cust[cust.Profit < 0]

    kpis = [
        ("Monthly revenue", gbp(revenue), f"{bil.Customer.nunique()} customers"),
        ("Gross profit", gbp(profit), f"{profit / revenue * 100:.1f}% margin"),
        ("Recoverable / month", gbp(recover), f"{gbp(recover * 12)} a year"),
        ("Exceptions found", f"{len(ex)}", "Lines needing action"),
    ]
    n = lambda k: int((ex.kind == k).sum()) if len(ex) else 0
    obs = [
        ("bad", f"{pl(n('unbilled'), 'service')} paid to suppliers but never billed to the customer: "
                f"{gbp(gain['unbilled'])} a month of lost revenue."),
        ("warn", f"{pl(n('qty'), 'line')} billed for fewer units than the supplier charges for (e.g. extra seats or handsets "
                 f"added but never invoiced): {gbp(gain['qty'])} a month."),
        ("warn", f"{pl(n('price'), 'line')} sold below cost. Repricing to list would add {gbp(gain['price'])} a month."),
        ("accent", f"{pl(n('refund'), 'line')} billed with no matching supplier service ({gbp(-gain['refund'])}). "
                   f"Check whether these were ceased: they are a refund / dispute risk."),
        ("good", f"Best performing category: {cat.Margin.idxmax()} at {cat.Margin.max():.0f}% margin."),
    ]
    if len(loss_makers):
        obs.insert(3, ("bad", f"{pl(len(loss_makers), 'customer account')} loss-making this month: "
                              + ", ".join(loss_makers.index[:3]) + ("..." if len(loss_makers) > 3 else "") + "."))
    recs = [
        "Raise back-billing for unbilled and under-billed lines (check contract terms first).",
        "Reprice below-cost lines at next renewal, or add a price-review clause.",
        "Reconcile 'billed, not supplied' lines against ceased orders before issuing credits.",
        "Run this reconciliation every bill run so leaks are caught in month one, not month twelve.",
    ]
    ex_show = ex.drop(columns="kind").rename(columns={"Supplier_qty": "Supplier qty", "Billed_qty": "Billed qty",
                                                      "Impact": "Monthly impact £"}) \
        .sort_values("Monthly impact £", key=abs, ascending=False) if len(ex) else ex
    return dict(kpis=kpis, cat=cat, cust=cust, ex=ex_show, gain=gain, revenue=revenue, cost=cost, profit=profit,
                recover=recover, obs=obs, recs=recs, sup=sup, bil=bil)


# ===========================================================================
# 4. SALES PIPELINE
# ===========================================================================
STAGES = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
STAGE_P = {"Lead": 0.10, "Qualified": 0.25, "Proposal": 0.50, "Negotiation": 0.75, "Won": 1.0, "Lost": 0.0}
OWNERS = ["A. Carter", "J. Patel", "R. Hughes", "L. Morgan"]


def generate_pipeline(industry, size, seed):
    rng = np.random.default_rng(seed)
    prof = INDUSTRIES[industry]
    n = int(60 * SIZES[size])
    accounts = fake_companies(rng, n)
    today = date.today()
    skill = {o: s for o, s in zip(OWNERS, rng.permutation([0.55, 0.45, 0.38, 0.30]))}
    rows = []
    for i in range(n):
        owner = str(rng.choice(OWNERS))
        created = today - timedelta(days=int(rng.integers(5, 200)))
        value = round(float(rng.lognormal(np.log(prof["deal_avg"]), 0.55)), -1)
        age = (today - created).days
        if age > 60 and rng.random() < 0.55:
            stage = "Won" if rng.random() < skill[owner] else "Lost"
            closed = created + timedelta(days=int(rng.integers(14, min(age, 120) + 1)))
            exp_close, last = closed, (today - closed).days
        else:
            stage = str(rng.choice(STAGES[:4], p=[0.30, 0.28, 0.24, 0.18]))
            closed = None
            exp_close = today + timedelta(days=int(rng.integers(-10, 170)))
            last = int(rng.choice([rng.integers(0, 14), rng.integers(14, 60)], p=[0.72, 0.28]))
        rows.append(dict(Account=accounts[i], Deal=str(rng.choice(prof["deal_types"])), Owner=owner, Stage=stage,
                         Value=value, Created=created, Closed=closed, ExpectedClose=exp_close, DaysSinceActivity=last))
    return pd.DataFrame(rows)


def analyse_pipeline(df):
    today = date.today()
    df = df.copy()
    df["Prob"] = df.Stage.map(STAGE_P)
    df["Weighted"] = df.Value * df.Prob
    open_ = df[df.Stage.isin(STAGES[:4])]
    won, lost = df[df.Stage == "Won"], df[df.Stage == "Lost"]
    win_rate = len(won) / max(len(won) + len(lost), 1) * 100
    cycle = float(np.mean([(r.Closed - r.Created).days for r in won.itertuples()])) if len(won) else 0
    stalled = open_[open_.DaysSinceActivity > 21].sort_values("Value", ascending=False)
    overdue = open_[open_.ExpectedClose < today]

    funnel = open_.groupby("Stage").agg(Deals=("Value", "size"), Value=("Value", "sum")).reindex(STAGES[:4]).fillna(0)
    months = [(today.replace(day=1) + pd.DateOffset(months=i)).date() for i in range(6)]
    o2 = open_.assign(M=open_.ExpectedClose.apply(lambda d: max(d, today).replace(day=1)))
    fc = o2.groupby(["M", "Stage"]).Weighted.sum().unstack(fill_value=0).reindex(months, fill_value=0)
    fc.index = [m.strftime("%b %y") for m in months]
    owners = pd.DataFrame({
        "Open pipeline": open_.groupby("Owner").Value.sum(),
        "Weighted": open_.groupby("Owner").Weighted.sum(),
        "Won value": won.groupby("Owner").Value.sum(),
        "Won": won.groupby("Owner").size(),
        "Lost": lost.groupby("Owner").size(),
    }).reindex(OWNERS).fillna(0)
    owners["Win rate"] = (owners.Won / (owners.Won + owners.Lost).replace(0, np.nan) * 100).fillna(0).round(0)
    best = owners["Win rate"].idxmax()

    def nba(r):
        if r.Stage in ("Proposal", "Negotiation"):
            return "Call to agree decision date"
        if r.Stage == "Qualified":
            return "Book discovery meeting"
        return "Re-qualify or close as lost"

    stalled_tbl = stalled.assign(**{"Next best action": stalled.apply(nba, axis=1)})[
        ["Account", "Deal", "Owner", "Stage", "Value", "DaysSinceActivity", "Next best action"]] \
        .rename(columns={"DaysSinceActivity": "Days idle", "Value": "Value £"})
    kpis = [
        ("Open pipeline", gbp(open_.Value.sum()), f"{len(open_)} live deals"),
        ("Weighted forecast", gbp(open_.Weighted.sum()), "Value × stage probability"),
        ("Win rate", f"{win_rate:.0f}%", f"{len(won)} won / {len(lost)} lost"),
        ("Avg sales cycle", f"{cycle:.0f} days", f"Avg won deal {gbp(won.Value.mean() if len(won) else 0)}"),
    ]
    obs = [
        ("bad", f"{pl(len(stalled), 'open deal')} ({gbp(stalled.Value.sum())}) have had no activity for 3+ weeks. "
                f"These are the fastest wins to chase."),
        ("warn", f"{pl(len(overdue), 'deal')} past their expected close date ({gbp(overdue.Value.sum())}). "
                 f"Forecast accuracy improves if these dates are updated."),
        ("accent", f"Next month's weighted forecast is {gbp(fc.iloc[1].sum())}; this month {gbp(fc.iloc[0].sum())}."),
        ("good", f"{best} has the strongest win rate ({owners.loc[best, 'Win rate']:.0f}%). Their approach is worth sharing with the team."),
    ]
    big = funnel.Value.idxmax()
    obs.append(("accent", f"Most pipeline value currently sits at '{big}' ({gbp(funnel.loc[big, 'Value'])})."))
    recs = [
        "Hold a weekly 15-minute review of stalled and overdue deals only.",
        "Require a next action + date on every open deal.",
        "Pair lower win-rate owners with the top performer on Proposal-stage calls.",
        "Move deals older than 90 days at 'Lead' to Lost to keep the forecast honest.",
    ]
    return dict(kpis=kpis, funnel=funnel, fc=fc, owners=owners, stalled=stalled_tbl, obs=obs, recs=recs, raw=df)


# ===========================================================================
# PDF REPORT (shared by all demos)
# ===========================================================================
def _esc(s):
    return html_lib.escape(str(s), quote=False)


def chart_png(kind, data):
    """Small, print-friendly matplotlib chart for the PDF."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    A, C, G, R, W = "#5B63E6", "#1FB5D6", "#22A07A", "#E05555", "#E8A20C"
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=160)
    if kind == "calls":
        h = data["hourly"]
        x = [f"{i}:00" for i in h.index]
        ax.bar(x, h.get("Answered", 0), color=A, label="Answered")
        ax.bar(x, h.get("Missed", 0), bottom=h.get("Answered", 0), color=R, label="Missed")
        ax.set_title("Inbound calls by hour", loc="left", fontsize=10, fontweight="bold")
    elif kind == "quality":
        s = data["scores"]
        ks = list(s.keys())[::-1]
        vals = [s[k] for k in ks]
        ax.barh(ks, vals, color=[G if v >= 82 else W if v >= 65 else R for v in vals])
        ax.set_xlim(0, 100)
        ax.set_title("Score by category", loc="left", fontsize=10, fontweight="bold")
    elif kind == "bills":
        c = data["cat"]
        x = np.arange(len(c))
        ax.bar(x - 0.2, c.Revenue, 0.4, color=A, label="Revenue")
        ax.bar(x + 0.2, c.Cost, 0.4, color=C, label="Cost")
        ax.set_xticks(x, c.index)
        ax.set_title("Revenue vs cost by category (£/month)", loc="left", fontsize=10, fontweight="bold")
    elif kind == "pipeline":
        fc = data["fc"]
        bottom = np.zeros(len(fc))
        for st_, col in zip(["Lead", "Qualified", "Proposal", "Negotiation"], ["#C7CAF7", "#9BA1F2", A, C]):
            if st_ in fc:
                ax.bar(fc.index, fc[st_], bottom=bottom, color=col, label=st_)
                bottom += fc[st_].values
        ax.set_title("Weighted forecast by month (£)", loc="left", fontsize=10, fontweight="bold")
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=7.5)
    ax.grid(axis="y" if kind != "quality" else "x", alpha=0.25)
    if kind != "quality":
        ax.legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def build_pdf(title, company, period, kpis, chart, observations, recs, table_df, table_title):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    NAVY, ACC, CYAN = colors.HexColor("#0A0E1A"), colors.HexColor("#7C83FF"), colors.HexColor("#38D6F5")
    MUTED, LINE = colors.HexColor("#6B7385"), colors.HexColor("#E2E6EF")
    TONE = {"good": "#22A07A", "warn": "#C98A06", "bad": "#D64545", "accent": "#5B63E6"}
    W, H = A4

    def page(c, doc):
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, H - 30 * mm, W, 30 * mm, stroke=0, fill=1)
        c.setFillColor(ACC)
        c.rect(0, H - 31.2 * mm, W / 2, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(CYAN)
        c.rect(W / 2, H - 31.2 * mm, W / 2, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(16 * mm, H - 11 * mm, "NOVALINK  ·  BESPOKE APPS")
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(16 * mm, H - 19.5 * mm, title)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#B8C0D4"))
        c.drawString(16 * mm, H - 25 * mm, f"{company}  ·  {period}")
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(colors.HexColor("#FBBF24"))
        c.drawRightString(W - 16 * mm, H - 11 * mm, "SAMPLE REPORT - FICTITIOUS DATA")
        c.setFont("Helvetica", 7.5)
        c.setFillColor(MUTED)
        c.drawString(16 * mm, 10 * mm, "Generated by a Novalink demo app  ·  info@novalinkhardware.co.uk")
        c.drawRightString(W - 16 * mm, 10 * mm, f"Page {doc.page}")
        c.restoreState()

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=38 * mm,
                            bottomMargin=18 * mm, title=title, author="Novalink")
    h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceBefore=8, spaceAfter=5)
    body = ParagraphStyle("b", fontName="Helvetica", fontSize=8.8, leading=12.5, textColor=colors.HexColor("#1F2433"))
    small = ParagraphStyle("s", fontName="Helvetica", fontSize=7.2, textColor=MUTED, leading=9)
    kv = ParagraphStyle("kv", fontName="Helvetica-Bold", fontSize=15, textColor=NAVY, leading=18)
    kl = ParagraphStyle("kl", fontName="Helvetica-Bold", fontSize=6.8, textColor=MUTED, leading=9)
    cell = ParagraphStyle("c", fontName="Helvetica", fontSize=7.4, leading=9.5)
    cellh = ParagraphStyle("ch", fontName="Helvetica-Bold", fontSize=7.4, leading=9.5, textColor=colors.white)

    story = []
    tiles = [[Paragraph(_esc(l.upper()), kl), Paragraph(_esc(v), kv), Paragraph(_esc(s), small)] for l, v, s in kpis]
    kt = Table([tiles], colWidths=[(W - 32 * mm) / len(kpis)] * len(kpis))
    kt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
                            ("LINEABOVE", (0, 0), (-1, 0), 2, ACC), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F8FC"))]))
    story += [kt, Spacer(1, 8)]
    story.append(Image(chart, width=W - 32 * mm, height=(W - 32 * mm) * 2.6 / 7.2))
    story.append(Paragraph("Key findings", h2))
    for tone, text in observations:
        story.append(Paragraph(f'<font name="ZapfDingbats" size="7" color="{TONE.get(tone, "#5B63E6")}">l</font>&nbsp;&nbsp;{_esc(text)}', body))
        story.append(Spacer(1, 3))
    if recs:
        story.append(Paragraph("Recommendations", h2))
        for i, r in enumerate(recs, 1):
            story.append(Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{_esc(r)}", body))
            story.append(Spacer(1, 2))
    if table_df is not None and len(table_df):
        story.append(Paragraph(_esc(table_title), h2))
        t = table_df.head(14)
        data = [[Paragraph(_esc(c), cellh) for c in t.columns]]
        for row in t.itertuples(index=False):
            data.append([Paragraph(_esc(f"{v:,.2f}" if isinstance(v, float) else v), cell) for v in row])
        tb = Table(data, repeatRows=1, colWidths=[(W - 32 * mm) / len(t.columns)] * len(t.columns))
        tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY),
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6FB")]),
                                ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(tb)
    doc.build(story, onFirstPage=page, onLaterPages=page)
    return buf.getvalue()
