#simple non-quine but constantly actualized

s = open("tgircbot.py","r")
a = ""
#a = str(s)
#print a

#for line in s:
#    a = a + line

a = s.read()

r = []
i = 0
while i < (len(a)):
    r.append(a[i:i+4090])
    i = i + 4090

for x in r:
    print x
    print "=================================="
