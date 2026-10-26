# AE FFX Converter

[![Checks](https://github.com/kexlyu24/ae-ffx-converter/actions/workflows/checks.yml/badge.svg)](https://github.com/kexlyu24/ae-ffx-converter/actions/workflows/checks.yml)

A dependency-free Python CLI that patches the format-version marker in Adobe After Effects 2026 animation presets (`.ffx`) to the AE 2025 marker.

> **Compatibility status:** this is a format-marker patcher, not a feature converter. Successful conversion does not prove that a preset loads or renders correctly in AE 2025. In-app AE 2025 verification is still required.

## Features

- Process individual presets or all `.ffx` files beside the script.
- Validate RIFX/FaFX container and chunk boundaries before writing.
- Keep source files untouched and refuse to overwrite existing output.
- Preserve animation payloads and trailing metadata, including XMP.
- Warn when variable-font property identifiers are present.
- Run with the Python standard library only.

## Requirements

- Python 3.9 or newer.
- After Effects 2025 for applying and verifying the output.
- Any fonts or third-party plugins required by your preset.

After Effects is not needed to run the patcher. No presets, Adobe software, or third-party assets are bundled.

## Quick start

Clone the repository, then run the script with your preset paths:

```sh
git clone https://github.com/kexlyu24/ae-ffx-converter.git
cd ae-ffx-converter
python convert_ae2025.py "path/to/My Preset.ffx" --output converted
```

On Windows, `py -3` can replace `python` if needed. Private repository access requires GitHub authentication.

### Batch conversion

```sh
python convert_ae2025.py "Title In.ffx" "Title Out.ffx" --output converted
```

Or place presets beside `convert_ae2025.py` and run:

```sh
python convert_ae2025.py
```

With no input arguments, the script scans only its own directory, not subdirectories. The default output is `AE2025` beside the script. An explicitly supplied relative output path is resolved against the current working directory.

```sh
python convert_ae2025.py --help
```

### Output and exit codes

Output files retain their input filenames. Existing output is never overwritten; choose a new output directory when repeating a conversion. Inputs with the same filename will collide in a shared output directory: the first successful write is kept and subsequent writes fail.

| Exit code | Meaning |
| --- | --- |
| `0` | All requested files were written successfully |
| `1` | At least one file failed; other files are still processed |
| `2` | Invalid CLI arguments or no input presets found |

A success message indicates a completed file operation, **not verified After Effects compatibility**.

## Supported format markers

| Input | Marker | Behavior |
| --- | --- | --- |
| AE 2026 | `0x61` | Patch to `0x60` |
| AE 2025 | `0x60` | Copy unchanged to a new output file |
| Other or unknown | Other values | Reject without writing output |

The supported layout has a 16-byte `head` chunk at offset 12 and header revision `3`. Its big-endian version field starts at offset 24. For `0x61` to `0x60`, only the byte at offset 27 changes.

The version-marker mapping is based on the community [FFX Downgrader documentation](https://github.com/Kisev2/FFX-Downgrader). It is not an Adobe-published format specification.

## Compatibility limits

The tool does **not** translate new effects, expressions, font features, or serialized properties. It does not install missing dependencies or remove unsupported effects. A variable-font warning only indicates that identifiers were found; it does not establish whether the animation actively uses them.

Two locally supplied AE 2026 presets were patched and compared byte-for-byte: their sizes were unchanged and only offset 27 differed. This verifies payload preservation for those files, not their behavior in AE 2025. They are intentionally excluded from this repository.

### Verify in After Effects 2025

1. Create a composition and select the appropriate target layer, such as a text layer for a text preset.
2. Choose **Animation > Apply Animation Preset** and select the converted `.ffx` file.
3. Check for load errors, missing fonts or plugins, and expression errors.
4. Preview the full animation and inspect keyframes and timing.
5. Compare against the original in AE 2026 with matching text, fonts, composition settings, and layer timing.

Do not replace a production preset until the results match.

## Troubleshooting

| Problem | Action |
| --- | --- |
| Output already exists | Choose a different `--output` directory |
| Unsupported version or unknown layout | Keep the original; this tool only supports the documented layout and markers |
| Invalid or truncated container | Obtain an intact source preset; do not force a header patch |
| Preset converts but AE rejects it | The marker patch is insufficient; capture the exact AE error |
| Animation looks different | Compare fonts, plugins, expressions, and features between AE versions |

## Development

Run the behavioral checks with no additional dependencies:

```sh
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on Windows and Linux with Python 3.9 and 3.14. Tests use synthetic containers rather than distributing proprietary presets. Automated checks cannot establish in-app rendering compatibility.

When reporting a problem, include the Python version, source and target AE versions, command used, and complete error message. Share presets only if you have permission to distribute them. Changes should preserve payload bytes and the no-overwrite behavior.

## Project scope

This repository targets the AE 2026-to-2025 format marker only. It is an independent project and is not affiliated with or endorsed by Adobe.
