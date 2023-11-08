import sys
import pandas as pd


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyse.py logfile")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])
    print(df[df.measure == 'won'].groupby('player').agg({'value': 'mean'}))


if __name__ == '__main__':
    main()
