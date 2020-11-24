import requests
from bs4 import BeautifulSoup
import random
import time
import os

# List of user agent to rotate them for avoiding being blocked
userAgents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Opera/9.80 (Macintosh; Intel Mac OS X; U; en) Presto/2.2.15 Version/10.00",
    "Opera/9.60 (Windows NT 6.0; U; en) Presto/2.1.1"
]

# Request url and return it
def request(url, payload):
    if not url or not payload:
        return -1

    # Pick a user agent from the list
    userAgent = random.choice(userAgents)
    print("===============")
    print("userAgent: " + userAgent)

    # Request Amazon list of products page according to the keyword and page number
    headers = { "user-agent": userAgent }
    r = requests.get(url, headers=headers, params=payload)

    print("URL: " + r.url)
    print("Status code:", r.status_code)
    print("===============")
    return r

# Parse Amazon list of products page and write extracted data into the file
def parseHTML(html, filename):
    if not html or not filename:
        return False

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Get the div containg all the results
    results = soup.body.find_all(class_="s-result-item")
    if not results:
        return False

    # Open the file where write the extracted data
    with open(filename, "a") as file:
        # Scan all the results
        for result in results:
            #print("*******************")

            # Try to get all data of interest
            try:
                h2          = result.h2
                url         = h2.a["href"]
                description = h2.span.string
                rank        = result.find("span", "a-icon-alt").string[:3]
                price       = result.find("span", "a-offscreen").string

            except Exception as e:
                #print(e)
                continue

            # Check if prime icon is present
            prime = result.find("i", "a-icon-prime")
            if (prime):
                prime = "True"
            else:
                prime = "False"

            '''print(description)
            print(price)
            print(prime)
            print(url)
            print(rank)'''

            line = description + "\t" + price + "\t" + prime + "\t" + url + "\t" + rank + "\n"
            file.write(line)

    return True


url        = "https://www.amazon.it/s"
keyword    = "computer"
pageNumber = 1

payload = { "k": keyword, "page": pageNumber }

filename = "./products.tsv"

# Before start remove previous file
if os.path.exists(filename):
  os.remove(filename)

while True:
    print(payload["page"])

    # Request the page
    r = request(url, payload)
    if r.status_code != 200:
        break

    # Parse the HTML of the page and write extracted data into a file
    success = parseHTML(r.text, filename)

    # Wait 5 seconds to avoid been blocked
    time.sleep(5)

    # Check if success, otherwise perform another request of the same page
    if not success:
        continue

    # Go to next page
    payload["page"] += 1
