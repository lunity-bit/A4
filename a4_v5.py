# A4 Kernel v1.6 - productive+light: superloop, lazy imports, cached wifi. Save as main.py
import sys, os, time, machine, gc
V = "A4 Kernel v1.6"
L = "EN"
def T(en, tr): return tr if L == "TR" else en
def cls():
    print("\n" * 2 + "=" * 28)
def hdr(t):
    cls()
    t = str(t)[:20]
    pad = " " * (20 - len(t)) if len(t) < 20 else ""
    print("| A4 " + t + pad + " |")
    print("=" * 28)
def inp(p="> "):
    try: return input(p).strip()
    except: return ""
def wait():
    try: input(T("-- Enter --", "-- Gir --"))
    except: time.sleep(1)
def cpu():
    print(T("CPU TEST...", "CPU TESTI..."))
    a = time.ticks_ms()
    x = 0
    for i in range(20000): x += (i*123) % 97
    d = time.ticks_diff(time.ticks_ms(), a)
    print("%dMHz 20k:%dms" % (machine.freq()//1000000, d))
    print("RESULT:" + (T("SUCCESS", "BASARILI") if d < 5000 and x else T("FAILED", "BASARISIZ")))
    wait()
def info():
    gc.collect()
    try: m = os.uname()[0]
    except: m = sys.platform
    try:
        v = os.statvfs("/")
        dk = "%dKB" % (v[0]*v[3]//1024)
    except: dk = "n/a"
    print(V, m, "%dMHz" % (machine.freq()//1000000), "%dKB" % (gc.mem_free()//1024), dk, L)
    wait()
def wifi():
    try: import network
    except:
        print(T("FAILED", "BASARISIZ"), "no net")
        wait()
        return
    global W
    try:
        if 'W' not in globals() or W is None:
            W = network.WLAN(network.STA_IF)
            W.active(True)
    except Exception as e:
        print(str(e)[:60])
        wait()
        return
    while 1:
        c = W.isconnected()
        print("--- WiFi %s ---" % (W.ifconfig()[0] if c else "DOWN"))
        print(T("1.Connect", "1.Baglan"), T("2.Cut", "2.Kes"), T("0.Back", "0.Geri"))
        k = inp()
        if k == "0" or not k: return
        if k == "1":
            print(T("Scanning...", "Taraniyor..."))
            try:
                nets = W.scan()
            except Exception as e:
                print(str(e)[:60])
                wait()
                continue
            if not nets:
                print(T("No WiFi found", "WiFi bulunamadi"))
                wait()
                continue
            seen = []
            for r in nets:
                ss = r[0].decode() if isinstance(r[0], bytes) else str(r[0])
                rssi = r[3]
                if ss and ss not in [x[0] for x in seen]:
                    seen.append((ss, rssi))
                if len(seen) >= 10: break
            for i, (ss, rs) in enumerate(seen):
                print("%d.%s (%ddBm)" % (i+1, ss, rs))
            print(T("0.Back", "0.Geri"))
            q = inp("no> ")
            if q == "0" or not q: continue
            try: idx = int(q)-1
            except: continue
            if idx < 0 or idx >= len(seen): continue
            ss = seen[idx][0]
            print("SSID:" + ss)
            p = inp("PASS: ")
            try:
                W.connect(ss, p)
                for _ in range(20):
                    if W.isconnected(): break
                    time.sleep(1)
                print((T("SUCCESS ", "BASARILI ") if W.isconnected() else T("FAILED", "BASARISIZ")) + (W.ifconfig()[0] if W.isconnected() else ""))
            except Exception as e: print(str(e)[:60])
            wait()
        elif k == "2":
            try: W.disconnect()
            except: pass
def sysapp():
    global L
    while 1:
        hdr(T("System", "Sistem"))
        print("  " + T("1.Info", "1.Bilgi"))
        print("  " + T("2.CPU Test", "2.CPU Testi"))
        print("  3.Dil [%s]" % L)
        print("  " + T("4.WiFi Connect", "4.WiFi Baglan"))
        print("  " + T("0.Back", "0.Geri"))
        print("-" * 28)
        k = inp()
        if k == "1": info()
        elif k == "2": cpu()
        elif k == "3":
            L = "TR" if L == "EN" else "EN"
            print(L)
        elif k == "4": wifi()
        elif k == "0" or not k: return
def write():
    d = "A4KERNEL_OK1234"
    try:
        open("_a4.tmp", "w").write(d)
        ok = open("_a4.tmp").read() == d
        try: os.remove("_a4.tmp")
        except: pass
        print("RESULT:" + (T("SUCCESS", "BASARILI") if ok else T("FAILED", "BASARISIZ")))
    except Exception as e: print(str(e)[:40])
    wait()
def qurl(s):
    # minimal urlencode for AI prompt (no urllib on Pico)
    r = ""
    for ch in s[:200]:
        o = ord(ch)
        if (48 <= o <= 57) or (65 <= o <= 90) or (97 <= o <= 122) or ch in "-_.~":
            r += ch
        elif ch == " ": r += "%20"
        else:
            r += "%%%02X" % o
    return r
def ai_chat():
    hdr("AI")
    try:
        import network
        w = network.WLAN(network.STA_IF)
        if not w.isconnected():
            print(T("WiFi DOWN! System>WiFi first", "WiFi KAPALI! Sistem>WiFi"))
            wait()
            return
    except Exception as e:
        print(str(e)[:60])
        wait()
        return
    print(T("Light AI: text.pollinations.ai", "Hafif AI: text.pollinations.ai"))
    print(T("empty=back", "bos=geri"))
    while 1:
        gc.collect()
        q = inp("AI> ")
        if not q: return
        url = "http://text.pollinations.ai/" + qurl(q)
        print("...")
        try:
            import urequests as rq
            r = rq.get(url, timeout=20)
            try: t = r.text
            except: t = str(r.content[:1000])
            try: r.close()
            except: pass
            print("-" * 28)
            print(t[:800] if t else "(empty)")
            print("-" * 28)
        except Exception as e:
            # socket fallback for low-mem
            try:
                import socket
                host = "text.pollinations.ai"
                path = "/" + qurl(q)
                ai = socket.getaddrinfo(host, 80)[0][-1]
                s = socket.socket()
                s.settimeout(15)
                s.connect(ai)
                s.send(b"GET " + path.encode() + b" HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
                d = b""
                while len(d) < 1200:
                    try: c = s.recv(512)
                    except: break
                    if not c: break
                    d += c
                try: s.close()
                except: pass
                j = d.find(b"\r\n\r\n")
                print((d[j+4:] if j >= 0 else d)[:800].decode("utf-8", "ignore"))
            except Exception as e2:
                print("FAILED", str(e2)[:70])
        gc.collect()
def links():
    hdr("Links")
    # 1) wifi check first - #1 browser failure cause
    try:
        import network
        w = network.WLAN(network.STA_IF)
        if not w.isconnected():
            print(T("WiFi DOWN! Go System>WiFi first", "WiFi KAPALI! Once Sistem>WiFi"))
            wait()
            return
        print("IP:" + w.ifconfig()[0])
    except Exception as e:
        print(str(e)[:60])
    LK = ("neverssl.com", "example.com", "micropython.org/ks/test.html", "raspberrypi.com")
    for i, u in enumerate(LK): print("%d. http://%s" % (i+1, u))
    print("5. " + T("Custom URL (http only)", "Ozel URL (http)"))
    print("6. AI Chat (pollinations)")
    print(T("0.Back", "0.Geri"))
    q = inp("no> ")
    if q == "0" or not q: return
    if q == "6":
        ai_chat()
        return
    if q == "5":
        u = inp("host/path: ").strip().replace("http://", "").replace("https://", "")
        if not u: return
    else:
        try: i = int(q)-1
        except: return
        if i < 0 or i >= len(LK): return
        u = LK[i]
    # split host/path
    if "/" in u:
        host = u.split("/")[0]
        path = "/" + "/".join(u.split("/")[1:])
    else:
        host = u
        path = "/"
    print("GET http://" + host + path)
    # try urequests, fallback to raw socket (small, no TLS)
    body = None
    err = ""
    try:
        import urequests as rq
        r = rq.get("http://" + host + path, timeout=10)
        try: sc = r.status_code
        except: sc = "?"
        print("HTTP", sc)
        try: body = r.text
        except: body = str(r.content[:1500])
        try: r.close()
        except: pass
    except Exception as e:
        err = str(e)[:80]
        print("urequests fail:", err)
        print(T("trying socket...", "socket deneniyor..."))
        try:
            import socket
            ai = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.settimeout(10)
            s.connect(ai)
            s.send(b"GET " + path.encode() + b" HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            gc.collect()
            d = b""
            while len(d) < 1500:
                try:
                    c = s.recv(512)
                except: break
                if not c: break
                d += c
            try: s.close()
            except: pass
            # cut headers
            j = d.find(b"\r\n\r\n")
            body = (d[j+4:] if j >= 0 else d)[:1200].decode("utf-8", "ignore")
            print("HTTP raw %dB" % len(d))
            err = ""
        except Exception as e2:
            print("RESULT:" + T("FAILED", "BASARISIZ"), str(e2)[:80])
            print(T("Fix: System>WiFi reconnect, use http:// only, no https", "Cozum: Sistem>WiFi baglan, sadece http://, https yok"))
            wait()
            return
    if body:
        o = ""
        sk = False
        for ch in body[:2000]:
            if ch == "<": sk = True
            elif ch == ">": sk = False
            elif not sk and len(o) < 500: o += ch
        print("-" * 28)
        print(o.strip()[:500] if o.strip() else body[:300])
        print("-" * 28)
        print("RESULT:" + T("SUCCESS", "BASARILI"))
    else:
        print("RESULT:" + T("FAILED", "BASARISIZ"), err[:60])
    wait()
def ml():
    print("TinyML: temp+hum -> comfort")
    try:
        a = int(float(inp("temp C: ")))
        b = int(float(inp("hum %: ")))
    except:
        print("RESULT:" + T("FAILED", "BASARISIZ"))
        wait()
        return
    t = time.ticks_ms()
    s = (38*a - 25*b)//10 + 10 - 50
    dt = time.ticks_diff(time.ticks_ms(), t)
    print("%s %dms" % (T("COMFY" if s > 0 else "MUGGY", "RAHAT" if s > 0 else "BUNALTICI"), dt))
    print("RESULT:" + T("SUCCESS", "BASARILI"))
    wait()
print(V, gc.mem_free())
while 1:
    gc.collect()
    hdr(T("MENU", "MENU"))
    print("  " + T("1.System", "1.Sistem"))
    print("  " + T("2.Write Test", "2.Yazma Testi"))
    print("  " + T("3.Links Browser", "3.Linkler"))
    print("  4.TinyML Demo")
    print("  " + T("5.Reboot", "5.Yeniden Baslat"))
    print("-" * 28)
    k = inp(T("sec (1-5):", "sec (1-5):") if L == "TR" else "sel (1-5):")
    if k == "1": sysapp()
    elif k == "2": write()
    elif k == "3": links()
    elif k == "4": ml()
    elif k == "5":
        time.sleep(1)
        machine.reset()
