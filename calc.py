import random

i = ""
randnum = []
result = 0

def rand():
    randNum = random.randint(-9, 9)
    return randNum



while i != 'exit':
    i = input('')
    if i == '.':
        print(sum(randnum),'...............')
        randnum.clear()
    else :
        r = rand()
        randnum.append(r)
        print(r)