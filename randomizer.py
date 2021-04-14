import sys, csv, random

def randomizer(argv):
    csvFile = str(argv[0])
    # print(csvFile)
    num = int(argv[1])

    reader = csv.reader(open(csvFile, 'r'))
    writer = csv.writer(open('hudmortgages.csv', 'w', newline=''))

    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        writer.writerow(next(reader))

        data = list(reader)
        for i in range(num):
            randRow = random.choice(data)
            writer.writerow(randRow)
     
if __name__ == "__main__":
   randomizer(sys.argv[1:])