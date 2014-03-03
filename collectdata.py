from bs4 import BeautifulSoup
from urllib2 import urlopen
from reverselines import reverse_lines
import time
from selenium import webdriver
URL = ['http://www.oddsportal.com/basketball/usa/nba/results/page/{}/',
		'http://www.oddsportal.com/basketball/usa/nba-2012-2013/results/page/{}/',
		'http://www.oddsportal.com/basketball/usa/nba-2011-2012/results/page/{}/']
num_pages = [13, 30, 24]
def generate_data(page, f, URL):
	html = urlopen(URL.format(page)).read()
	pg = BeautifulSoup(html)

	browser = webdriver.Chrome('C:/DCB/chromedriver_win32/chromedriver.exe')
	browser.get(URL.format(page))
	odds = browser.find_elements_by_class_name('odds-nowrp')

	odds = [element.text for element in odds]
	oddsindex = 0
	browser.quit()

	data = pg.find_all('td', {'class': 'name table-participant'})
	scores = pg.find_all('td', {'class': 'center bold table-odds'})
	
	for t, score in zip(data, scores):
		try:
			f.write(fix_str(t.span.string))
			f.write(' > ')
		except AttributeError:	# Rare case where neither is bolded (ex. game cancelled)
			continue
		for order, s in enumerate(t.a.stripped_strings):
			if s.strip() != t.span.string.strip():
				f.write(fix_str(s))
				if order == 1: 
					f.write(' |H') 
					f.write(' ^{} {}'.format(fix_odds(odds[oddsindex]), fix_odds(odds[oddsindex + 1])))
					oddsindex += 2
				else: 
					f.write(' |A')
					f.write(' ^{} {}'.format(fix_odds(odds[oddsindex + 1]), fix_odds(odds[oddsindex])))
					oddsindex += 2
				break
		f.write(' & ')
		f.write(fix_str(score.string))
		f.write('\n')

def fix_odds(s):
	try:
		if '+' in s:
			return str(float(s[1:]) / 100 + 1)
		elif '-' in s:
			return str((float(s[1:]) + 100)/float(s[1:]))
		elif '/' in s:
			s = s.strip()
			return str((float(s[:s.find('/')]) / float(s[s.find('/') + 1:]) + 1.0))
		elif '.' in s: return s
		else: 
			print s
			return 1.0
	except: return 1.0

def fix_str(s):
	s = s.strip()
	if ':' in s:
		if 'OT' in s: s = s[:s.find('OT')].strip()
		s = s.split(':')
		s = [int(_) for _ in s]
		s = sorted(s, reverse=True)
		s = [str(_) for _ in s]
		s = ' '.join(s)
	else:
		s = s.replace('- ', '')
		s = s.replace('-', '')
	return s.encode('UTF-8')

def readCommand():
  """
  Processes the command used to output to a different file.
  """
  import sys
  from optparse import OptionParser
  argv = sys.argv[1:]
  usageStr = """
  USAGE:      python collectdata.py -o output.txt
  """
  parser = OptionParser(usageStr)

  default_fn = 'out' + time.strftime('%m_%d_%y_%H_%M_%S', time.localtime()) + '.txt'

  parser.add_option('-f', '--file', dest='fn',
                    help='the output file (default is timestamped)',
                    metavar='FILE', default=default_fn)

  options, otherjunk = parser.parse_args(argv)

  return options.fn
  

if __name__ == '__main__':
	fn = readCommand()
	f = open('temp', 'w+')
	for url, p in zip(URL, num_pages):
		for i in range(1, p):
			print i
			generate_data(i, f, url)
	f.close()
	f = open('temp', 'r')
	fout = open(fn, 'a')
	reverse_lines(f, fout)
	f.close()
	fout.close()