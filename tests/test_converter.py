import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest

from convert_ae2025 import convert


def chunk(tag, payload):
    return tag + struct.pack(">I", len(payload)) + payload + b"\0" * (len(payload) % 2)


def preset(version=0x61):
    head = chunk(b"head", struct.pack(">IIII", 3, version, 10, 0x017F0000))
    payload = chunk(b"LIST", b"besc" + chunk(b"data", b"odd"))
    body = b"FaFX" + head + payload
    return b"RIFX" + struct.pack(">I", len(body)) + body + b"<?xpacket test?>"


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "input.ffx"
        self.output = Path(self.directory.name) / "output.ffx"
        self.stdout = contextlib.redirect_stdout(io.StringIO())
        self.stdout.__enter__()
        self.addCleanup(self.stdout.__exit__, None, None, None)

    def test_patch_preserves_payload_padding_metadata_and_source(self):
        original = preset()
        self.source.write_bytes(original)
        convert(self.source, self.output)
        expected = bytearray(original)
        expected[27] = 0x60
        self.assertEqual(self.output.read_bytes(), expected)
        self.assertEqual(self.source.read_bytes(), original)

    def test_2025_input_is_copied_without_changes(self):
        original = preset(0x60)
        self.source.write_bytes(original)
        convert(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), original)

    def test_existing_output_is_not_overwritten(self):
        self.source.write_bytes(preset())
        self.output.write_bytes(b"existing content")
        with self.assertRaises(FileExistsError):
            convert(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), b"existing content")

    def test_source_cannot_be_output(self):
        original = preset()
        self.source.write_bytes(original)
        with self.assertRaises(ValueError):
            convert(self.source, self.source)
        self.assertEqual(self.source.read_bytes(), original)

    def test_unsupported_or_malformed_inputs_produce_no_output(self):
        bad_size = bytearray(preset())
        struct.pack_into(">I", bad_size, 4, len(bad_size) + 100)
        bad_nested = bytearray(preset())
        struct.pack_into(">I", bad_nested, 52, 1000)
        bad_layout = bytearray(preset())
        struct.pack_into(">I", bad_layout, 20, 99)
        missing_padding = bytearray(preset())
        struct.pack_into(">I", missing_padding, 40, 15)
        for data in (b"not a preset", preset(0x62), bad_size,
                     bad_nested, bad_layout, missing_padding):
            with self.subTest(data=bytes(data)):
                self.source.write_bytes(data)
                with self.assertRaises(ValueError):
                    convert(self.source, self.output)
                self.assertFalse(self.output.exists())
                self.assertEqual(self.source.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
