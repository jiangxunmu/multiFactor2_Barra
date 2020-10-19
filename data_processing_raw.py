import csv

NANKey = ["0","","停牌","N"]

closes = csv.reader(open("adj_price.csv", "r"))
opens = csv.reader(open("open_price.csv", "r"))
# highs = csv.reader(open("high_price.csv", "r"))
# lows = csv.reader(open("low_price.csv", "r"))
tradings = csv.reader(open("trading_status.csv", "r"))
isNotLim = csv.writer(open("isNotLim.csv", "w", newline=""))
isTrading = csv.writer(open("isTrading.csv", "w", newline=""))

# Is Not Limited
heads = False
for close,open in zip(closes,opens):
    if not heads:
        isNotLim.writerow(close)
        heads = True
        continue
    INL = []
    head = False
    for c,o in zip(close,open):
        if not head:
            INL.append(c)
            head = True
            continue
        inl = 0
        if c not in NANKey and o not in NANKey:
            inl = abs(float(c)/float(o)-1)<0.1
        INL.append(int(inl))
    isNotLim.writerow(INL)

# trading status processing
heads = False
wait = [0 for i in range(3845)]
for trading in tradings:
    if not heads:
        isTrading.writerow(trading)
        heads = True
        continue
    cur = []
    head = False
    for n, t in zip(range(3845), trading):
        if not head:
            cur.append(t)
            head = True
            continue
        if t in NANKey or wait[n] != 0:
            cur.append(0)
        else:
            cur.append(1)
        if t == "N":
            wait[n] = -120
        elif wait[n] < 0:
            wait[n] += 1
    isTrading.writerow(cur)


