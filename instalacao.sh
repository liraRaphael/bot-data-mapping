# instala o selenium e requests
echo 'instalando pacotes...'


pip3 install selenium
pip3 install requests
pip3 install jsonschema2popo2
pip3 install unidecode

echo 'Pacotes instalados...'

# faz a copia dos drivers
sudo cp geckodriver /usr/local/bin
sudo cp chromedriver /usr/local/bin
echo 'Drivers copiado...'

export PATH=$PATH:/usr/local/bin/geckodriver
export PATH=$PATH:/usr/local/bin/chromedriver