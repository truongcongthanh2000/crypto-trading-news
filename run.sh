#!/bin/bash

# Usage: ./run.sh [num_ports] [max_circuit_dirtiness]
# Example: ./run.sh 5 300  -> opens 9050..9054, circuit rotates every 300s
# Example: ./run.sh 3      -> opens 9050..9052, circuit rotates every 600s
# Example: ./run.sh        -> opens only 9050, circuit rotates every 600s

NUM_PORTS=${1:-1}
MAX_CIRCUIT=${2:-600}

echo "[*] Cleaning old processes..."

# Kill old tor instances started by this script
pkill -f "tor -f /tmp/torrc-multi" 2>/dev/null

# Kill old python crypto_trading_news instances
pkill -f "python3 -m crypto_trading_news" 2>/dev/null

# Stop system tor service if running
sudo systemctl stop tor 2>/dev/null

# Remove old tor state
sudo rm -f /var/lib/tor/state

echo "[*] Old processes cleaned."

# Temp torrc file
TORRC=/tmp/torrc-multi
rm -f $TORRC

echo "[*] Generating torrc with $NUM_PORTS SocksPorts..."
for ((i=0; i<$NUM_PORTS; i++)); do
    PORT=$((9050 + i))
    echo "SocksPort $PORT IsolateSOCKSAuth" >> $TORRC
done

# Optionally pin exit nodes
# echo "ExitNodes {sg}" >> $TORRC
# echo "StrictNodes 1" >> $TORRC
echo "MaxCircuitDirtiness $MAX_CIRCUIT" >> $TORRC

echo "[*] Starting Tor with custom config (MaxCircuitDirtiness=$MAX_CIRCUIT)..."
tor -f $TORRC > /tmp/tor.log 2>&1 &
TOR_PID=$!
echo "Tor started with PID $TOR_PID, log at /tmp/tor.log"

sleep 5  # give Tor some time to bootstrap

echo "[*] Starting Python module..."
source .venv/bin/activate
nohup python3 -m crypto_trading_news > /tmp/crypto_trading_news.log 2>&1 &
PY_PID=$!
echo "Python started with PID $PY_PID, log at /tmp/crypto_trading_news.log"

echo "[*] Setup complete."
