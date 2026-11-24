import matplotlib.pyplot as plt

values = []
with open('data.txt') as f:
    for line in f:
        try:
            if (line.strip() and -10000000 < int(line.strip()) < 10000000):
                values.append(int(line.strip()))
        except:
            pass

plt.plot(values)
plt.xlabel('sample')
plt.ylabel('int32_t value')
#plt.axvline(16000)
#plt.axvline(16000 * 2)
plt.tight_layout()
plt.savefig('plot.png', dpi=300)
