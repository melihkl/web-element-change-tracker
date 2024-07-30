# Web Element Change Tracker

The Web Element Change Tracker is a tool designed to monitor web pages and track changes in web elements, such as buttons, inputs, text areas, and select elements. It uses Selenium WebDriver for automation and provides detailed reports on the changes detected, including new, removed, and modified elements.

## Features
- Multi-browser Support: Compatible with both Chrome and Edge browsers.
- Automated Login: Supports automated login for pages requiring authentication.
- Change Detection: Identifies changes in web elements, including additions, deletions, and modifications.
- Detailed Reporting: Generates comprehensive HTML reports detailing all detected changes.

## Requirements
- Python 3.x
- Selenium
- WebDriver: ChromeDriver or EdgeDriver, depending on the browser used

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/melihkl/web-element-change-tracker.git
    ```
2. Install Dependencies
   ```bash
    pip install selenium
    ```
3. Set Up Configuration
  - Update config.json with your settings, including:
    - browser_type: "Chrome" or "Edge"
    - login_required: true or false
    - login_url, username, password: Required if login is needed.
    - username_element, password_element, login_button_element: The IDs of the respective elements on the login page.
  - Populate pages.json with the URLs and names of the pages to monitor.

## Output
- changes.json: A JSON file logging all detected changes.
- previous_data.json: Stores the state of elements from the last run for comparison.
- changes_report.html: An HTML report detailing the changes, formatted for easy review.

## Configuration Details
- config.json: Contains settings for the tool, such as browser type, login credentials, and element selectors.
- pages.json: Lists the pages to be monitored, formatted as key-value pairs of page names and URLs.

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License - see the LICENSE file for details.
