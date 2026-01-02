# 🧠 FUNDAMENTAL DRIVE KNOWLEDGE v5.3.3 – TUYUL FX ULTRA WOLF

## 🎯 PURPOSE

Memberikan **bias makroekonomi terukur** dalam pipeline TUYUL FX AGI. Modul ini **tidak menggantikan** analisis teknikal, melainkan berfungsi sebagai **“angin arah makro”** yang memandu pengambilan risiko dan konfirmasi tren jangka menengah.

---

## 🔍 CORE VARIABLES

| Faktor           | Deskripsi                                                       | Rentang     | Dampak                               |
| :--------------- | :-------------------------------------------------------------- | :---------- | :----------------------------------- |
| `policy_diff`    | Perbedaan kebijakan moneter antar mata uang (hawkish vs dovish) | -1.0 → +1.0 | Penggerak arah utama                 |
| `inflation_diff` | Selisih inflasi antar ekonomi                                   | -1.0 → +1.0 | Menentukan arah kebijakan suku bunga |
| `commodity_corr` | Korelasi terhadap harga komoditas (oil, gold, copper)           | -1.0 → +1.0 | Dukungan fundamental CAD, AUD, NZD   |
| `risk_sentiment` | Mode pasar global (risk-on/off)                                 | -1.0 → +1.0 | Menekan/penguatan JPY & USD          |
| `carry_diff`     | Selisih yield antar mata uang                                   | -1.0 → +1.0 | Indikasi arus modal internasional    |

---

## ⚙️ FORMULA INTEGRASI

```text
FUND_BIAS_SCORE = 0.25(policy_diff)
                + 0.20(inflation_diff)
                + 0.15(commodity_corr)
                + 0.20(risk_sentiment)
                + 0.20(carry_diff)
```

Normalisasi skor ke 0–1:

* ≥ **0.65 → BULLISH**
* 0.35–0.65 → NEUTRAL
* ≤ **0.35 → BEARISH**

---

## 🧩 PENGGUNAAN DALAM PIPELINE

```
... → FTA (L10) → FUNDAMENTAL DRIVE (L11.5) → Adaptive Risk (L11) → Fusion (L12)
```

Modul ini **tidak memberi sinyal entry langsung**, melainkan mempengaruhi:

* **Risk Fraction Adjustment**
* **Fusion Confidence Weight (CONF₁₂)**
* **Bias Sinkronisasi Reflective Layer**

---

## 📊 OUTPUT FORMAT

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

## 📓 INTERPRETASI PRAKTIS

| Skor      | Arah           | Strategi                                              |
| --------- | -------------- | ----------------------------------------------------- |
| ≥0.75     | Bullish kuat   | Prioritaskan **buy trend**, hindari **short counter** |
| 0.50–0.75 | Netral positif | Risiko normal, ikuti arah momentum                    |
| 0.35–0.50 | Netral negatif | Kurangi leverage, tunggu konfirmasi                   |
| ≤0.35     | Bearish kuat   | Hindari buy, fokus **sell setup**                     |

---

## 🧠 RELASI KE MODUL TUYUL LAIN

| Layer     | Modul                | Hubungan                                             |
| :-------- | :------------------- | :--------------------------------------------------- |
| **L10**   | FTA / FIB Confluence | Menyediakan konteks makro bagi confluence teknikal   |
| **L11.5** | Fundamental Drive    | Menghasilkan bias makro kuantitatif                  |
| **L11**   | Adaptive Risk Engine | Menyesuaikan `adjusted_risk` berdasarkan bias        |
| **L12**   | Fusion Spectre       | Mengintegrasikan hasil akhir ke `CONF₁₂` dan `WLWCI` |

---

> “Teknikal membaca perilaku harga, fundamental membaca arus kekuatan di baliknya.
> TUYUL menyatukan keduanya menjadi kesadaran reflektif makro yang hidup.” ⚡🐺

---
