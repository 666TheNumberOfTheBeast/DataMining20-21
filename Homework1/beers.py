# Find the top-10 beers with the highest average overall score among the beers that have had at least 100 reviews.
# Some beers appear in multiple lines, do preprocessing, in order to sum score of the reviews

# Use a hash table => dictionary
dict = {}

with open('beers.txt', 'r') as file:
    for line in file:
        # Split the line according to the separator into max 2 elements
        items = line.strip().split(sep="\t", maxsplit=1)

        # Try to get key and score (converting the latter to integer)
        try:
            key   = items[0]
            score = int(items[1])

            #print(key)
            #print(score)
        except:
            continue

        # Check if the key is already in the dictionary otherwise init a new entry
        if key in dict:
            overallScore, nr = dict[key]
            dict[key] = (overallScore+score, nr+1)
        else:
            dict[key] = (score, 1)

#print(dict)

# Sort the dictionary by the average overall score of each entry within the dictionary from largest to smallest
sorted = sorted(dict.items(), key=lambda item : item[1][0]/item[1][1], reverse=True)

#print(sorted)

i  = 0
n  = 10
nr = 100

for item in sorted:
    if item[1][1] >= nr:
        print(item)

        i+=1
        if i == n:
            break
