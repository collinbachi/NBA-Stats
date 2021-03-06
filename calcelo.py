''' Calculate Elo '''

import math
import time
import random
from operator import itemgetter
import sys, getopt

class Prediction:

	def __init__(self, coeffs, stdevs):
		self.K = coeffs[0]
		self.SCORE_FACTOR = coeffs[1]
		self.coeffs = coeffs[2:]
		self.stdevs = stdevs
		self.msqdev = 0
		self.picks = 0
		self.count = 0

	def init_ratings(self):
		self.ratings = {	'Boston Celtics': 1400,
				'Brooklyn Nets': 1400,
				'New York Knicks': 1400,
				'Philadelphia 76ers': 1400,
				'Toronto Raptors': 1400,
				'Chicago Bulls': 1400,
				'Cleveland Cavaliers': 1400,
				'Detroit Pistons': 1400,
				'Indiana Pacers': 1400,
				'Milwaukee Bucks': 1400,
				'Atlanta Hawks': 1400,
				'Charlotte Bobcats': 1400,
				'Miami Heat': 1400,
				'Orlando Magic': 1400,
				'Washington Wizards': 1400,
				'Denver Nuggets': 1400,
				'Minnesota Timberwolves': 1400,
				'Oklahoma City Thunder' : 1400,
				'Portland Trail Blazers': 1400,
				'Utah Jazz': 1400,
				'Golden State Warriors': 1400,
				'Los Angeles Clippers': 1400,
				'Los Angeles Lakers': 1400,
				'Phoenix Suns': 1400,
				'Sacramento Kings': 1400,
				'Dallas Mavericks': 1400,
				'Houston Rockets': 1400,
				'Memphis Grizzlies': 1400,
				'New Orleans Pelicans': 1400,
				'San Antonio Spurs': 1400
				}

	def test(self, i):
		picks = 0
		count = 0
		samples = list(set([random.randint(1000, 2500) for _ in range(1000)]))
		i.seek(0)
		self.init_ratings()

		for num, line in enumerate(i.readlines()):
			winner = line[:line.index('>')].strip()
			loser = line[line.index('>') + 1: line.index('|')].strip()
			score = line[line.index('&') + 1:].strip().split()
			wHome = 1 if line[line.index('|') + 1: line.index('^')].strip() == 'H' else 0 # BACKWARDS needs to be fixed
			wlOdds = line[line.index('^') + 1:line.index('&')].strip().split()
			wOdd = float(wlOdds[0])
			lOdd = float(wlOdds[1])
			score = abs(int(score[0]) - int(score[1])) 
			
			try:
				winnerR = self.ratings[winner]
			except: continue
			loserR = self.ratings[loser]
			try:
				winnerEX = 1.0 / (1 + math.pow(10 , ((1.0 * loserR - winnerR)/400)))
				loserEX = 1.0 / (1 + math.pow(10 , ((1.0 * winnerR - loserR)/400)))
			except:
				print abs(winnerR - loserR)
				return 0.0
			self.ratings[winner] = self.ratings[winner] + math.pow(score, self.SCORE_FACTOR) * self.K * (1 - winnerEX)
			self.ratings[loser] = self.ratings[loser] + math.pow(score, self.SCORE_FACTOR) * self.K * (0 - loserEX)
			wisheat = 1 if winner == 'Miami Heat' else 0
			lisheat = 1 if loser == 'Miami Heat' else 0

			if num in samples:
				self.msqdev += math.pow(1 - winnerEX, 1)

				winner_ts = self.coeffs[0] * math.pow(winnerEX, self.coeffs[2]) + self.coeffs[1] * wisheat + self.coeffs[3] * wHome + self.coeffs[4] * wOdd
				loser_ts = self.coeffs[0] * math.pow(loserEX, self.coeffs[2]) + self.coeffs[1] * lisheat + self.coeffs[3] * (1 - wHome) + self.coeffs[4] * lOdd

				if winner_ts > loser_ts: picks+=1
				count+=1

		return 1.0 * picks / count

	def print_ratings(self, o):
		rlist = [(k,v) for (k,v) in self.ratings.iteritems()]
		rlist = sorted(rlist, key=itemgetter(1), reverse=True)
		for k, v in rlist:
			o.write(k + ': ' + str(round(v, 2)) + '\n')


if __name__ == '__main__':
	stime = time.time()
	bests = []
	updatesGA = False

	i = open('bestnewest.txt', 'r')
	gaout = open('gadata.txt', 'r')

	NUM_PARENTS = 4
	names_coeffs = ['K', 'ScoreExp', 'Elo', 'IsHeat', 'EloExp', 'Home', 'Odds']
	fit_coeffs = []
	stdev_coeffs = [.05, .01, .05, .05, .01, .05, .3]

	for j, line in enumerate(gaout.readlines()):
		fit_coeffs.append([])
		vals = line.split()
		for val in vals:
			fit_coeffs[j].append(float(val))

	bestResult = Prediction(fit_coeffs[0], stdev_coeffs).test(i)
	gaout.close()

	fixed_coeffs = fit_coeffs[:]
	for j in range(len(fit_coeffs)):
		for ii in range(25):
			for _, v in enumerate(fixed_coeffs[j]):
				fit_coeffs[j][_] = random.normalvariate(v, stdev_coeffs[_])

			pred = Prediction(fit_coeffs[j], stdev_coeffs)
			result = (pred.test(i) + pred.test(i)) / 2.0
			rlist = [result]
			for vv in fixed_coeffs[j]:
				rlist.append(vv)
			bests.append(rlist)
			print '{}% '.format(round(result*100, 2)),
			for _, v in enumerate(fit_coeffs[j]):
				print '{}={} '.format(names_coeffs[_], round(v, 2)),
			print
	pred.print_ratings(open('ratingsout.txt', 'w'))

	bests = sorted(bests, key=itemgetter(0), reverse=True)
	print sum([_[0] for _ in bests]) / len(bests)


	if updatesGA:
		gaout = gaout = open('gadata.txt', 'w')
		for k in range(NUM_PARENTS):
			for _, v in enumerate(bests[k][1:]):
				gaout.write('{} '.format(v))
			gaout.write('\n')

		gaout.close()
	
	print 'time: ' + str(time.time() - stime)

''' TODO: -i input, -o output, -p preditction file '''
