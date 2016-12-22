import parenlang

import sys
import time

def parse_stdin():
	instr = sys.stdin.read()
	start = time.time()
	p = parenlang.Parser().parse(instr)
	end = time.time()
	print('Took {} seconds'.format(end - start))
	print('\n'.join(map(str, p)))

def main():
	parse_stdin()

if __name__ == '__main__':
	main()
