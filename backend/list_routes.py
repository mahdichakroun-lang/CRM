from app.main import create_app

app = create_app()
with open("/tmp/routes.txt", "w") as f:
    for r in app.routes:
        path = getattr(r, 'path', '?')
        methods = getattr(r, 'methods', set())
        f.write(f"{','.join(methods) if methods else 'N/A':10s} {path}\n")

with open("/tmp/routes.txt") as f:
    print(f.read())
