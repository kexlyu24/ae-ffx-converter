"""Patch the FFX format gate to AE 2025; does not translate newer AE features."""
from pathlib import Path
import argparse
import struct
import sys


def convert(source: Path, destination: Path) -> None:
    data = bytearray(source.read_bytes())
    if len(data) < 36 or data[:4] != b"RIFX" or data[8:12] != b"FaFX":
        raise ValueError("Bukan preset RIFX/FaFX yang didukung")
    end = 8 + struct.unpack_from(">I", data, 4)[0]
    if end > len(data) or end < 36:
        raise ValueError("Ukuran kontainer tidak valid")
    # Validate chunk boundaries without interpreting or dropping any payload.
    stack = [(12, end)]
    heads = []
    while stack:
        pos, boundary = stack.pop()
        while pos < boundary:
            if pos + 8 > boundary:
                raise ValueError("Header chunk terpotong")
            tag = data[pos:pos + 4]
            size = struct.unpack_from(">I", data, pos + 4)[0]
            stop = pos + 8 + size
            padded = stop + (size & 1)
            if padded > boundary:
                raise ValueError("Isi chunk terpotong")
            if tag == b"LIST":
                if size < 4:
                    raise ValueError("LIST tidak valid")
                stack.append((pos + 12, stop))
            if tag == b"head" and boundary == end:
                heads.append((pos + 8, size))
            pos = padded
    if heads != [(20, 16)] or struct.unpack_from(">I", data, 20)[0] != 3:
        raise ValueError("Layout head tidak dikenal; file tidak diubah")
    version = struct.unpack_from(">I", data, 24)[0]
    if version not in (0x60, 0x61):
        raise ValueError(f"Versi 0x{version:x} tidak didukung; hanya AE 2025/2026")
    struct.pack_into(">I", data, 24, 0x60)
    if source.resolve() == destination.resolve():
        raise ValueError("Output tidak boleh menimpa sumber")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        output.write(data)
    print(f"OK: {source.name} -> {destination} (0x{version:x} -> 0x60)")
    if b"ADBE Text VF Axis" in data:
        print("  PERINGATAN: properti variable-font ditemukan; kompatibilitas AE 2025 belum terverifikasi.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path, help="Default: semua .ffx di folder tool")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "AE2025")
    args = parser.parse_args()
    files = args.files or sorted(Path(__file__).resolve().parent.glob("*.ffx"))
    if not files:
        parser.error("Tidak ada file .ffx")
    failed = False
    for source in files:
        try:
            convert(source, args.output / source.name)
        except (OSError, ValueError) as error:
            print(f"GAGAL: {source}: {error}", file=sys.stderr)
            failed = True
    print("Hanya penanda format yang dikonversi. Uji animasi di AE 2025 sebelum dipakai produksi.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
