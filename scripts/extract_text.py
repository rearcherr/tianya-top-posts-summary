import os, sys, json, re, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\extract"
OUT = r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\text"
os.makedirs(OUT, exist_ok=True)

MAX_PAGES = 60   # per-file page cap; posts are long, we take the core
MAX_CHARS = 90000

def extract_pdf(path):
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(path) as pdf:
            n = len(pdf.pages)
            step = 1
            if n > MAX_PAGES:
                step = max(1, n // MAX_PAGES)
            for i in range(0, n, step):
                try:
                    t = pdf.pages[i].extract_text() or ""
                except Exception:
                    t = ""
                if t.strip():
                    parts.append(f"\n[[page {i+1}/{n}]]\n" + t)
                if sum(len(p) for p in parts) > MAX_CHARS:
                    break
        txt = "\n".join(parts)
        return txt, n, None
    except Exception as e:
        # fallback to pypdf
        try:
            from pypdf import PdfReader
            r = PdfReader(path)
            n = len(r.pages)
            parts = []
            for i in range(min(n, MAX_PAGES)):
                try:
                    parts.append(r.pages[i].extract_text() or "")
                except Exception:
                    pass
            return "\n".join(parts), n, None
        except Exception as e2:
            return "", 0, f"{e} | {e2}"

def handle(fp):
    name = os.path.basename(fp)
    base, ext = os.path.splitext(name)
    ext = ext.lower()
    dest = os.path.join(OUT, base + ".txt")
    if os.path.exists(dest) and os.path.getsize(dest) > 500:
        return (base, "cached", 0)
    try:
        if ext == ".pdf":
            txt, pages, err = extract_pdf(fp)
        elif ext in (".txt", ".md"):
            txt, pages, err = open(fp, "r", encoding="utf-8", errors="ignore").read(), 0, None
        elif ext in (".doc", ".docx"):
            try:
                import docx
                d = docx.Document(fp)
                txt = "\n".join(p.text for p in d.paragraphs)
            except Exception:
                raw = open(fp, "rb").read()
                try:
                    txt = raw.decode("utf-16-le", errors="ignore")
                except Exception:
                    txt = raw.decode("gbk", errors="ignore")
            pages, err = 0, None
        elif ext in (".html", ".htm"):
            txt = open(fp, "r", encoding="utf-8", errors="ignore").read()
            txt = re.sub(r"<[^>]+>", " ", txt)
            pages, err = 0, None
        else:
            return (base, "skip:" + ext, 0)
        txt = re.sub(r"\n{4,}", "\n\n\n", txt)
        if len(txt.strip()) < 50:
            return (base, "empty", 0)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(txt)
        return (base, "ok", len(txt))
    except Exception as e:
        return (base, "err:" + str(e)[:80], 0)

if __name__ == "__main__":
    files = []
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            files.append(os.path.join(dp, f))
    print("files found:", len(files))
    stats = {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(handle, f) for f in files]
        for i, fu in enumerate(as_completed(futs), 1):
            base, status, ln = fu.result()
            key = status.split(":")[0]
            stats[key] = stats.get(key, 0) + 1
            if i % 20 == 0:
                print(i, "/", len(files), stats, flush=True)
    print("DONE", stats)
    print("txt files:", len(os.listdir(OUT)))
