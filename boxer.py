# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import json

class BoxerSpider(scrapy.Spider):
    name = 'boxer'
    base_url = 'http://box.live/boxing-rankings/'

    #custom header
    headers = {
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }

    #Crawlers entry point
    def start_requests(self):
    	yield scrapy.Request(
    		url = self.base_url,
    		headers = self.headers,
    		callback = self.parse_boxers)

    def parse_boxers(self, response):
    	 #extracting champions
    	 boxer_urls = []

    	 champions_url = response.css('div[class="rank_full_mini"]')
    	 champions_url = champions_url.css('a[href*="boxers"]::attr(href)')
    	 champions_url = champions_url.getall()
    	 
    	 #Extract challenger URL's
    	 challenger_url = response.css('div[class="rank_full_mini"]')
    	 challenger_url = challenger_url.css('ol').css('li')
    	 challenger_url = challenger_url.css('a::attr(href)')
    	 challenger_url = challenger_url.getall()

    	 #loop over champions url
    	 for champions in champions_url:
    	 	#append to boxer_list
    	 	boxer_urls.append(champions)

    	 for challengers in challenger_url:
    	 	#append to boxer_list
    	 	boxer_urls.append(challengers)

    	 #boxer count for debugging process
    	 count = 1
    	
    	 for boxer_url in boxer_urls:
    		# crawl boxer's profile
    		 yield response.follow(
    			url=boxer_url,
    			headers=self.headers,
    			#for debugging
    			meta={
    				'count': count,
    				'total': len(boxer_urls)
    			},
    			callback=self.parse_profile
    		 )
    		 #break
    		 # increment boxer count
    		 count += 1

    #crawl profile
    def parse_profile(self, response):
    	'''
    	#store response locally
    	with open('profile.html','w', encoding = "utf-8") as f:
    		f.write(response.text)
    	'''
    	'''
    	# local HTML content
    	content = ''
        
        
    	# open local HTML file
    	with open('profile.html', 'r',encoding="utf8") as f:
    	    for line in f.read():
    	        content += line
    	
    	# init scrapy selector
    	response = Selector(text=content)
    	'''
    	# extract current boxer count
    	count = response.meta.get('count')
    	total = response.meta.get('total')
    	
    	# print debug info
    	print('\n\nBoxer #%s out of %s total boxers\n\n' % (count, total))

    	#print(response)
    	#extract profile features
    	features = {
    		'name:' : response.css('li[class="hightlight full-record"]')
    						  .css('h1::text').get(),
    		'image_url': response.css('div[class="single-fighter"]')
    							 .css('img::attr(src)')
    							 .get(),

    		'record' : response.css('span[class="record"]::text').get(),
    		'titles': {
    			'IBF': response.css('li[class="ibf-belt belt-row"]::text').get(),
    			'WBO': response.css('li[class="wbo-belt belt-row"]::text').get(),
    			'WBA': response.css('li[class="wba-belt belt-row"]::text').get()
    		},
    		
    		'points_count': [],
    		
    		
    		#didnt work this way
    		#'point_count': {
    		#	'TKO': response.css('span[class="points-count"]').css('small::text')[0].get(),
    		#	'UD' : response.css('span[class="points-count"]').css('small::text')[1].get(),
    		#	'TKO1' : response.css('span[class="points-count"]').css('small::text')[2].get(),
    		#	'TKO2': response.css('span[class="points-count"]').css('small::text')[3].get(),
    		#	'UD1' : response.css('span[class="points-count"]').css('small::text')[4].get()
    		#},

    		'stats': {
    			'age': response.css('span[class="f-desc"]::text').getall()[0],
    			'height': response.css('span[class="f-desc"]::text').getall()[1],
    			'reach': response.css('span[class="f-desc"]::text').getall()[2],
    			'stance': response.css('span[class="f-desc"]::text').getall()[3],
    		},
            
    		'full_record': {
    			'wins': response.css('span[class="f-desc"]::text').getall()[4],
    			'by_ko': response.css('span[class="f-desc"]::text').getall()[5],
    			'ko_%': response.css('span[class="f-desc"]::text').getall()[6],
    			'lost': response.css('span[class="f-desc"]::text').getall()[7],
    			'stopped': response.css('span[class="f-desc"]::text').getall()[8],
    			'draws': response.css('span[class="f-desc"]::text').getall()[9],
    			'debut': response.css('span[class="f-desc"]::text').getall()[10],
    			'pro_rds': response.css('span[class="f-desc"]::text').getall()[11]
    		},

    		#we found error with wbo
    		'ranking': {},
    		'division': "".join([
    					text.get().split(' @ ')[-1]
    					for text in 
    					response.css('li[class="hightlight full-record"]::text')
    					if '@' in text.get()
    					]),

    		'description': '\n'.join(response.css('div[class="expert-fighter-filters"]')
            								 .css('p::text')
    										 .getall()),
    		'odds': [],
    		'potential_fights': [],
    		
    	}

    	#extract Ranking
    	try:
    			features['ranking'] = {
    			'wbo': response.css('span[class="f-desc"]::text').getall()[12],
    			'ibf': response.css('span[class="f-desc"]::text').getall()[13],
    			'wbc': response.css('span[class="f-desc"]::text').getall()[14],
    			'wba': response.css('span[class="f-desc"]::text').getall()[15]
    			}
    	except:
    		pass
    	# extract points count keys
    	points_count_keys = list(filter(None, [
    							text.get().replace('\n', '').strip()
    							for text in
    							response.css('span[class="points-count"]').css('i::text')
    							if text.get() != ' < '
    						]))

    	# extract points count values
    	points_count_vals = list(filter(None, [
    							text.get().replace('\n', '').strip()
    							for text in
    							response.css('span[class="points-count"]')
    									.css('i')
    									.css('small::text')
    							if text.get() != ' < '
    						]))

    	# loop over the range of points count
    	for index in range(0, len(points_count_vals)):
    		features['points_count'].append(
    			{points_count_keys[index]: points_count_vals[index]}\
    		)


    	#scraping odds
    	for table in response.css('table[class="responsive boxing-betting-table"]'):
    		
    		# extract odds row
    		odds_row = list(filter(None, [
    							text.get().replace('\n', '').replace(' ', '')
    							for text in
    							table.css('tr').css('span[class="dec odd"] *::text')
    							]))
            
    		

    		# extract fighter name
    		fighter_name = table.css('td[class="fighter_name"]').css('a::text').getall()
    		
    		features['odds'].append({
    			'boxer': {
    				'name': fighter_name[0],
    				'williamhill': odds_row[0],
    				'unibet': odds_row[1],
    				'boyle': odds_row[2],
    				'ladbrokes': odds_row[3],
    				'skybet': odds_row[4],
    				'betway': odds_row[5],
    				'bwin': odds_row[6],
    				'betfred': odds_row[7],
    				'winner': odds_row[8]
    			},
    			
    			'opponent': {
    				'name': fighter_name[1],
    				'williamhill': odds_row[9],
    				'unibet': odds_row[10],
    				'boyle': odds_row[11],
    				'ladbrokes': odds_row[12],
    				'skybet': odds_row[13],
    				'betway': odds_row[14],
    				'bwin': odds_row[15],
    				'betfred': odds_row[16],
    				'winner': odds_row[17]
    			}
    			})

    	

    	#extract potential fights
    	for fight in response.css('div[class="boxer-area"]')[1:]:
    		# extract potential date
    		try:
    			potential_date = fight.css('span[class="date potenclash"]::text').get()
    			potential_date = potential_date.strip('\n').split(' : ')[-1]
    			
    		except:
    			potential_date = 'N/A'    		
    		
    		features['potential_fights'].append({
    		'opponent_name': fight.css('span[class="l-name"]::text').get(),
    		'opponent_image_url': fight.css('div[class="right"]').css('img::attr(src)').get(),
    		'opponent_record' : fight.css('span.record-r').css('span::text').get().strip('\n'),
    		'potential_date' : potential_date,
    		'title_belts': {
    							'wbc': fight.css('li[class="wbc-belt belt-row"]::text').get(),
    							'ibf': fight.css('li[class="ibf-belt belt-row"]::text').get(),
    							'wba': fight.css('li[class="wba-belt belt-row"]::text').get(),
    							'wbo': fight.css('li[class="wbo-belt belt-row"]::text').get()
    					}
    		})	

    			
    	#printing resulting dataset
    	#print(json.dumps(features, indent = 2))

    	# write features to file
    	with open('boxers.jsonl', 'a') as f:
    		f.write(json.dumps(features, indent=2) + '\n')
