with open('demo.txt', 'r') as f:

    line = f.readline()
    while line:
        print(line)
        line = f.readline()

print('Done!')