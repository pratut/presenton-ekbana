# Standard production (CPU)
docker compose up production --build

# Production with GPU support
docker compose up production-gpu --build

# Run in detached mode (background)
docker compose up production -d --build

# To stop
docker compose down