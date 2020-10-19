import csv

NANKey = ["0","","停牌","N"]

isNotLim = csv.reader(open("isNotLim.csv", "r"))
isTrading = csv.reader(open("isTrading.csv", "r"))
isST = csv.reader(open("ST.csv", "r"))
result = csv.writer(open("result.csv", "w", newline=""))

# Result
heads = False
for INL,IT,IST in zip(isNotLim,isTrading,isST):
    if not heads:
        result.writerow(INL)
        heads = True
        continue
    cur = []
    head = False
    for inl,it,ist in zip(INL,IT,IST):
        if not head:
            cur.append(inl)
            head = True
            continue
        tmp = 0
        if int(inl) and int(it) and not int(ist):
            tmp = 1
        cur.append(tmp)
    result.writerow(cur)