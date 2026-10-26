"""Patch the FFX format gate to AE 2025; does not translate newer AE features."""
from pathlib import Path
import argparse
import struct
import sys


def convert(source: Path, destination: Path) -> None:
    data = bytearray(source.read_bytes())
    if len(data) < 36 or data[:4] != b"RIFX" or data[8:12] != b"FaFX":
        raise ValueError("Not a supported RIFX/FaFX preset")
    end = 8 + struct.unpack_from(">I", data, 4)[0]
    if end > len(data) or end < 36:
        raise ValueError("Invalid container size")
    # Validate chunk boundaries without interpreting or dropping any payload.
    stack = [(12, end)]
    heads = []
    while stack:
        pos, boundary = stack.pop()
        while pos < boundary:
            if pos + 8 > boundary:
                raise ValueError("Truncated chunk header")
            tag = data[pos:pos + 4]
            size = struct.unpack_from(">I", data, pos + 4)[0]
            stop = pos + 8 + size
            padded = stop + (size & 1)
            if padded > boundary:
                raise ValueError("Truncated chunk payload")
            if tag == b"LIST":
                if size < 4:
                    raise ValueError("Invalid LIST chunk")
                stack.append((pos + 12, stop))
            if tag == b"head" and boundary == end:
                heads.append((pos + 8, size))
            pos = padded
    if heads != [(20, 16)] or struct.unpack_from(">I", data, 20)[0] != 3:
        raise ValueError("Unknown head layout; file left unchanged")
    version = struct.unpack_from(">I", data, 24)[0]
    if version not in (0x60, 0x61):
        raise ValueError(f"Unsupported version 0x{version:x}; expected AE 2025/2026")
    struct.pack_into(">I", data, 24, 0x60)
    if source.resolve() == destination.resolve():
        raise ValueError("Output must not overwrite the source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        output.write(data)
    print(f"OK: {source.name} -> {destination} (0x{version:x} -> 0x60)")
    if b"ADBE Text VF Axis" in data:
        print("  WARNING: variable-font properties found; AE 2025 compatibility is unverified.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path, help="Input presets; defaults to all .ffx files beside this script")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "AE2025",
                        help="Output directory (default: AE2025 beside this script); existing files are never overwritten")
    args = parser.parse_args()
    files = args.files or sorted(Path(__file__).resolve().parent.glob("*.ffx"))
    if not files:
        parser.error("No .ffx files found")
    failed = False
    for source in files:
        try:
            convert(source, args.output / source.name)
        except (OSError, ValueError) as error:
            print(f"FAILED: {source}: {error}", file=sys.stderr)
            failed = True
    print("Only the format marker is patched. Test animations in AE 2025 before production use.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
