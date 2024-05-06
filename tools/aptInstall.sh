BLUE='\033[36m'
GREEN='\033[32m'

cd ..

echo -e "${BLUE}Starting makeConfig.py\033[0m"
python3 tools/makeConfig.py

sudo apt install pip -y
echo ""
echo -e "${GREEN}pip installed!\033[0m"
echo ""

sudo pip install -r requirements.txt
echo ""
echo -e "${GREEN}Requirements!\033[0m"
echo ""

touch machines.json
echo ""
echo -e "${GREEN}Empty JSON created!\033[0m"
echo ""

echo ""
echo -e "${BLUE}=========================================\033[0m"
echo -e "${BLUE}|  ${GREEN}Alex's file mover install complete!  ${BLUE}|\033[0m"
echo -e "${BLUE}=========================================\033[0m"
echo ""