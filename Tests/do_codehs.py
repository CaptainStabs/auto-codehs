import requests
from lxml.html import fromstring

student_number = "1758629"
section_number = "234939"

payload={}
headers = {
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Cookie': '_ga=GA1.2.794132728.1634580125; _gat=1; _gid=GA1.2.814236272.1636467944; csrftoken=aXsurNihSC9S6W9VRiYoiIMA8QmLGQbq; sessionid=6z3pdinm3zco08wd4vg3m9pkkifexj51; uid=1758629; username=TheSFMgineer'
}

s = requests.Session()
s.headers.update(headers)

for assignment_number in range(50244506, 50244630):
    url = f"https://codehs.com/student/{student_number}/section/{section_number}/assignment/{assignment_number}/"
    response = s.request("GET", url, data=payload)
    with open("test.html", "w") as test_file:
        test_file.write(response.text)


    parser = fromstring(response.text)

    student_assignment_id = parser.xpath(f'//*[@href="/student/{student_number}/section/{section_number}/assignment/{assignment_number}/"]/@data-said')[0]
    print(student_assignment_id)

    no_name = False
    while not no_name:
        try:
            print(parser.xpath('//*[@class="__abacus_editor-label"]/span/text()')[0])
            no_name = True
        except IndexError:
            print(parser.xpath('//*[@class="__abacus_editor-label"]/span/text()'))
            no_name = False

    # if
    break




def submit_answer(student_assignment_id):
    submit_api_url = "https://codehs.com/lms/ajax/submit_assignment"

    payload = f'method=submit_assignment&student_assignment_id={student_assignment_id}'
    submitted_answer = s.request("POST", submit_api_url, data=payload)

def get_answer():
    return

def next_module():
    return                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
