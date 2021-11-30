from urllib import parse
file_objects = ["index.html", "style.css"]

for file in file_objects:
    parsed_url = parse.urlparse("https://codehs.com/editor/426681/solution/index.html")

    url_path = str(parsed_url[2]).split('/')

    new_path = "/".join(parsed_url[2].split('/')[:-1]) + f"/{file}"
    print(new_path)

    print("https://" + str('/'.join(parsed_url[1:2])) + new_path)
