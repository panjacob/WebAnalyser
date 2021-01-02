import os
from matplotlib import pyplot as plt

site_dir = "sites/wp.pl"
searched_word = 'epidemia'
files = os.listdir(site_dir)


def dates_sorted(files):
    numbers = []
    for file in files:
        number = file.split('.')[0]
        numbers.append(int(number))
    return sorted(numbers)


dates = dates_sorted(files)
result = []

for date in dates:
    date = str(date)
    word_count = 0
    text = open(site_dir + "/" + date + ".txt", "r").read().lower()
    text_list = text.split(' ')
    for word in text_list:
        if word.__contains__(searched_word):
            word_count += 1
    result.append(word_count)

plt.title(searched_word + " " + site_dir)
plt.plot( result)
# plt.axis([0, 6, 0, 20])
plt.show()


