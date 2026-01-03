# TUYUL FX — Reflective Simulation & Drift Feedback Sandbox (Offline Diagnostic Manual v6.0r++)

## 1. Tujuan Sandbox Reflective System

Sandbox reflektif TUYUL FX dibuat untuk:

- Menguji kestabilan sistem reflektif tanpa koneksi cloud atau Vault runtime.
- Melatih dan mengkalibrasi parameter alpha–beta–gamma serta learning gain adaptif (REE).
- Menganalisis respons sistem reflektif terhadap drift, energi TRQ–3D, dan field resonance.
- Mengukur integritas harmonik antar layer (Hybrid, FX, Kartel, Journal).

Semua pengujian dilakukan di lingkungan aman, tanpa mempengaruhi Vault asli.

---

## 2. Struktur Sandbox

Folder `sandbox_reflective/` berisi:

```
├── run_reflective_simulation.py          # Simulasi reflektif penuh (TRQ–3D + alpha beta gamma)
├── test_feedback_drift_loop.py           # Uji drift dan recovery adaptif
└── configs/
    ├── simulation_params.yml             # Parameter eksperimen utama
    ├── mock_vault_state.json             # State Quad Vault tiruan
    └── logs/                             # Folder hasil uji simulasi
```

---

## 3. Siklus Eksperimen Reflective

Setiap simulasi sandbox menjalankan 5–10 siklus yang mencakup:

| Langkah | Modul            | Fungsi                                                  |
| ------- | ---------------- | ------------------------------------------------------- |
| 1       | TRQ3D Engine     | Hitung energi reflektif (price × time × volume)         |
| 2       | Drift Simulation | Hasilkan deviasi acak alpha–beta–gamma untuk uji stabilitas |
| 3       | REE Analysis     | Analisis drift dan koherensi reflektif                  |
| 4       | Field Resonance  | Petakan resonansi dan hitung stabilitas medan reflektif |
| 5       | Integrity Check  | Evaluasi integritas dan pemicu auto-recovery            |
| 6       | Logging          | Simpan semua hasil ke `sandbox_reflective/logs/`        |

---

## 4. Menjalankan Simulasi

### Mode 1: Simulasi Reflektif Penuh

Jalankan:

```bash
python sandbox_reflective/run_reflective_simulation.py
```

Hasil:

- Setiap siklus mencetak energi TRQ–3D, drift alpha beta gamma, dan integritas sistem.
- Log otomatis tersimpan di: `sandbox_reflective/logs/simulation_<timestamp>.json`

### Mode 2: Uji Drift Feedback Loop

Jalankan:

```bash
python sandbox_reflective/test_feedback_drift_loop.py
```

Hasil:

- Menunjukkan stabilitas sistem terhadap perubahan besar alpha–beta–gamma.
- Jika integrity < 0.93, sistem menjalankan recovery adaptif.

---

## 5. Parameter Eksperimen

Semua parameter dikontrol dari `configs/simulation_params.yml`.

Contoh:

```yaml
reflective_field:
  alpha_variance: 0.025
  beta_variance: 0.020
  gamma_variance: 0.022

drift_simulation:
  drift_amplitude_alpha: 0.018
  recovery_trigger_threshold: 0.93
```

Rekomendasi:

| Kondisi       | Parameter                | Nilai Disarankan |
| ------------- | ------------------------ | ---------------- |
| Pasar Tenang  | alpha beta gamma variance| 0.010–0.015      |
| Pasar Volatil | alpha beta gamma variance| 0.020–0.030      |
| Uji Recovery  | Drift amplitude          | ≥ 0.018          |
| Stress Test   | Reflective intensity max | ≥ 1.20           |

---

## 6. Hasil yang Harus Diperhatikan

| Indikator              | Ideal     | Arti                                        |
| ---------------------- | --------- | ------------------------------------------- |
| reflective_coherence   | ≥ 0.94    | Sinkronisasi antar-layer stabil             |
| integrity_index        | ≥ 0.95    | Sistem reflektif sehat                      |
| reflective_intensity   | 1.05–1.15 | Energi TRQ–3D aktif tapi seimbang           |
| harmonic_alignment     | ≥ 0.95    | Medan reflektif dalam harmonic lock         |
| drift_mean             | < 0.01    | Drift stabil, pembelajaran adaptif berhasil |

Jika integrity_index < 0.93 maka recovery dijalankan otomatis melalui REEIntegrityController.

---

## 7. Log dan Analisis

Semua log disimpan di:

```
sandbox_reflective/logs/
  ├── simulation_<timestamp>.json
  ├── drift_test_<timestamp>.json
  ├── reflective_sandbox.log
```

Gunakan `data/logs/reflective_cycle_log.json` untuk membandingkan dengan runtime asli TUYUL FX.

---

## 8. Tips Tuning Adaptif

| Tujuan                  | Parameter                     | Aksi                              |
| ----------------------- | ----------------------------- | --------------------------------- |
| Menambah sensitivitas   | learning_gain_max naik        | Reaksi lebih cepat terhadap drift |
| Menurunkan overreaction | decay_rate naik               | Kurangi fluktuasi gain            |
| Menstabilkan resonansi  | harmonic_alignment_target naik| Medan lebih harmonik              |
| Mempercepat recovery    | boost_factor naik             | Auto-recovery lebih agresif       |

---

## 9. Integrasi ke Sistem Nyata

Setelah eksperimen stabil:

1. Salin hasil konfigurasi dari `simulation_params.yml` ke `core_meta/configs/ree_adaptive_drift_config.yml`.
2. Sinkronisasi Vault dengan:

   ```bash
   python server_api/routes/vault.py --sync
   ```

3. Jalankan reflective runtime:

   ```bash
   python core_reflective/system_bootstrap.py
   ```

---

## 10. Kesimpulan

- Sandbox reflektif adalah laboratorium tertutup TUYUL FX Ultimate.
- Memungkinkan uji cepat, tuning parameter, dan validasi integritas reflektif tanpa cloud.
- Semua hasil simulasi akan masuk ke Journal Vault setelah sinkronisasi berikutnya.

Mode: Reflective Discipline (Offline) — Integrity Vault: Stable (≥ 0.95) — Harmonic Lock: Active — Status: Ready for Live Synchronization
