from urllib import parse
parsed_url = parse.urlparse("https://codehs.com/student/1758629/section/234939/assignment/50244505/")

# This could be compressed down to one line
url_path = str(parsed_url[2]).split('/')
next_assignment_number = int(url_path[-2]) + 1
print(next_assignment_number)
new_path = "/".join(parsed_url[2].split('/')[:-2]) + f"/{next_assignment_number}"
print(new_path)


print("https://" + str('/'.join(parsed_url[1:2])) + new_path)
