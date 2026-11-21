import sys
import json
import os
import re
import sqlite3
import time
import uuid
import hashlib
import toastfit

def clean(value):
    return "".join(c if c.isprintable() else "?" for c in str(value))

def print_online(result):
    players = result.get("players", [])
    print(f"Online: {result.get('online', len(players))}")
    for p in players:
        print()
        print(f"{clean(p.get('username'))}  {clean(p.get('duration'))}  (since {clean(p.get('connected_at'))})  ip:  {clean(p.get('ip'))}")
        uuids = [f"canonical={clean(p.get('canonical_uuid'))}"] + [re.sub(r"^\((session|world)_uuid=", r"(\1=", clean(a)) for a in re.findall(r"\([^()]*\)", str(p.get("aliases") or ""))]
        print(f"  {'uuids':<9}{'  '.join(uuids)}")
        print(f"  {'version':<9}{clean(p.get('version'))}")
        info = [f"auth={clean(p.get('auth'))}"]
        if p.get("reason"):
            info.append(f"reason={clean(p.get('reason'))}")
        if p.get("registered"):
            info.append(f"registered={clean(p.get('registered'))}")
        info.append(f"avatar={clean(p.get('avatar'))}")
        print(f"  {'info':<9}{'  '.join(info)}")

UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')

def resolve_target(value):
    if UUID_RE.match(value):
        return value.lower()
    digest = hashlib.md5(f"OfflinePlayer:{value}".encode("utf-8")).digest()
    return str(uuid.UUID(bytes=digest, version=3))

def open_db():
    if not os.path.exists("data/users.db"):
        return None
    return sqlite3.connect("data/users.db")

def main():
    if len(sys.argv) < 2:
        print("Usage: python admin.py <command> [args]")
        print("Commands: online <id>, delete <uuid>, ban <uuid>, chat <msg>, toast <type> <title> <desc>")
        return
    cmd = sys.argv[1]
    token = open("data/.admin_session").read().strip()
    if cmd == "online":
        rid = hashlib.md5(str(time.time()).encode()).hexdigest()
        cmd_file = f"data/.admin_command_{rid}.json"
        with open(cmd_file, "w") as f:
            json.dump({"token": token, "type": "online", "id": rid}, f)
        # Wait for result
        for _ in range(10):
            time.sleep(0.1)
            result_file = f"data/.admin_result_{rid}.json"
            if os.path.exists(result_file):
                with open(result_file) as f:
                    result = json.load(f)
                print_online(result)
                os.remove(result_file)
                return
        print("No response from backend")
    elif cmd in ("delete", "ban"):
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        rid = hashlib.md5(str(time.time()).encode()).hexdigest()
        cmd_file = f"data/.admin_command_{rid}.json"
        with open(cmd_file, "w") as f:
            json.dump({"token": token, "type": f"{cmd}_account", "uuid": target}, f)
        print(f"{cmd} command sent for {target}")
    elif cmd == "chat":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        rid = hashlib.md5(str(time.time()).encode()).hexdigest()
        cmd_file = f"data/.admin_command_{rid}.json"
        with open(cmd_file, "w") as f:
            json.dump({"token": token, "type": "chat", "message": msg}, f)
        print("Chat broadcast sent")
    elif cmd == "toast":
        t_type = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        title = sys.argv[3] if len(sys.argv) > 3 else ""
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        rid = hashlib.md5(str(time.time()).encode()).hexdigest()
        cmd_file = f"data/.admin_command_{rid}.json"
        with open(cmd_file, "w") as f:
            json.dump({"token": token, "type": "toast", "toast_type": t_type, "title": title, "desc": desc}, f)
        print("Toast broadcast sent")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
