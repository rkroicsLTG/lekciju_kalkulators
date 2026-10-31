"""Lekciju grupas beigu laika kalkulators (Streamlit)."""

from datetime import datetime, time, timedelta

import pandas as pd
import streamlit as st

LEKCIJAS_GARUMS = 90  # min, tīrais lekcijas laiks
OFICIALA_PAUZE = 5  # min, pauze katras lekcijas vidū

# Standarta lekciju laiki pēc saraksta (sākums, beigas)
LAIKI = [
    (time(8, 15), time(9, 50)),
    (time(10, 15), time(11, 50)),
    (time(12, 30), time(14, 5)),
    (time(14, 30), time(16, 5)),
    (time(16, 30), time(18, 5)),
    (time(18, 15), time(19, 50)),
    (time(20, 15), time(21, 50)),
]


def hm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def starpbrizu_vietas(brizi: int, vietas: int) -> set[int]:
    """Izvieto starpbrīžus pēc iespējas vienmērīgi starp lekciju pusēm."""
    if brizi <= 0:
        return set()
    return {round((i + 0.5) * vietas / brizi - 0.5) for i in range(brizi)}


st.set_page_config(page_title="Lekciju kalkulators", page_icon="⏰", layout="centered")
st.title("⏰ Lekciju beigu laika kalkulators")
st.caption(
    f"Viena lekcija = {LEKCIJAS_GARUMS} min + {OFICIALA_PAUZE} min pauze vidū. "
    "Norādi, cik starpbrīžus patiešām taisāt, un uzzini, kad beigsies lekciju grupa."
)

# --- Ievade ---
sakuma_veids = st.radio(
    "Lekcijas sākums",
    ["Pēc saraksta", "Sarunāts cits laiks"],
    horizontal=True,
)
if sakuma_veids == "Pēc saraksta":
    sakums_t = st.selectbox(
        "Sākuma laiks",
        [s for s, _ in LAIKI],
        index=1,
        format_func=lambda t: t.strftime("%H:%M"),
    )
else:
    sakums_t = st.time_input("Sākuma laiks", value=time(10, 0), step=timedelta(minutes=5))

col1, col2 = st.columns(2)
with col1:
    lekcijas = st.selectbox("Lekcijas pēc kārtas", [1, 2, 3, 4], index=1)
max_brizi = 2 * lekcijas - 1  # pauze katras lekcijas vidū + starp lekcijām
with col2:
    brizi = st.selectbox(
        "Starpbrīžu skaits",
        list(range(max_brizi + 1)),
        index=lekcijas,
        help=f"Kopā iespējamas {max_brizi} vietas: {lekcijas} lekciju vidū un "
        f"{lekcijas - 1} starp lekcijām.",
    )
briza_garums = st.select_slider(
    "Viena starpbrīža garums (min)",
    options=[5, 10, 15, 20, 25, 30, 40],
    value=OFICIALA_PAUZE,
    disabled=brizi == 0,
)

# --- Aprēķins ---
sakums = datetime.combine(datetime.today(), sakums_t)
beigas = sakums + timedelta(minutes=lekcijas * LEKCIJAS_GARUMS + brizi * briza_garums)

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Sākums", hm(sakums))
c2.metric("Beigas", hm(beigas))
c3.metric("Kopā", f"{(beigas - sakums).seconds // 3600} h {(beigas - sakums).seconds % 3600 // 60} min")

# Salīdzinājums ar oficiālo sarakstu, ja sākums sakrīt ar saraksta laiku
sakumi = [s for s, _ in LAIKI]
if sakums_t in sakumi:
    idx = sakumi.index(sakums_t)
    if idx + lekcijas <= len(LAIKI):
        oficialas = datetime.combine(datetime.today(), LAIKI[idx + lekcijas - 1][1])
        starpiba = int((oficialas - beigas).total_seconds() // 60)
        if starpiba > 0:
            st.success(f"Pēc saraksta būtu jābeidz {hm(oficialas)} — beigsiet **{starpiba} min ātrāk**.")
        elif starpiba < 0:
            st.warning(f"Pēc saraksta būtu jābeidz {hm(oficialas)} — beigsiet **{-starpiba} min vēlāk**.")
        else:
            st.info(f"Beigas sakrīt ar sarakstu ({hm(oficialas)}).")

# --- Laika grafiks ---
vietas = starpbrizu_vietas(brizi, max_brizi)
rindas = []
laiks = sakums
puse = LEKCIJAS_GARUMS // 2
for i in range(2 * lekcijas):
    nr = i // 2 + 1
    beigas_daļai = laiks + timedelta(minutes=puse)
    rindas.append({"No": hm(laiks), "Līdz": hm(beigas_daļai), "Kas": f"{nr}. lekcija, {i % 2 + 1}. daļa"})
    laiks = beigas_daļai
    if i in vietas:
        beigas_daļai = laiks + timedelta(minutes=briza_garums)
        rindas.append({"No": hm(laiks), "Līdz": hm(beigas_daļai), "Kas": "☕ Starpbrīdis"})
        laiks = beigas_daļai

with st.expander("Laika grafiks", expanded=True):
    st.dataframe(pd.DataFrame(rindas), hide_index=True, width="stretch")
