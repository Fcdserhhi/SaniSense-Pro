from machine import Pin, ADC, I2C
from vl53l0x import VL53L0X
import network
import socket
import time

ssid = "SmartRestroom"
password = "12345678"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)
print(ap.ifconfig())

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)
server.setblocking(False)   

green  = Pin(2,  Pin.OUT)
red    = Pin(4,  Pin.OUT)
yellow = Pin(5,  Pin.OUT)

sos_btn   = Pin(13, Pin.IN, Pin.PULL_UP)
clean_btn = Pin(12, Pin.IN, Pin.PULL_UP)
maint_btn = Pin(14, Pin.IN, Pin.PULL_UP)

buzzer = Pin(18, Pin.OUT)

ir1      = Pin(26, Pin.IN)
ir2      = Pin(25, Pin.IN)
basin_ir = Pin(27, Pin.IN)
disp_ir  = Pin(33, Pin.IN)

mq = ADC(Pin(34))
mq.atten(ADC.ATTN_11DB)

water = ADC(Pin(35))
water.atten(ADC.ATTN_11DB)

WATER_MIN = 0      
WATER_MAX = 3200   

def water_percent(raw):
    pct = (raw - WATER_MIN) / (WATER_MAX - WATER_MIN) * 100
    return max(0, min(100, int(pct)))

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
tof = VL53L0X(i2c)

people_count       = 0
occupied           = False
basin_status       = "NOT USED"
odor_status        = "NORMAL"
stock_status       = "AVAILABLE"
cleaning_status    = "NORMAL"
maintenance_status = "NORMAL"
hygiene_score      = 100
hygiene_state      = "GOOD"
cleaning_required  = False

last_entry   = 0
last_exit    = 0
last_sensors = 0
distance     = 999
odor         = 0
water_raw    = 0

last_sos   = 0
last_clean = 0
last_maint = 0

def beep():
    buzzer.on()
    time.sleep_ms(80)
    buzzer.off()

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def build_html(people_count, occupied, distance, odor, odor_status,
               water_raw, hygiene_score, hygiene_state, basin_status,
               stock_status, cleaning_status, maintenance_status,
               cleaning_required):

    w_pct        = water_percent(water_raw)
    occupied_txt = "OCCUPIED" if occupied else "VACANT"
    occ_cls      = "danger" if occupied else "ok"
    ppl_cls      = "danger" if people_count >= 8 else ("warn" if people_count >= 5 else "ok")
    odor_cls     = "danger" if odor_status == "CRITICAL" else ("warn" if odor_status == "HIGH" else "ok")
    water_cls    = "danger" if w_pct > 80 else ("warn" if w_pct > 30 else "ok")
    water_lbl    = "HIGH" if w_pct > 80 else ("MEDIUM" if w_pct > 30 else "LOW")
    stock_cls    = "danger" if stock_status == "LOW" else "ok"
    stock_val    = "LOW" if stock_status == "LOW" else "OK"
    basin_cls    = "warn" if basin_status == "USED" else ""
    hyg_cls      = "danger" if hygiene_score < 50 else ("warn" if hygiene_score < 80 else "ok")
    hyg_color    = "#ff3b5c" if hygiene_score < 50 else ("#ffb800" if hygiene_score < 80 else "#00ff9d")
    w_color      = "#ff3b5c" if w_pct > 80 else ("#ffb800" if w_pct > 30 else "#00ff9d")
    clean_cls    = "warn" if cleaning_status in ("CLEANING ACTIVE", "FAILED") else ("ok" if cleaning_status == "VERIFIED" else "")
    clean_val    = "ACTIVE" if cleaning_status == "CLEANING ACTIVE" else ("OK" if cleaning_status == "VERIFIED" else ("FAIL" if cleaning_status == "FAILED" else "--"))
    maint_cls    = "danger" if maintenance_status == "SOS ALERT" else ("warn" if maintenance_status == "MAINTENANCE REQUIRED" else "ok")
    sos_cls      = "" if maintenance_status == "SOS ALERT" else "hidden"
    clean_req    = "CLEANING REQUIRED" if cleaning_required else "All clear"

    h = (
        "<!DOCTYPE html><html><head>"
        "<meta charset=UTF-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1.0'>"
        "<title>Smart Restroom</title>"
        "<style>"
        ":root{--bg:#050c1a;--panel:#0a1628;--border:#0e2a4a;--accent:#00d4ff;--accent2:#00ff9d;--warn:#ffb800;--danger:#ff3b5c;--text:#cde8ff;--muted:#3a6080;}"
        "*{margin:0;padding:0;box-sizing:border-box;}"
        "body{background:var(--bg);color:var(--text);font-family:monospace;padding:12px;}"
        "header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid var(--border);}"
        "h1{font-size:13px;font-weight:bold;letter-spacing:3px;color:var(--accent);}"
        ".sub{font-size:9px;color:var(--muted);letter-spacing:2px;margin-top:2px;}"
        ".live{display:flex;align-items:center;gap:5px;font-size:10px;color:var(--accent2);}"
        ".dot{width:7px;height:7px;background:var(--accent2);border-radius:50%;animation:p 1.4s ease-in-out infinite;}"
        "@keyframes p{0%,100%{opacity:1}50%{opacity:0.2}}"
        ".grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}"
        ".card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px;}"
        ".card.warn{border-color:rgba(255,184,0,0.5);}"
        ".card.danger{border-color:rgba(255,59,92,0.6);}"
        ".card.ok{border-color:rgba(0,255,157,0.35);}"
        ".lbl{font-size:8px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}"
        ".val{font-size:22px;color:var(--accent);line-height:1;}"
        ".card.warn .val{color:var(--warn);}.card.danger .val{color:var(--danger);}.card.ok .val{color:var(--accent2);}"
        ".sm{font-size:8px;letter-spacing:1px;text-transform:uppercase;margin-top:4px;color:var(--muted);}"
        ".wide{grid-column:span 2;}.big .val{font-size:42px;}"
        ".bar-wrap{margin-top:6px;height:4px;background:var(--border);border-radius:2px;overflow:hidden;}"
        ".bar{height:100%;border-radius:2px;}"
        ".sec{grid-column:1/-1;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);padding:5px 0 2px;border-top:1px solid var(--border);margin-top:2px;}"
        ".alert{grid-column:1/-1;background:rgba(255,59,92,0.12);border:1px solid rgba(255,59,92,0.5);border-radius:8px;padding:9px 12px;font-size:11px;color:var(--danger);letter-spacing:1px;animation:ab 1s ease-in-out infinite;}"
        "@keyframes ab{0%,100%{opacity:1}50%{opacity:0.4}}"
        ".hidden{display:none;}"
        "footer{margin-top:14px;text-align:center;font-size:9px;color:var(--muted);letter-spacing:2px;}"
        "</style></head><body>"
        "<header><div><h1>SMART RESTROOM</h1><div class=sub>IOT MONITOR - ESP32</div></div>"
        "<div class=live><div class=dot></div>LIVE</div></header>"
        "<div class=grid>"
        "<div class='alert " + sos_cls + "'>! SOS ALERT -- IMMEDIATE ASSISTANCE REQUIRED</div>"
        "<div class=sec>OCCUPANCY</div>"
        "<div class='card big " + ppl_cls + "'><div class=lbl>People Inside</div>"
        "<div class=val>" + str(people_count) + "</div><div class=sm>in restroom</div></div>"
        "<div class='card " + occ_cls + "'><div class=lbl>Stall</div>"
        "<div class=val style='font-size:15px'>" + occupied_txt + "</div>"
        "<div class=sm>" + str(distance) + " mm</div></div>"
        "<div class='card " + basin_cls + "'><div class=lbl>Basin</div>"
        "<div class=val style='font-size:15px'>" + basin_status + "</div></div>"
        "<div class=sec>ENVIRONMENT</div>"
        "<div class='card " + odor_cls + "'><div class=lbl>Air / Odor</div>"
        "<div class=val>" + str(odor) + "</div><div class=sm>" + odor_status + "</div></div>"
        "<div class='card " + water_cls + "'><div class=lbl>Water Level</div>"
        "<div class=val>" + str(w_pct) + "%</div><div class=sm>" + water_lbl + "</div>"
        "<div class=bar-wrap><div class=bar style='width:" + str(w_pct) + "%;background:" + w_color + "'></div></div></div>"
        "<div class='card " + stock_cls + "'><div class=lbl>Dispenser</div>"
        "<div class=val style='font-size:15px'>" + stock_val + "</div>"
        "<div class=sm>" + stock_status + "</div></div>"
        "<div class=sec>HYGIENE &amp; MAINTENANCE</div>"
        "<div class='card wide " + hyg_cls + "'><div class=lbl>Hygiene Score</div>"
        "<div class=val>" + str(int(hygiene_score)) + "%</div>"
        "<div class=sm>" + hygiene_state + " -- " + clean_req + "</div>"
        "<div class=bar-wrap><div class=bar style='width:" + str(int(hygiene_score)) + "%;background:" + hyg_color + "'></div></div></div>"
        "<div class='card " + clean_cls + "'><div class=lbl>Cleaning</div>"
        "<div class=val style='font-size:15px'>" + clean_val + "</div>"
        "<div class=sm>" + cleaning_status + "</div></div>"
        "<div class='card wide " + maint_cls + "'><div class=lbl>Maintenance</div>"
        "<div class=val style='font-size:14px'>" + maintenance_status + "</div></div>"
        "</div>"
        "<footer>AUTO-REFRESH 3s - 192.168.4.1 - v1.2</footer>"
        "<script>setTimeout(function(){location.reload();},3000);</script>"
        "</body></html>"
    )
    return h

green.on()
beep()
print("SMART RESTROOM STARTED")

while True:

    now = time.ticks_ms()

    if time.ticks_diff(now, last_sensors) >= 300:
        last_sensors = now
        odor      = mq.read()
        water_raw = water.read()
        try:
            d = tof.read()
            distance = d if d is not None else 999
        except:
            distance = 999

    if ir1.value() == 0:
        t = time.ticks_ms()
        deadline = time.ticks_add(t, 1000)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if ir2.value() == 0:
                if time.ticks_diff(now, last_entry) > 2000:
                    people_count += 1
                    last_entry = now
                    beep()
                    print("ENTRY:", people_count)
                break

    if ir2.value() == 0:
        t = time.ticks_ms()
        deadline = time.ticks_add(t, 1000)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            if ir1.value() == 0:
                if time.ticks_diff(now, last_exit) > 2000:
                    if people_count > 0:
                        people_count -= 1
                    last_exit = now
                    beep()
                    print("EXIT:", people_count)
                break

    if distance < 120:
        occupied = True
        green.off(); red.on()
    else:
        occupied = False
        red.off(); green.on()

   
    basin_status = "USED"      if basin_ir.value() == 0 else "NOT USED"
    stock_status = "AVAILABLE" if disp_ir.value()  == 0 else "LOW"

    if odor > 450:
        odor_status = "CRITICAL"
        hygiene_score -= 0.1
    elif odor > 350:
        odor_status = "HIGH"
    else:
        odor_status = "NORMAL"

    if people_count >= 8 or odor > 450 or hygiene_score < 70:
        cleaning_required = True
        yellow.on()
    else:
        cleaning_required = False
        if not occupied:
            yellow.off()

    if clean_btn.value() == 0 and time.ticks_diff(now, last_clean) > 3000:
        last_clean = now
        cleaning_status = "CLEANING ACTIVE"
        beep(); yellow.on()
        print("CLEANING STARTED")
        w_before = water.read()
        time.sleep_ms(3000)
        w_after = water.read()
        if abs(w_after - w_before) > 10:
            cleaning_status   = "VERIFIED"
            hygiene_score     = 100
            cleaning_required = False
        else:
            cleaning_status = "FAILED"
        beep()

    if sos_btn.value() == 0 and time.ticks_diff(now, last_sos) > 3000:
        last_sos = now
        maintenance_status = "SOS ALERT"
        beep(); red.on()
        print("SOS ALERT")

    if maint_btn.value() == 0 and time.ticks_diff(now, last_maint) > 3000:
        last_maint = now
        maintenance_status = "MAINTENANCE REQUIRED"
        beep()
        print("MAINTENANCE")
    hygiene_score = clamp(hygiene_score, 0, 100)

    if hygiene_score >= 80:
        hygiene_state = "GOOD"
    elif hygiene_score >= 50:
        hygiene_state = "MODERATE"
    else:
        hygiene_state = "CRITICAL"

    client = None
    try:
        client, _ = server.accept()
        client.settimeout(2.0)

        try:
            client.recv(1024)         
        except:
            pass

        page = build_html(
            people_count, occupied, distance, odor, odor_status,
            water_raw, hygiene_score, hygiene_state, basin_status,
            stock_status, cleaning_status, maintenance_status,
            cleaning_required
        )

        resp = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: " + str(len(page)) + "\r\n"
            "Connection: close\r\n\r\n"
            + page
        )
        client.sendall(resp)

    except OSError:
        pass    

    finally:
        if client:
            try:
                client.close()
            except:
                pass

    time.sleep_ms(20)
