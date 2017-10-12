## start elasticsearch service ##
echo " "
echo ">> Starting Elasticsearch (ES)"
sudo systemctl stop elasticsearch
sudo systemctl start elasticsearch

echo " "
echo ">> Wait few seconds"
sleep 5


## delete index before starting satori new data collection
read -n1 -p ">> Delete Do that? [y,n]" doit
case $doit in
  y|Y) curl -X DELETE 'http://localhost:9200/satori/youtube-videos' ;;
  n|N) echo ">> Appending to old index" ;;
  *) echo ">> Unknown option" ;;
esac


## start reading the messages from satori ##
echo " "
echo ">> Starting satori data collection"
nohup python feedhandler/satori_youtube.py --credentials=feedhandler/credentials.json &
