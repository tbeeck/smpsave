import argparse
import sys

def main():
	if len(sys.argv) < 2:
		return
	action = sys.argv[1]
	print("Action:", action)


if __name__ == '__main__':
	main()