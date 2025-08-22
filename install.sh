echo Updating the server
sudo apt-get update

echo Installing tor
sudo apt install -y apt-transport-https curl gnupg lsb-release -y
DISTRO=$(lsb_release -cs)
sudo tee /etc/apt/sources.list.d/tor.list > /dev/null <<EOF
deb     [signed-by=/usr/share/keyrings/deb.torproject.org-keyring.gpg] https://deb.torproject.org/torproject.org $DISTRO main
deb-src [signed-by=/usr/share/keyrings/deb.torproject.org-keyring.gpg] https://deb.torproject.org/torproject.org $DISTRO main
EOF
curl -fsSL https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | sudo gpg --dearmor | sudo tee /usr/share/keyrings/deb.torproject.org-keyring.gpg >/dev/null
sudo apt update
sudo apt install tor deb.torproject.org-keyring -y

echo Installing pip
sudo apt install python3-pip -y

echo Installing virtual environment 
sudo apt-get install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate

echo Install all packages
pip3 install -r requirements.txt

echo Install browser chromium headless mode
playwright install --only-shell chromium

echo Installing playwright chromium dependencies
playwright install-deps chromium

echo "Installing Node.js (for PM2)..."
# Use NodeSource to get latest stable Node.js
sudo apt install nodejs npm -y

echo "Installing PM2 globally..."
sudo npm install -g pm2