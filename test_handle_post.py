import json
import urllib.request

url = "https://odoox.recognate.in/api/debug"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res, open("out_debug.json", "w") as f:
        f.write(
            json.dumps(
                {"status": res.status, "body": json.loads(res.read().decode("utf-8"))},
                indent=2,
            )
        )
except urllib.error.HTTPError as e:
    with open("out_debug.json", "w") as f:
        f.write(f"ERROR: {e.code}")
except Exception as e:
    with open("out_debug.json", "w") as f:
        f.write(f"ERROR: {e!s}")
