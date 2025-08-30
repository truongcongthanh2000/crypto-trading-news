module.exports = {
  apps: [
    {
      name: "tor-multi",
      script: "bash",
      args: [
        "-c",
        `
        sudo rm -rf /tmp/*
        sudo rm -f /var/lib/tor/state
        TORRC=/tmp/torrc-multi
        rm -f $TORRC

        NUM_PORTS="\${NUM_PORTS:-1}"
        MAX_CIRCUIT="\${MAX_CIRCUIT:-600}"

        echo "[*] Generating torrc with $NUM_PORTS SocksPorts..."
        for ((i=0; i<$NUM_PORTS; i++)); do
          PORT=$((9050 + i))
          echo "SocksPort $PORT IsolateSOCKSAuth" >> $TORRC
        done

        echo "MaxCircuitDirtiness $MAX_CIRCUIT" >> $TORRC

        echo "[*] Starting Tor with custom config..."
        exec tor -f $TORRC
        `
      ],
      autorestart: true,
      restart_delay: 5000,
      out_file: "/tmp/tor.log",
      error_file: "/tmp/tor-error.log"
    },
    {
      name: "crypto-trading-news",
      script: ".venv/bin/python3",
      args: ["-m", "crypto_trading_news"],
      autorestart: true,
      restart_delay: 5000,
      out_file: "/tmp/crypto_trading_news.log",
      error_file: "/tmp/crypto_trading_news-error.log"
    }
  ]
};
