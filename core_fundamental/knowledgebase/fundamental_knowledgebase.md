# 🧠 FUNDAMENTAL DRIVE KNOWLEDGE BASE v1.0 – TUYUL FX ULTRA WOLF

## 🎯 Deskripsi Singkat (≤350 karakter)

> FUNDAMENTAL DRIVE KNOWLEDGE BASE v1.0. Panduan logika makroekonomi reflektif
> bagi sistem TUYUL FX. Mengintegrasikan kebijakan moneter, data ekonomi,
> korelasi komoditas, dan risk sentiment untuk mendukung reasoning Layer 11.5
> dan Fusion Layer (L12). Update terakhir: Oktober 2025.

## ⚙️ Posisi & Fungsi Dalam Pipeline

```
L10   → FTA (Technical–Fundamental Alignment)
L11   → Fundamental Drive Engine
L11.2 → High Impact Monitor
L11.3 → Weekly Outlook Sync
L11.5 → Auto Fundamental Feed
↓
L12   → Fusion Reflective Integrator
```

| Layer   | Modul                         | Fungsi                                        |
| :------ | :---------------------------- | :-------------------------------------------- |
| L10     | FTA & TWMS                    | Mendeteksi keselarasan teknikal–fundamental   |
| L11     | Fundamental Drive             | Menentukan bias makro terukur                 |
| L11.3   | WeeklyOutlookSync             | Menyusun risk outlook global mingguan         |
| L11.5   | AutoFeed + Policy Tracker     | Menyediakan skor fundamental & arah kebijakan |
| L12     | Fusion Reflective Propagation | Menggabungkan bias makro dengan reasoning AI  |

---

## 1️⃣ CORE FUNDAMENTAL DRIVERS

### A. Monetary Policy Matrix

#### Major Central Banks Impact

```
Bank Sentral    | Kebijakan        | Dampak Pair         | Timeframe
----------------|------------------|---------------------|------------
Fed (USD)       | Hawkish/Dovish   | Semua USD pairs     | Immediate
ECB (EUR)       | Rate Decision    | EUR pairs           | 24-48h
BoE (GBP)       | MPC Minutes      | GBP pairs           | Immediate
BoJ (JPY)       | YCC Policy       | JPY pairs (carry)   | Session
BoC (CAD)       | Rate + Oil view  | CAD pairs           | 12-24h
RBA (AUD)       | Rate + Commodity | AUD pairs           | Session
RBNZ (NZD)      | Rate Decision    | NZD pairs           | Session
SNB (CHF)       | Intervention     | CHF pairs           | Immediate
```

#### Monetary Policy Scoring System

```python
HAWKISH_SIGNALS = {
    "rate_hike": +3,
    "hawkish_tone": +2,
    "forward_guidance_tight": +2,
    "QT_acceleration": +1,
    "inflation_concern": +1,
}

DOVISH_SIGNALS = {
    "rate_cut": -3,
    "dovish_tone": -2,
    "forward_guidance_easy": -2,
    "QE_expansion": -1,
    "growth_concern": -1,
}
```

### B. Economic Data Hierarchy

#### Tier 1 - Market Movers (ATR >150%)

- Interest Rate Decision → Volatilitas tertinggi
- Non-Farm Payrolls (NFP) → USD pairs
- GDP (Preliminary) → Trend jangka menengah
- CPI / Inflation → Policy expectation shift
- Central Bank Speech → Tone & forward guidance

#### Tier 2 - Moderate Impact (ATR 100-150%)

- Retail Sales
- Manufacturing PMI
- Employment Change
- Trade Balance

#### Tier 3 - Low Impact (ATR <100%)

- Consumer Confidence
- Building Permits
- Pending Home Sales

### C. Commodity Correlation Engine

```
Currency  | Primary Link      | Correlation | Threshold Impact
----------|-------------------|-------------|------------------
CAD       | WTI Oil           | +0.85       | $5/barrel move
AUD       | Iron Ore / Gold   | +0.78       | $50/ton move
NZD       | Dairy Prices      | +0.65       | 10% price shift
NOK       | Brent Oil         | +0.80       | $5/barrel move
```

#### Oil-CAD Trading Rules

```
IF Oil > $85/barrel → CAD Strength Mode
IF Oil < $75/barrel → CAD Weakness Mode
IF Oil volatility >5% → Wait confirmation
```

### D. Risk Sentiment Indicators

#### Risk-On Assets

- S&P 500 ↑ → AUD, NZD, CAD buy bias
- VIX < 15 → Sell JPY, CHF
- High Yield Spreads ↓ → Commodity FX strong

#### Risk-Off Assets

- VIX > 25 → Buy JPY, CHF, USD
- Gold > $2000 → Safe haven demand
- Treasury Yields ↓ → USD mixed, JPY strong

---

## 2️⃣ FUNDAMENTAL DRIVE WORKFLOW

### STEP 1: Macro Environment Scan (15 menit)

```
1. Check DXY (USD Index) trend
2. Review major equity indexes (S&P, DAX, Nikkei)
3. Monitor VIX / volatility index
4. Check commodity prices (Oil, Gold)
5. Review interest rate differentials
```

### STEP 2: Currency Strength Meter (Real-time)

```python
STRENGTH_FACTORS = {
    "monetary_policy": 0.30,
    "economic_data": 0.25,
    "risk_sentiment": 0.20,
    "commodity_link": 0.15,
    "positioning": 0.10,
}
```

### STEP 3: News Catalyst Filter

```
High Priority (Trade Immediately):
- Central Bank Rate Decision
- NFP / Employment Data
- Flash CPI
- Central Bank Emergency Statement

Medium Priority (Watch & Confirm):
- PMI Data
- Retail Sales
- GDP (final reading)

Low Priority (Background Info):
- Consumer Confidence
- Minor speeches
```

### STEP 4: Alignment Check

```
✅ STRONG ALIGNMENT (>80% confidence)
   Technical: Trend clear + structure intact
   Fundamental: Clear driver + data support
   Sentiment: Positioning favorable

⚠️ MODERATE ALIGNMENT (60-80%)
   Mixed signals → reduce size 50%

❌ WEAK ALIGNMENT (<60%)
   No trade → wait for clarity
```

---

## 3️⃣ FUNDAMENTAL-TECHNICAL SYNC MATRIX

### Scenario Matrix

```
Fundamental  | Technical    | Action              | Confidence
-------------|--------------|---------------------|------------
Bullish      | Bullish      | BUY (full size)     | 90%+
Bullish      | Neutral      | BUY pullback        | 75%
Bullish      | Bearish      | WAIT correction     | 60%
Bearish      | Bearish      | SELL (full size)    | 90%+
Bearish      | Neutral      | SELL rally          | 75%
Bearish      | Bullish      | WAIT rally exhaust  | 60%
Neutral      | Any          | No trade            | 50%
```

---

## 4️⃣ REAL-TIME NEWS INTEGRATION

### News Sources Priority

```
1. Central Bank Websites (Fed, ECB, BoE, etc.)
2. Bloomberg Terminal
3. Reuters Eikon
4. ForexFactory Calendar
5. TradingEconomics
```

### News Trading Protocol

```
T-60 min: Review consensus & forecast
T-30 min: Set alerts & prepare orders
T-5 min:  Cancel all pending orders
T-0:      News release
T+1 min:  Wait for spike completion
T+3 min:  Enter on retracement (if aligned)
T+30 min: Evaluate trade performance
```

---

## 5️⃣ PAIR-SPECIFIC FUNDAMENTAL DRIVERS

### EURUSD

```
Primary: ECB vs Fed policy differential
Secondary: EU economic data, US yields
Catalyst: Rate decisions, inflation data
Average Move: 80-120 pips on major news
```

### GBPUSD

```
Primary: BoE policy stance
Secondary: Brexit sentiment, UK employment
Catalyst: MPC minutes, wage data
Average Move: 100-150 pips on major news
```

### USDJPY

```
Primary: Fed policy + Risk sentiment
Secondary: BoJ YCC policy, US-JP yield gap
Catalyst: Fed decision, US yields shift
Average Move: 80-100 pips on major news
```

### AUDJPY (Carry Trade)

```
Primary: Risk sentiment + commodity prices
Secondary: RBA vs BoJ differential
Catalyst: China data, equity moves
Average Move: 120-180 pips on risk shifts
```

### USDCAD

```
Primary: Oil prices + BoC policy
Secondary: Fed vs BoC differential
Catalyst: Oil inventory, BoC decision
Average Move: 60-90 pips on major news
```

---

## 6️⃣ POSITION SIZING BERDASARKAN FUNDAMENTAL CONFIDENCE

```python
BASE_RISK = 0.7  # per trade

if fundamental_confidence >= 85:
    position_size = BASE_RISK * 1.2  # 0.84%
elif fundamental_confidence >= 75:
    position_size = BASE_RISK * 1.0  # 0.70%
elif fundamental_confidence >= 65:
    position_size = BASE_RISK * 0.7  # 0.49%
else:
    position_size = 0  # NO TRADE
```

---

## 7️⃣ WOLF DISCIPLINE CHECKLIST (Fundamental Edition)

```
☑️ Saya sudah cek economic calendar untuk hari ini
☑️ Saya tahu arah bias fundamental untuk pair ini
☑️ Saya tahu catalyst utama yang menggerakkan pair
☑️ Saya sudah cek sentiment risk-on / risk-off
☑️ Saya sudah konfirmasi tidak ada news high-impact 2 jam ke depan
☑️ Technical alignment mendukung fundamental bias
☑️ Saya siap exit jika fundamental berubah mendadak
☑️ Saya tidak trading berdasarkan rumor atau spekulasi
```

---

## 8️⃣ COMMON FUNDAMENTAL PITFALLS

### ❌ Kesalahan Fatal

1. Trading melawan central bank policy direction
2. Ignore risk sentiment shifts (risk-on/off)
3. Overtrading pada news low-impact
4. Tidak adjust bias saat data berubah
5. Hold posisi saat high-impact news upcoming

### ✅ Best Practices

1. Always align dengan monetary policy trend
2. Respect risk sentiment sebagai filter utama
3. Trade only Tier 1 & Tier 2 data events
4. Close positions 30 min sebelum major news
5. Review & update bias setiap pagi

---

## 9️⃣ MONTHLY FUNDAMENTAL REVIEW TEMPLATE

```markdown
### Bulan: [Month Year]

#### A. Monetary Policy Update
- Fed: [Status & Next Move]
- ECB: [Status & Next Move]
- BoE: [Status & Next Move]
- BoJ: [Status & Next Move]

#### B. Macro Trend
- Global Growth: [Accelerating / Stable / Slowing]
- Inflation Trend: [Rising / Stable / Falling]
- Risk Appetite: [Risk-On / Neutral / Risk-Off]

#### C. Currency Rankings (Strength)
1. [Strongest]
2. ...
8. [Weakest]

#### D. Top Fundamental Trades for Next Month
- Pair 1: [Direction] - [Reason]
- Pair 2: [Direction] - [Reason]
- Pair 3: [Direction] - [Reason]
```

---

## 🔟 FUNDAMENTAL DRIVE INTEGRATION COMMANDS

### Daily Morning Routine

```bash
1. python fundamental_scanner.py --mode morning
2. Review output: currency_strength_today.json
3. Update trading bias di journal
4. Set alerts untuk news hari ini
```

### Pre-Trade Check

```bash
python fundamental_scanner.py --pair EURUSD --check
# Output: Fundamental bias, confidence score, upcoming catalysts
```

### Real-time News Monitor

```bash
python news_monitor.py --pairs "EURUSD,GBPUSD,USDJPY" --alert
# Output: Real-time fundamental shifts & alerts
```

---

## 📊 Core Variables & Bias Formula

| Faktor           | Deskripsi                                                       | Rentang     | Dampak                               |
| :--------------- | :-------------------------------------------------------------- | :---------- | :----------------------------------- |
| `policy_diff`    | Perbedaan kebijakan moneter antar mata uang (hawkish vs dovish) | -1.0 → +1.0 | Penggerak arah utama                 |
| `inflation_diff` | Selisih inflasi antar ekonomi                                   | -1.0 → +1.0 | Menentukan arah kebijakan suku bunga |
| `commodity_corr` | Korelasi terhadap harga komoditas (oil, gold, copper)           | -1.0 → +1.0 | Dukungan fundamental CAD, AUD, NZD   |
| `risk_sentiment` | Mode pasar global (risk-on/off)                                 | -1.0 → +1.0 | Menekan/penguatan JPY & USD          |
| `carry_diff`     | Selisih yield antar mata uang                                   | -1.0 → +1.0 | Indikasi arus modal internasional    |

### Bias Integration Formula

```
FUND_BIAS_SCORE = 0.25(policy_diff)
                + 0.20(inflation_diff)
                + 0.15(commodity_corr)
                + 0.20(risk_sentiment)
                + 0.20(carry_diff)
```

Normalisasi skor ke 0–1:

- ≥0.65 → BULLISH
- 0.35–0.65 → NEUTRAL
- ≤0.35 → BEARISH

---

## 🧩 Penggunaan Dalam Pipeline

```
... → FTA (L10) → FUNDAMENTAL DRIVE (L11.5) → Adaptive Risk (L11) → Fusion (L12)
```

Modul ini tidak memberi sinyal entry langsung, melainkan mempengaruhi:

- Risk Fraction Adjustment
- Fusion Confidence Weight (CONF₁₂)
- Bias Sinkronisasi Reflective Layer

---

## 📊 Output Format

```json
{
  "pair": "CADJPY",
  "layer": "L11.5-FUNDAMENTAL",
  "FUND_BIAS_SCORE": 0.72,
  "FUND_BIAS_DIR": "BULLISH",
  "timestamp": "2025-11-12T13:00:00Z"
}
```

---

## 🧠 Relasi ke Modul TUYUL Lain

| Layer     | Modul                | Hubungan                                             |
| :-------- | :------------------- | :--------------------------------------------------- |
| L10       | FTA / FIB Confluence | Menyediakan konteks makro bagi confluence teknikal   |
| L11.5     | Fundamental Drive    | Menghasilkan bias makro kuantitatif                  |
| L11       | Adaptive Risk Engine | Menyesuaikan `adjusted_risk` berdasarkan bias        |
| L12       | Fusion Spectre       | Mengintegrasikan hasil akhir ke `CONF₁₂` dan `WLWCI` |

---

> Teknikal memberi sinyal kapan masuk, fundamental memberi alasan kenapa harga bergerak.
> Serigala bijak menggunakan keduanya. ⚡🐺

