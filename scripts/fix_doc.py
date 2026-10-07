"""Extract text from a Word 97-2003 (.doc) binary file by parsing the
FIB -> piece table (CLX) -> text stream. Handles compressed (cp1252-ish)
and uncompressed (UTF-16LE) piece encodings, plus ANSI/UTF-8 codepage text.
"""
import sys, struct, olefile

def extract_doc_text(path):
    ole = olefile.OleFileIO(path)
    doc = ole.openstream("WordDocument").read()
    # FIB
    wIdent, nFib = struct.unpack_from("<HH", doc, 0)
    flags = struct.unpack_from("<H", doc, 10)[0]
    fWhichTblStm = (flags >> 9) & 1
    table_name = "1Table" if fWhichTblStm else "0Table"
    if not ole.exists(table_name):
        table_name = "0Table" if ole.exists("0Table") else "1Table"
    tbl = ole.openstream(table_name).read()

    # fcClx / lcbClx at fibRgFcLcb offset; for nFib>=193 it's fcClx at 0x01A2
    if nFib >= 193:
        fcClx, lcbClx = struct.unpack_from("<II", doc, 0x01A2)
    else:
        # older: locate via fibRgFcLcb blob
        raise RuntimeError("old nFib %d" % nFib)

    clx = tbl[fcClx:fcClx + lcbClx]
    # parse Clx: sequence of Prc (0x01) then Pcdt (0x02)
    i = 0
    pcdt = None
    while i < len(clx):
        t = clx[i]
        if t == 1:  # Prc
            cb = struct.unpack_from("<H", clx, i + 1)[0]
            i += 3 + cb
        elif t == 2:  # Pcdt
            lcb = struct.unpack_from("<I", clx, i + 1)[0]
            pcdt = clx[i + 5:i + 5 + lcb]
            break
        else:
            break
    if pcdt is None:
        raise RuntimeError("no piece table")

    # PlcPcd: n pieces; CP array (n+1) of 4-byte, then n PCDs of 8 bytes
    n = (len(pcdt) - 4) // 12
    cps = [struct.unpack_from("<I", pcdt, k * 4)[0] for k in range(n + 1)]
    out = []
    for k in range(n):
        off = 4 * (n + 1) + k * 8
        fc_raw = struct.unpack_from("<I", pcdt, off + 2)[0]
        compressed = (fc_raw & 0x40000000) != 0
        fc = fc_raw & 0x3FFFFFFF
        cch = cps[k + 1] - cps[k]
        if compressed:
            raw = doc[fc // 2: fc // 2 + cch]
            out.append(raw.decode("cp1252", errors="replace"))
        else:
            raw = doc[fc: fc + cch * 2]
            out.append(raw.decode("utf-16-le", errors="replace"))
    ole.close()
    return "".join(out)

if __name__ == "__main__":
    src = r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\extract\缠中说禅\一代目前辈分享（自己独立思考吧）.doc"
    dst = r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\text\一代目前辈分享（自己独立思考吧）.txt"
    t = extract_doc_text(src)
    # strip control chars
    import re
    t = t.replace("\r\n", "\n").replace("\x07", "\n").replace("\x0c", "\n")
    t = "".join(ch for ch in t if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    t = re.sub(r"\n{3,}", "\n\n", t)
    open(dst, "w", encoding="utf-8").write(t)
    cjk = sum(1 for c in t if "\u4e00" <= c <= "\u9fff")
    print("chars", len(t), "cjk", cjk)
    print("--- sample 1200 ---")
    print(t[3000:4600])
