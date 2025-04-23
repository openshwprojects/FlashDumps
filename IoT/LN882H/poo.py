import os

FIRMWARE_PATHS = [
    "C:\Users\divad\Documents\GitHub\FlashDumps\IoT\LN882H\Tuya_3.5.4_BSD34_EU_PLUG_(百视盾计量_schemaID-efnwqc)_WL2S_LN882H_1.0.4.bin",
    "C:\Users\divad\Documents\GitHub\FlashDumps\IoT\LN882H\Tuya_3.5.4_Farylink-UK_Plug_(Smart-Plug-schemaID-g2xobg)_cptnnkbvpdxkkcvy_FL-M118-V1.1_1.0.0.bin",
    "C:\Users\divad\Documents\GitHub\FlashDumps\IoT\LN882H\Tuya_3.5.4_FEIT_Chasing_FETAP20CAN_(schemaID-fxxrjk)_LN882H_1.0.18.bin",
]

KEY_MASTER = b"qwertyuiopasdfgh"  # 16 bytes

# The known strings from TuyaConfig.cs that, if found at start of a block, trigger XOR pass.
KEY_PART_1 = b"8710_2M"           # 7 bytes
KEY_PART_2 = b"HHRRQbyemofrtytf"  # 16 bytes

# How many bytes to XOR-decode (and examine) if we suspect a block start
DECODE_CHUNK_SIZE = 4096

# How much ASCII context to print from the decoded data
ASCII_CONTEXT = 256

def xor_decode(data: bytes, start_offset: int, key: bytes) -> bytes:
    """
    XOR-decode 'data' (a slice of the firmware) with 'key' in the same
    repeating pattern used by Tuya (BK7231).
    The offset matters, because the key index is (offset_in_firmware + i) % 16.
    """
    out = bytearray(data)
    key_len = len(key)
    for i in range(len(out)):
        # Overall offset in the original file = (start_offset + i)
        out[i] ^= key[(start_offset + i) % key_len]
    return bytes(out)

def is_ascii_printable(c: int) -> bool:
    # We'll treat roughly 32..126 plus CR, LF, tab as 'printable' in context
    return 32 <= c <= 126 or c in (9, 10, 13)

def bytes_to_preview_str(b: bytes, max_len=256) -> str:
    """
    Convert a bytes chunk to a 'printable' ASCII snippet, replacing non-printable with '.'
    and limiting to max_len for brevity.
    """
    s = []
    for c in b[:max_len]:
        if is_ascii_printable(c):
            s.append(chr(c))
        else:
            s.append(".")
    return "".join(s)

def main():
    for fw_path in FIRMWARE_PATHS:
        if not os.path.exists(fw_path):
            print(f"SKIP: File not found {fw_path}")
            continue

        print("=" * 80)
        print(f"Analyzing: {fw_path}")
        with open(fw_path, "rb") as f:
            firmware = f.read()
        fw_len = len(firmware)
        print(f"File size: {fw_len} bytes\n")

        found_any = False

        # We'll do a sliding check across entire firmware
        max_check = fw_len - 1
        # We'll define the lengths we want to test: 7 bytes for KEY_PART_1, 16 for KEY_PART_2
        check_lengths = [(KEY_PART_1, len(KEY_PART_1)), (KEY_PART_2, len(KEY_PART_2))]

        for offset in range(max_check):
            # For each known key part...
            for (keypart, keypart_len) in check_lengths:
                if offset + keypart_len > fw_len:
                    # Can't read beyond end of file
                    continue

                # We'll XOR-decode exactly that many bytes
                chunk = firmware[offset: offset + keypart_len]
                decoded = xor_decode(chunk, offset, KEY_MASTER)

                if decoded == keypart:
                    # We found a match: "8710_2M" or "HHRRQbyemofrtytf"
                    found_any = True
                    print(f"\n[!] Potential block start at offset 0x{offset:08X}")
                    print(f"    Decodes to keypart: {keypart!r}")

                    # Let's XOR a bigger chunk (~4 KB) for inspection
                    decode_end = min(offset + DECODE_CHUNK_SIZE, fw_len)
                    big_slice = firmware[offset: decode_end]
                    big_decoded = xor_decode(big_slice, offset, KEY_MASTER)

                    # Print a short hex preview
                    hex_preview = big_decoded[:64].hex()
                    print(f"    Decoded chunk (first 64 bytes, hex): {hex_preview}")

                    # Print an ASCII preview
                    ascii_preview = bytes_to_preview_str(big_decoded, ASCII_CONTEXT)
                    print(f"    ASCII preview:\n{ascii_preview}\n")

        if not found_any:
            print("No offsets found where XOR-decoding yields '8710_2M' or 'HHRRQbyemofrtytf'.")

        print("-" * 80 + "\n")

if __name__ == "__main__":
    main()
