from datetime import datetime
import json
from pprint import pprint
import sys

from elasticsearch import Elasticsearch

logger = None

ES_INDEX = 'satori'
ES_DOC_TYPE = 'youtube-video'

class ESHandler(object):

    def __init__(self, log_handler, es_mapping_fname):
        global logger
        logger = log_handler

        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])  # elasticsearch instance

        # create an index with pre-defined mapping
        self.mapping = self._get_mapping(es_mapping_fname)
        self._delete_index(ES_INDEX) # first delete existing index (if any)
        self._create_index_with_mapping(ES_INDEX, self.mapping)




    def _get_mapping(self, mapping_fname):
        assert (mapping_fname != None), "Error! ES-mapping file not provided"
        with open(mapping_fname) as json_data_file:
            data = json.load(json_data_file)
        return json.dumps(data)


    def _create_index_with_mapping(self, index_name, index_mapping):
        try:
            self.es.indices.create(index=index_name, body=index_mapping)
        except:
            self._handle_es_exception("ESHandler::_create_index_with_mapping - ES exception", sys.exc_info())


    def _delete_index(self, index_name):
        try:
            self.es.indices.delete(index=index_name)
        except:
            logger.warning("ESHandler::_delete_index - ES exception")
            print sys.exc_info()
            pass


    def format_message(self, data):
        """ This will return a compressed version of the received message"""

        if data == None:
            logger.error("format_message: Empty message data")
            sys.exit()
        else:
            formatted_data = {
                #'ts': datetime.now(),
                '@timestamp': self._unix_time_millis(),
                'title': data['snippet']['title'].strip(),   # video title
                #'desc' :  data['snippet']['description'].strip(),  # description
                'desc' : "TBD",
                'ch_title' : data['snippet']['channel_title'].strip(),   # channel title
                'pub' : self._get_cleaned_published_date(data['snippet']['published_at']), # published date
                #'tags': "|".join(data['snippet']['tags']),   # video tags
                'tags': [s.strip() for s in data['snippet']['tags']] if len(data['snippet']['tags'])>0 else None, # video tags
                'cnt_dlikes': int(data['statistics']['dislike_count']) if data['statistics']['dislike_count'] != '' else 0,
                'cnt_likes': int(data['statistics']['like_count']) if data['statistics']['like_count'] != '' else 0,
                'cnt_views' : int(data['statistics']['view_count']) if data['statistics']['view_count'] != '' else 0
            }

            return formatted_data


    def push_to_es(self, data):
        formatted_data = self.format_message(data)
        #pprint(formatted_data)
        #print "---"
        try:
            self.es.index(index=ES_INDEX, doc_type=ES_DOC_TYPE,
                     #timestamp=datetime.now().isoformat(), # deprecated in ES 5.0
                     body=formatted_data)
            return formatted_data
        except:
            self._handle_es_exception("ESHandler::push_to_es - ES exception", sys.exc_info())


    def _get_cleaned_published_date(self, pubdate):
        if pubdate == '':
            return None
        elif "Streamed live on " in pubdate:
            return datetime.strptime(pubdate.replace('Streamed live on ', ''), '%b %d, %Y').strftime('%Y%m%d')
        else:
            try:
                return datetime.strptime(pubdate, '%b %d, %Y').strftime('%Y%m%d')
            except:
                return None

    def _handle_es_exception(self, msg, exec_info):
        logger.error(msg)
        print exec_info
        sys.exit()

    def _unix_time_millis(self):
        dt = datetime.now()
        epoch = datetime.utcfromtimestamp(0)
        return int((dt - epoch).total_seconds() * 1000.0) - 28800000
