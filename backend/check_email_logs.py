import subprocess

result = subprocess.run(["docker", "logs", "--tail", "500", "crm_backend"], capture_output=True)
stdout_text = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
stderr_text = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
logs = stdout_text + stderr_text

filtered = []
for line in logs.splitlines():
    if any(word in line.lower() for word in ['email', 'erreur', 'smtp', 'échec', 'notify', 'karim', 'dpay']):
        filtered.append(line.strip())

with open("c:\\Users\\Lenovo\\Desktop\\crm\\backend\\email_logs.txt", "w", encoding='utf-8') as f:
    f.write("\n".join(filtered))
