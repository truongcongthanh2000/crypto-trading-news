echo Updating the server
sudo apt-get update

echo Installing pip
sudo apt install python3-pip -y

echo Installing virtual environment 
sudo apt-get install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate

echo Install all packages
pip3 install -r requirements.txt

echo Installing playwright chromium dependencies
playwright install-deps chromium