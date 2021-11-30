from bs4 import BeautifulSoup
import requests

solution_url = "https://codehs.com/editor/426681/solution/index.html"
answer = requests.request("GET", solution_url)
print(answer.text)
soup = BeautifulSoup(answer, "html.parser")
for data in soup(["noscript", "script", "grammarly-desktop-integration"]):
    data.decompose()

print(soup)
