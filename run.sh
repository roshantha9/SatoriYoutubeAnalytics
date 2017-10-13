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

## start grafana service
echo " "
echo ">> Starting Grafana server"
#sudo service grafana-server start
sudo systemctl daemon-reload
sudo systemctl start grafana-server
#sudo systemctl status grafana-server

## start reading the messages from satori ##
echo " "
echo ">> Starting satori data collection"
nohup python feedhandler/satori_youtube.py --credentials=feedhandler/credentials.json --es_mapping=feedhandler/es-mapping.json &

## launch elasticHQ
firefox /home/rosh/Software/ElasticHQ/royrusso-elasticsearch-HQ-eb117d4/index.html

## launch grafana
firefox http://localhost:3000
