# Production code

```bash
cd /home/ek-lap-47/Ekbana/presenton-ekbana
docker stop presenton-container
docker rm presenton-container
docker compose build production
docker compose up -d production
```

# Dev mode

```bash
cd /home/ek-lap-47/Ekbana/presenton-ekbana
docker compose build development
docker compose up -d development
```

Open:
`http://localhost:5000`

# Sanity check

```bash
docker compose ps
docker logs -f $(docker compose ps -q production)
```

# Stop compose

From project root:

```bash
docker compose stop production development
```

Remove them too: 

```bash
docker compose down
```

# Run minial compose

Production only: 

```bash
docker compose up -d production
```

Development only: 

```bash
docker compose up -d development
```

