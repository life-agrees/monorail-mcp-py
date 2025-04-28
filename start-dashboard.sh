#!/usr/bin/env sh
# Railway will inject PORT=12345 (or similar) into the env.
echo "⏳ Starting Streamlit on port $PORT…"
exec streamlit run \
  --server.address 0.0.0.0 \
  --server.port "$PORT" \
  dashboard.py
