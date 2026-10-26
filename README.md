# Konversi preset ke AE 2025

Jalankan `python convert_ae2025.py` untuk mengonversi seluruh `.ffx` di folder tool ke subfolder `AE2025`. Tidak memerlukan paket Python tambahan. Untuk memilih file:

```
python convert_ae2025.py "SaaS Text 1.ffx" "SaaS Text 2.ffx" --output AE2025
```

File sumber tidak diubah. Output yang sudah ada ditolak, bukan ditimpa; gunakan folder output lain untuk mengulang.

Tool memvalidasi kontainer RIFX/FaFX dan mengubah field versi dari `0x61` ke `0x60`. Semua payload, termasuk metadata XMP di luar kontainer, dipertahankan. Pemetaan versi mengacu pada https://github.com/Kisev2/FFX-Downgrader . Ini adalah patch penanda format, bukan penerjemah fitur AE 2026.

Kedua preset telah dikonversi dan diperiksa: ukuran tetap, hanya byte pada offset 27 berubah. Keduanya mengandung properti `ADBE Text VF Axis 1` sampai `8`; keberadaan field ini tidak membuktikan bahwa animasinya menggunakan variable font, tetapi kompatibilitasnya belum teruji.

## Pengujian yang masih diperlukan

AE 2025 tidak ditemukan pada instalasi lokal yang diperiksa. Hasil belum dinyatakan kompatibel penuh.

Di AE 2025, buat composition dan text layer, pilih layer tersebut, lalu gunakan Animation > Apply Animation Preset untuk memilih masing-masing file dari folder AE2025. Periksa pesan error, expression, font, keyframe, serta hasil animasi sepanjang durasinya. Bandingkan dengan preset asli di AE 2026 menggunakan teks, font, frame rate, dan waktu layer yang sama. Jangan mengganti preset produksi sebelum hasil tersebut cocok.
