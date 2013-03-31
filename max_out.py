import sys


def main():
    classifications = dict()
    for line in sys.stdin:
        classification = line.strip().split()
        category = '0'
        if len(classification) == 2:
            category = classification[1]

        sha1 = classification[0]

        classifications[sha1] = max(classifications.get(sha1, '0'), category)


    for sha1, category in classifications.items():
        print sha1, category


if __name__ == "__main__":
    main()
