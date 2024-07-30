import os
import time
import json
from selenium import webdriver
from selenium.webdriver import EdgeOptions, ChromeOptions
from selenium.webdriver.common.by import By

driver = webdriver

with open('config.json') as config_file:
    config = json.load(config_file)

if config['browser_type'] == "Edge":
    options = EdgeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Edge(options=options)
elif config['browser_type'] == "Chrome":
    options = ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

driver.maximize_window()

if config['login_required']:
    driver.get(config["login_url"])
    time.sleep(1)
    username = driver.find_element(By.ID, config['username_element'])
    password = driver.find_element(By.ID, config['password_element'])
    username.send_keys(config['username'])
    password.send_keys(config['password'])
    driver.find_element(By.ID, config['login_button_element']).click()
    time.sleep(1)

with open('pages.json') as pages_file:
    pages = json.load(pages_file)

previous_data = {}
if os.path.exists('previous_data.json'):
    with open('previous_data.json', encoding="utf-8") as previous_file:
        previous_data = json.load(previous_file)

changes = {}

for page_name, page_url in pages.items():
    driver.get(page_url)
    time.sleep(2)

    driver.execute_script("""
    window.getXPath = function(element) {
        if (element.id !== '') {
            return 'id("' + element.id + '")';
        }
        if (element.tagName === 'HTML') {
            return '/' + element.tagName.toLowerCase();
        }
        if (element === document.body) {
            return '/html/body';
        }

        var ix = 0;
        var siblings = element.parentNode.childNodes;
        for (var i = 0; i < siblings.length; i++) {
            var sibling = siblings[i];
            if (sibling === element) {
                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
            }
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                ix++;
            }
        }
    }
    """)

    elements = driver.find_elements(By.XPATH, '//button | //input | //textarea | //select')
    current_elements_info = {}

    for element in elements:
        element_xpath = driver.execute_script("return getXPath(arguments[0]);", element)
        element_info = {
            "type": element.get_attribute('type'),
            "id": element.get_attribute('id'),
            "name": element.get_attribute('name'),
            "className": element.get_attribute('class'),
            "text": element.get_attribute('outerText'),
            "xpath": element_xpath
        }
        current_elements_info[element_xpath] = element_info

    previous_elements_info = previous_data.get(page_url, {})
    page_changes = {"added": {}, "removed": {}, "modified": {}}

    for xpath, info in current_elements_info.items():
        if xpath not in previous_elements_info:
            page_changes["added"][xpath] = info
        elif info != previous_elements_info[xpath]:
            page_changes["modified"][xpath] = {
                "previous": previous_elements_info[xpath],
                "current": info
            }

    for xpath, info in previous_elements_info.items():
        if xpath not in current_elements_info:
            page_changes["removed"][xpath] = info

    if any(page_changes.values()):
        changes[page_url] = {
            "page_name": page_name,
            "changes": page_changes}

    previous_data[page_url] = {
        "page_name": page_name,
        "elements": current_elements_info}

    previous_data[page_url] = current_elements_info

with open('changes.json', 'w', encoding='utf-8') as changes_file:
    json.dump(changes, changes_file, indent=4, ensure_ascii=False)

with open('previous_data.json', 'w', encoding='utf-8') as previous_file:
    json.dump(previous_data, previous_file, indent=4, ensure_ascii=False)

driver.quit()


def json_to_html(changes):
    html_content = """
    <html>
    <head>
        <title>Element Changes Report</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .added { background-color: #eaffea; }
            .removed { background-color: #ffeaea; }
            .modified { background-color: #eaf3ff; }
        </style>
    </head>
    <body>
        <h2>Element Changes Report</h2>
    """

    for url, data in changes.items():
        page_name = data.get("page_name", "")
        html_content += f"""
        <h3>{page_name} ({url})</h3>
        <table>
            <tr>
                <th>Type</th>
                <th>XPath</th>
                <th>ID</th>
                <th>Name</th>
                <th>Class</th>
                <th>Text</th>
                <th>Change Type</th>
            </tr>
        """

        for xpath, info in data["changes"]["added"].items():
            html_content += f"""
            <tr class="added">
                <td>{info['type']}</td>
                <td>{xpath}</td>
                <td>{info['id']}</td>
                <td>{info['name']}</td>
                <td>{info['className']}</td>
                <td>{info['text']}</td>
                <td>Added</td>
            </tr>
            """

        for xpath, info in data["changes"]["removed"].items():
            html_content += f"""
            <tr class="removed">
                <td>{info['type']}</td>
                <td>{xpath}</td>
                <td>{info['id']}</td>
                <td>{info['name']}</td>
                <td>{info['className']}</td>
                <td>{info['text']}</td>
                <td>Removed</td>
            </tr>
            """

        for xpath, change in data["changes"]["modified"].items():
            previous = change["previous"]
            current = change["current"]
            html_content += f"""
            <tr class="modified">
                <td>{current['type']}</td>
                <td>{xpath}</td>
                <td>{previous['id']} -> {current['id']}</td>
                <td>{previous['name']} -> {current['name']}</td>
                <td>{previous['className']} -> {current['className']}</td>
                <td>{previous['text']} -> {current['text']}</td>
                <td>Modified</td>
            </tr>
            """

        html_content += "</table>"

    html_content += """
    </body>
    </html>
    """

    return html_content


with open('changes.json', 'r', encoding='utf-8') as changes_file:
    changes_data = json.load(changes_file)

html_report = json_to_html(changes_data)

with open('changes_report.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_report)
