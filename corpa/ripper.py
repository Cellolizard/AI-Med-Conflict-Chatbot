import requests
import urllib
import re
import csv
from boilerpipe.extract import Extractor

file = open('urls.csv', 'rb')
reader = csv.reader(file)
urls = list(reader)
corpus = open('corpus_plaintext.txt', 'a')
tot_url = succ_url = 0
for url in urls:
	tot_url += 1
	u = 'http://boilerpipe-web.appspot.com/extract?extractor=ArticleExtractor&output=text&extractImages=&token=&url=' + urllib.quote(url[0])
	print(u)
	extractor = Extractor(extractor='ArticleExtractor', url=u)
	extracted_text = extractor.getText()
	if resp.status_code == 200 and extracted_text:
		succ_url += 1
		# print re.sub(u"(\u2018|\u2019)", "'", resp.text)
		corpus.write(extracted_text.text.encode('ascii', 'ignore'))
print('{0} of {1} pages successfully ripped.'.format(tot_url, succ_url))