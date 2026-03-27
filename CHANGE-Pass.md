```bash
cd /mnt/nfs/2026/projects/presenton-ekbana/servers/fastapi

python3 - <<'PY'
from utils.auth_backend import _hash_password
print(_hash_password("StrongPassword@123"))
PY
```

Paste this in admin file;
```bash
cd /mnt/nfs/2026/projects/presenton-ekbana
docker compose restart production
```

if not editable: 
```bash
ls -l app_data/admin_auth.json
```
#### make your user owner (or whole app_data dir)
```bash
sudo chown -R "$USER":"$USER" app_data
```
#### ensure writable
```bash
chmod 600 app_data/admin_auth.json
```