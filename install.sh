#install ollama
curl -fsSL https://ollama.com/install.sh | sh

#intall docker
sudo apt install -y docker.io
sudo systemctl enable docker --now
sudo usermod -aG docker $USER

#install sherlock
sudo apt install sherlock

#install dependencies
pip install -r requirements.txt