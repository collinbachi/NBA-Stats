''' Reverses the ordering of lines in a file '''

import sys

def reverse_lines(i, o):
	lines = []
	for line in i.readlines():
		lines.append(line)
	lines.reverse()
	for line in lines:
		o.write(line)

if __name__ == '__main__':
	i = open(sys.argv[1], 'r')
	o = open(sys.argv[1] + '_r', 'w')
	reverse_lines(i, o)
	i.close()
	o.close()