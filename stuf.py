import struct
import re
import os
import shutil
import sys
import json

try:
    mode = sys.argv[1]
except:
    mode = "e"

with open('sfx_gta3pc.lst', 'r') as f:
    names = re.findall(r"^[^-|;].*$", f.read(), re.MULTILINE)

if mode == 'w':
    if os.path.exists("sfx.SDT"):
        shutil.move("sfx.SDT", "sfx_backup.SDT")
    if os.path.exists("SFX.RAW"):
        shutil.move("SFX.RAW", "SFX_BACKUP.RAW")

    sfx = open("SFX.RAW", 'ab')
    sdt = open("sfx.SDT", 'ab')
    with open('loop_info.json', 'r') as f:
        loop_info = json.loads(f.read())
    
    for name in names:
        filename = f"output/{name}"
        if os.path.exists(filename):
            with open(filename, 'rb') as sound:
                print(name)

                quickbit = struct.unpack("4si4s4sihhiihh4si", sound.read(44))
                data = sound.read()

                offset = sfx.tell()
                size = quickbit[12]
                rate = quickbit[7]
                loop_start = loop_info[name]["loop_start"]
                loop_end = loop_info[name]["loop_end"]

                quickbit = struct.pack("iiiii", offset, int(size), rate, loop_start, loop_end)
                sdt.write(quickbit)
                sfx.write(data)


    exit()
if mode == 'e':
    current = 0
    sfx = open('sfx.RAW', 'rb')
    sdt = open('sfx.SDT', 'rb')
    loop_info = {}

    for name in names:
        if name != "quit":
            filename = f"output/{name}"
            data = sdt.read(4*5)
            if data:
                s = struct.unpack("iiiii", data)
                offset = s[0]
                size = s[1]
                rate = s[2]
                loop_start = s[3]
                loop_end = s[4]
                filename = f"output/{name}"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                sfx.seek(offset)
                audio = sfx.read(size)
                with open(filename, 'wb') as output:
                    quickbit = struct.pack("4si4s4sihhiihh4si", b"RIFF", size+36, b"WAVE", b"fmt ", 16, 1, 1, rate, rate*2, 2, 16, b"data", size)
                    output.write(quickbit+audio)
                    loop_info[name] = {}
                    loop_info[name]["loop_start"] = loop_start
                    loop_info[name]["loop_end"] = loop_end
                    print(filename)
    with open('loop_info.json', 'w') as f:
        f.write(json.dumps(loop_info))

    # done
    exit()

print("unknown mode selected")