#!/usr/bin/env bash
# Run this 2-3 minutes before you send the cold email.
# It hits the demo + API a few times so the free-tier hosts are hot
# when the recipient clicks the link. Idempotent. Safe to re-run.

set -e

DEMO="https://out-gwumfbso.devinapps.com/"
API="https://aol-api-enqcpqaq.fly.dev"

echo "Warming demo + API..."
for i in 1 2 3; do
  curl -fsSL --max-time 15 "$DEMO" -o /dev/null && echo "  demo  attempt $i: ok"
  curl -fsSL --max-time 15 "$API/" -o /dev/null && echo "  api   attempt $i: ok"
  curl -fsSL --max-time 15 "$API/api/features" -o /dev/null && echo "  feat  attempt $i: ok"
  curl -fsSL --max-time 15 "$API/api/analytics" -o /dev/null && echo "  stats attempt $i: ok"
  sleep 1
done

echo ""
echo "Warm. Send the email now."
