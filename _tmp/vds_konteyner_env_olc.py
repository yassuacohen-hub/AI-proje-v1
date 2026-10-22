import subprocess, json
# D-380: yalniz ad + DOLU/BOS yazar, deger basmaz
def ssh(cmd):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "huginn-vds", cmd], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    return r.stdout, r.stderr, r.returncode

out, err, rc = ssh("docker inspect hugin_admin")
print("inspect rc", rc, err[:200])
if rc == 0:
    d = json.loads(out)[0]
    env = dict(e.split("=", 1) for e in d["Config"]["Env"] if "=" in e)
    print("STARTED:", d["State"].get("StartedAt"), "| status:", d["State"].get("Status"))
    for k in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "BREVO_API_KEY", "MAILERLITE_API_KEY"]:
        print(" ", k, "DOLU" if env.get(k) else "YOK/BOS")
    print("compose:", d["Config"]["Labels"].get("com.docker.compose.project.working_dir"), d["Config"]["Labels"].get("com.docker.compose.project.config_files"))
    print("mounts:", [(m.get("Source"), m.get("Destination")) for m in d.get("Mounts", [])])
    print("restart policy:", d["HostConfig"]["RestartPolicy"])
