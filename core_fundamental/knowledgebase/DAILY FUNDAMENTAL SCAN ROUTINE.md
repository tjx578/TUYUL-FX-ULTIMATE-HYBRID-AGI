# 🧠 DAILY FUNDAMENTAL SCAN ROUTINE v5.3.3+

## TUYUL FX – Morning Wolf Process 🐺⚡

### 📄 Deskripsi Singkat (≤350 karakter)

> **Routine scanning manual TUYUL FX AGI** untuk menentukan bias fundamental harian berdasarkan
> kalender ekonomi, kekuatan mata uang, risiko makro, dan sentimen global.
> Output: Ranking 8 mata uang, 3 pair prioritas, dan jurnal harian reflektif.

---

### ⚙️ Fungsi Dalam Sistem TUYUL FX

| Layer | Modul                  | Fungsi                                       |
| :---- | :--------------------- | :------------------------------------------- |
| L11.2 | HighImpactMonitor      | Deteksi event berdampak tinggi               |
| L11.3 | WeeklyOutlookSync      | Agregasi makro harian → mingguan             |
| L11.4 | FundamentalScanner     | Eksekusi rutin pagi hari                     |
| L11.5 | FundamentalDriveEngine | Menggabungkan bias makro dengan pipeline AI  |
| L12   | Fusion Layer           | Integrasi bias reflektif untuk reasoning AGI |

---

### 🧩 Integrasi Otomatis

* File ini digunakan oleh modul `fundamental_scanner.py`.
* Hasil dipublikasikan ke:
  * `/data/journals/fundamental_journal.json`
  * `/quad_vaults/journal_vault/session_logs/reflective_log_YYYYMMDD.json`
* Sinkron ke **REE Feedback (L17)** setiap minggu via `weekly_outlook_sync.py`.

---

### 🧠 Keterkaitan Modul

```
CB Policy Tracker (cb_policy_tracker.json)
     ↓
Event Risk Matrix (event_risk_matrix.json)
     ↓
FundamentalAutoFeed v5.3.3
     ↓
Daily Scan Routine (ini)
     ↓
Fundamental Drive Engine
     ↓
Fusion Reflective Layer (CONF₁₂)
```

---

### 🗂️ Penempatan File

```
core_fundamental/
└── knowledgebase/
    ├── fundamental_knowledgebase.md
    ├── DAILY FUNDAMENTAL SCAN ROUTINE.md  ✅
    └── economic_terms_reference.json
```

---

### ✅ Tujuan Operasional

* Menciptakan **habit reflektif makro harian** (before London Open).
* Meningkatkan **precision fusion** antara *fundamental bias* dan *technical alignment (FTA)*.
* Mengurangi risiko overtrade & bias tanpa data.

---

### ✅ STEP 1: News Calendar Check (3 min)

```
SOURCES:
├─ ForexFactory.com/calendar
├─ TradingEconomics.com/calendar
└─ FXStreet.com/economic-calendar

FILTER SETTINGS:
☐ Date: TODAY
☐ Impact: HIGH only
☐ Time Zone: GMT+7 (WIB)

RECORD:
Time  | Event                    | Currency | Impact
------|--------------------------|----------|-------
XX:XX | [Event Name]             | XXX      | HIGH
XX:XX | [Event Name]             | XXX      | HIGH

MARK NO-TRADE WINDOWS:
├─ [Time] - [Time]: [Currency] [Event]
└─ Rule: No trades ±30 min dari high-impact news
```

---

### ✅ STEP 2: Quick Currency Strength (8 min)

**For Each Currency (USD, EUR, GBP, JPY, AUD, CAD, NZD, CHF):**

```
A. MONETARY POLICY (Quick Check):
   CB Rate? [X.XX%]
   Bias? [Hawkish/Neutral/Dovish]
   Last Action? [Hike/Hold/Cut]
   
B. COMMODITY LINK (If Applicable):
   CAD: Oil price? [$XX]
        → >$85 = Strong | $75-85 = Neutral | <$75 = Weak
   
   AUD: Gold price? [$XXXX]
        → >$2050 = Strong | $1900-2050 = Neutral | <$1900 = Weak
   
   NZD: Dairy index? [XXXX]
        → >3500 = Strong | 3000-3500 = Neutral | <3000 = Weak

C. RISK SENTIMENT:
   VIX? [XX.X]
   → <15 = Risk-on (favor AUD/NZD/CAD)
   → >25 = Risk-off (favor JPY/CHF/USD)
   
   S&P 500 yesterday? [Up/Down X%]
   → Up >0.5% = Risk-on
   → Down >1% = Risk-off

D. QUICK SCORE (Mental Math):
   Policy: +/- points
   Commodity: +/- points
   Sentiment: +/- points
   → TOTAL: [Score]
```

**SHORTCUT METHOD (Use Scanner):**

```python
# If using automated scanner:
python fundamental_scanner.py --mode morning --quick

# Output example:
# USD: 65 | EUR: 55 | GBP: 62 | JPY: 38
# AUD: 52 | CAD: 35 | NZD: 48 | CHF: 45
```

---

### ✅ STEP 3: Rank & Pair Selection (3 min)

```
RANKING (Strongest → Weakest):
1. [XXX]: Score [XX]
2. [XXX]: Score [XX]
3. [XXX]: Score [XX]
4. [XXX]: Score [XX]
5. [XXX]: Score [XX]
6. [XXX]: Score [XX]
7. [XXX]: Score [XX]
8. [XXX]: Score [XX]

IDENTIFY STRONG PAIRS (Diff ≥20):
✅ [XXX][XXX]: Diff +XX (STRONG)
✅ [XXX][XXX]: Diff +XX (STRONG)
✅ [XXX][XXX]: Diff +XX (MODERATE)

WATCHLIST FOR TECHNICAL ANALYSIS:
├─ Priority 1: [PAIR] ([Reason])
├─ Priority 2: [PAIR] ([Reason])
└─ Priority 3: [PAIR] ([Reason])
```

---

### ✅ STEP 4: Document & Set Alerts (1 min)

```
SAVE TO JOURNAL:
────────────────────────────────────────
📅 [DATE] FUNDAMENTAL SCAN
────────────────────────────────────────
Top: [XXX] (Score: XX)
Bottom: [XXX] (Score: XX)
Key Driver: [Oil/Risk-on/News/etc]
High-Impact News: [List]
────────────────────────────────────────
WATCHLIST:
1. [PAIR] - [Bias] (F-Conf: XX%)
2. [PAIR] - [Bias] (F-Conf: XX%)
3. [PAIR] - [Bias] (F-Conf: XX%)
────────────────────────────────────────

SET PRICE ALERTS:
☐ [PAIR]: Alert @ [Price] (entry zone)
☐ [PAIR]: Alert @ [Price] (entry zone)
☐ [PAIR]: Alert @ [Price] (entry zone)

SET TIME ALERTS:
☐ XX:00 - Pre-news reminder ([Event])
☐ XX:00 - Pre-news reminder ([Event])
```

---

## 📊 SCAN OUTPUT TEMPLATE

```
════════════════════════════════════════════════════════════
🐺 FUNDAMENTAL SCAN: [Day, Date Month Year]
════════════════════════════════════════════════════════════

⏰ SCAN TIME: 06:00 WIB

📅 HIGH-IMPACT NEWS TODAY:
├─ [Time]: [Currency] - [Event]
├─ [Time]: [Currency] - [Event]
└─ [Time]: [Currency] - [Event]

🚫 NO-TRADE WINDOWS:
├─ [Start]-[End]: [Reason]
└─ [Start]-[End]: [Reason]

════════════════════════════════════════════════════════════
💪 CURRENCY STRENGTH RANKING:
════════════════════════════════════════════════════════════
1. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
2. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
3. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
4. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
5. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
6. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
7. [XXX]: [Score] | [Hawkish/Neutral/Dovish]
8. [XXX]: [Score] | [Hawkish/Neutral/Dovish]

════════════════════════════════════════════════════════════
🔑 KEY FUNDAMENTAL DRIVERS TODAY:
════════════════════════════════════════════════════════════
Primary: [Description - e.g., "Oil $62 driving CAD weakness"]
Secondary: [Description - e.g., "Risk-on supporting AUD"]
Risk: [Description - e.g., "Fed speech tonight = volatility"]

════════════════════════════════════════════════════════════
🎯 PAIR WATCHLIST (Diff ≥20):
════════════════════════════════════════════════════════════

🥇 PRIORITY 1: [PAIR]
   ├─ Differential: +[XX] ([Strong/Moderate])
   ├─ Bias: [BULLISH/BEARISH]
   ├─ F-Confidence: [XX]%
   ├─ Key Driver: [Reason]
   └─ Entry Idea: [LONG/SHORT] on [H4/D1] structure

🥈 PRIORITY 2: [PAIR]
   ├─ Differential: +[XX]
   ├─ Bias: [BULLISH/BEARISH]
   ├─ F-Confidence: [XX]%
   ├─ Key Driver: [Reason]
   └─ Entry Idea: [LONG/SHORT] on [H4/D1] structure

🥉 PRIORITY 3: [PAIR]
   ├─ Differential: +[XX]
   ├─ Bias: [BULLISH/BEARISH]
   ├─ F-Confidence: [XX]%
   ├─ Key Driver: [Reason]
   └─ Entry Idea: [LONG/SHORT] on [H4/D1] structure

════════════════════════════════════════════════════════════
📝 TRADING NOTES:
════════════════════════════════════════════════════════════
[Any special considerations for today]

════════════════════════════════════════════════════════════
```

---

## 📋 REAL EXAMPLE (Oct 9, 2025)

```
════════════════════════════════════════════════════════════
🐺 FUNDAMENTAL SCAN: Wednesday, 09 October 2025
════════════════════════════════════════════════════════════

⏰ SCAN TIME: 06:15 WIB

📅 HIGH-IMPACT NEWS TODAY:
├─ 14:30: USD - Initial Jobless Claims
├─ 20:00: CAD - BoC Governor Macklem Speech
└─ 21:00: EUR - ECB Press Conference

🚫 NO-TRADE WINDOWS:
├─ 14:00-15:00: USD volatility (Jobless Claims)
├─ 19:30-20:30: CAD volatility (BoC speech)
└─ 20:30-21:30: EUR volatility (ECB presser)

════════════════════════════════════════════════════════════
💪 CURRENCY STRENGTH RANKING:
════════════════════════════════════════════════════════════
1. USD: 65 | Dovish (but high rate 4.125%)
2. GBP: 62 | Hawkish (BoE firm stance)
3. EUR: 55 | Neutral (ECB wait-and-see)
4. AUD: 52 | Neutral (RBA on hold)
5. NZD: 48 | Neutral (RBNZ neutral)
6. CHF: 45 | Neutral (SNB passive)
7. JPY: 38 | Dovish (BoJ ultra-loose)
8. CAD: 35 | Dovish (BoC aggressive cuts + Oil weak) ⬅️ WEAKEST

════════════════════════════════════════════════════════════
🔑 KEY FUNDAMENTAL DRIVERS TODAY:
════════════════════════════════════════════════════════════
Primary: Oil $62.18 (<$75 threshold) = CAD MASSIVE WEAKNESS
         → All CAD pairs bearish bias for CAD
         
Secondary: Fed/BoC rate differential +162.5 bps (abnormal)
           → USDCAD strong bullish bias
           
Tertiary: Moderate risk-on (VIX 16.3) = Slight AUD/NZD support
          → But oil dominates for CAD

Risk: BoC speech 20:00 tonight (potential volatility)
      → Close/hedge CAD positions before 19:30

════════════════════════════════════════════════════════════
🎯 PAIR WATCHLIST (Diff ≥20):
════════════════════════════════════════════════════════════

🥇 PRIORITY 1: USDCAD
   ├─ Differential: +30 (VERY STRONG)
   ├─ Bias: BULLISH
   ├─ F-Confidence: 88%
   ├─ Key Driver: Oil $62 + Rate gap +162.5bps
   └─ Entry Idea: LONG on H4 pullback to 1.3960-1.3970
                  OR break above 1.4020

🥈 PRIORITY 2: GBPCAD
   ├─ Differential: +27 (STRONG)
   ├─ Bias: BULLISH
   ├─ F-Confidence: 82%
   ├─ Key Driver: Oil weakness + GBP hawkish BoE
   └─ Entry Idea: LONG on H4 structure support

🥉 PRIORITY 3: USDJPY
   ├─ Differential: +27 (STRONG)
   ├─ Bias: BULLISH
   ├─ F-Confidence: 75%
   ├─ Key Driver: Fed/BoJ rate differential + Safe-haven flows
   └─ Entry Idea: LONG on D1 demand zone test

════════════════════════════════════════════════════════════
📝 TRADING NOTES:
════════════════════════════════════════════════════════════
• CAD shorts highly favored (oil critical weakness)
• Watch BoC speech 20:00 for surprises
• USD pairs mixed (dovish Fed but high rate)
• Risk-on modest, not strong enough to override oil factor
• JPY weakness continues (BoJ dovish)

🐺 Wolf Strategy Today: 
   Focus on CAD shorts, especially USDCAD (highest conviction)
   Avoid CAD longs completely
   Close CAD exposure before BoC speech 19:30

════════════════════════════════════════════════════════════
```

---

## ⚡ QUICK REFERENCE CARDS

### Card 1: Currency Scoring Quick Guide

```
┌─────────────────────────────────────────┐
│ QUICK CURRENCY SCORING                  │
├─────────────────────────────────────────┤
│                                         │
│ HAWKISH CB = +20-30 points              │
│ DOVISH CB = -20-30 points               │
│                                         │
│ OIL >$85 = CAD +25                      │
│ OIL <$75 = CAD -25                      │
│                                         │
│ GOLD >$2050 = AUD +20                   │
│ GOLD <$1900 = AUD -15                   │
│                                         │
│ VIX <15 = Risk-on (+AUD/NZD/CAD)        │
│ VIX >25 = Risk-off (+JPY/CHF/USD)       │
│                                         │
│ STRONG DIFF = ≥20 points                │
│ MODERATE DIFF = 15-20 points            │
│ WEAK DIFF = <15 points (skip)           │
│                                         │
└─────────────────────────────────────────┘
```

### Card 2: News Impact Hierarchy

```
┌─────────────────────────────────────────┐
│ NEWS IMPACT LEVELS                      │
├─────────────────────────────────────────┤
│                                         │
│ TIER 1 (Close positions ±30 min):       │
│ ├─ Interest Rate Decisions              │
│ ├─ NFP (US Employment)                  │
│ ├─ CPI / Inflation Data                 │
│ └─ Central Bank Speeches                │
│                                         │
│ TIER 2 (Monitor, adjust SL):            │
│ ├─ GDP Reports                          │
│ ├─ Retail Sales                         │
│ ├─ PMI Data                             │
│ └─ Trade Balance                        │
│                                         │
│ TIER 3 (Minimal adjustment):            │
│ ├─ Consumer Confidence                  │
│ ├─ Housing Data                         │
│ └─ Minor Speeches                       │
│                                         │
└─────────────────────────────────────────┘
```

### Card 3: Pair Selection Matrix

```
┌──────────────┬──────────┬───────────┐
│ Differential │ Action   │ F-Conf    │
├──────────────┼──────────┼───────────┤
│ ≥30 points   │ ✅ STRONG│ 85-95%    │
│ 20-29 points │ ✅ TRADE │ 70-84%    │
│ 15-19 points │ ⚠️ WATCH │ 60-69%    │
│ <15 points   │ ❌ SKIP  │ <60%      │
└──────────────┴──────────┴───────────┘
```

---

## 🤖 AUTOMATION OPTIONS

### Option 1: Python Scanner

```bash
# Run automated scanner
python fundamental_scanner.py --mode morning

# Output: Currency scores + watchlist
# Time saved: 10 minutes
```

### Option 2: Spreadsheet Template

```
Download: fundamental_scan_template.xlsx
├─ Tab 1: CB Policy Tracker (update monthly)
├─ Tab 2: Daily Commodity Prices (update daily)
├─ Tab 3: Auto-Calculate Scores
└─ Tab 4: Watchlist Generator

Time: 5 minutes (just input prices)
```

### Option 3: TradingView Scanner

```
Custom Scanner Settings:
├─ Scan: All Forex Majors + Crosses
├─ Filter: Price vs EMAs
├─ Sort: By volume
└─ Manual fundamental overlay

Time: 15 minutes (hybrid approach)
```

---

## 🎯 SUCCESS METRICS

**Track Weekly:**

```
☐ Scans completed: [X/7] days
☐ Average scan time: [XX] minutes
☐ Watchlist accuracy: [XX]%
☐ High-impact news identified: [X]
☐ Successful F-bias calls: [X/Y] = [XX]%
```

**Review Monthly:**

```
☐ Most accurate fundamental drivers
☐ Missed opportunities (why?)
☐ False signals (what went wrong?)
☐ Time optimization achieved
☐ Scan process improvements needed
```

---

## ⚠️ CRITICAL REMINDERS

```
1. ⏰ CONSISTENCY > PERFECTION
   → Scan setiap pagi, even weekends (note Sunday gap)
   
2. 📝 DOCUMENT ALWAYS
   → "If not journaled, didn't happen"
   
3. 🚫 NO TRADING WITHOUT SCAN
   → Fundamental blind = gambling
   
4. 🔄 UPDATE MONTHLY
   → CB rates, bias, commodity thresholds
   
5. ⚡ SPEED COMES WITH PRACTICE
   → Week 1: 30 min | Week 4: 15 min | Week 12: 10 min
   
6. 🎯 QUALITY > QUANTITY
   → 1 strong signal > 5 weak signals
```

---

## 🐺 WOLF MORNING MANTRAS

```
"Scan pertama, trade kedua, profit ketiga"

"Oil price adalah darah CAD, VIX adalah mood market"

"20-point differential = green light, <15 = red light"

"News calendar bukan prediksi, tapi awareness"

"Ranking currency = peta, technical analysis = kompas"

"Morning scan 06:00 = competitive edge vs retail traders"

"Fundamental tanpa technical = peta tanpa arah"
"Technical tanpa fundamental = arah tanpa tujuan"
```

---

**⏰ SCAN CHECKLIST SUMMARY**

```
MORNING ROUTINE (15-20 MIN):
☐ [ 3 min] News calendar → Mark events
☐ [ 8 min] Currency strength → Rank 1-8
☐ [ 3 min] Pair selection → Watchlist
☐ [ 1 min] Document → Journal + Alerts
☐ [Done!] Ready for technical analysis

THEN:
→ Proceed to SOP Multi-Pair Phase 2 (Technical)
→ Combine F+T for FTA Score
→ Execute only ≥65% setups
```

---

🧠 **Kesimpulan Akhir**

> **DAILY FUNDAMENTAL SCAN ROUTINE v5.3.3+** adalah fondasi reflektif sistem TUYUL FX AGI.
> Mengubah analisis makro manual menjadi proses disiplin, terukur, dan otomatis —
> diintegrasikan langsung dengan Fusion & Reflective Layers. ⚡🐺

---
