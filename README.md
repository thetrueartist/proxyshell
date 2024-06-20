# ProxyShell: A Bash Shell with Integrated Proxy Fetching, Verifying, Management and Scraping Capabilities

Welcome to **ProxyShell**, a customizable bash shell designed to fetch, verify and manage HTTP and HTTPS proxies efficiently. It allows you to run shell commands and Python scripts through a dynamic proxy chain, ensuring enhanced privacy and connectivity.

## Features of Proxyshell

### Proxy Management
- **Proxy Fetching & Verification**: Fetches verfies and filters out non-working proxies from various online sources (*proxynova.com & free-proxy-list.net*).
- **Dynamic Proxy Switching**: Automatically cycle through available HTTP and HTTPS proxies to ensure continuous connectivity.
- **Background Verifcation**: Fetches and verifies new proxies as well as old ones to ensure reliable connectivity.
- **Asynchronous Requests**: **Blazing fast** - fetch and verify over 700* proxies in under 20 seconds - it utilizes `aiohttp` for speedy and efficient asynchronous HTTP/HTTPS requests.
- **Proxy Status**: View the current status of HTTP and HTTPS proxies, including the count of available proxies.

### Command Execution
- **Proxied Shell Commands**: Run shell commands through the current proxy.
- **Python Script Execution**: Execute Python scripts in a proxied environment using the `runpy` module.

### Web Scraping
- **URL Scraping**: Scrape data from URLs provided in a text file and save the results in CSV format.
- **Data Parsing**: Extract titles, headings, paragraphs, tables, images, and links from HTML content using BeautifulSoup.

### IP and Browser Management
- **Public IP Check**: Check your current proxied public IP address using `ifconfig.me`.
- **Firefox Integration**: Launch and close Firefox with the current HTTPS proxy settings.

### Drawbacks
- **Disallowed Commands**: Due to the fact that these proxies are all HTTP/HTTPS proxies the script prevents execution of certain commands (`ping`, `traceroute`, `ssh`, etc.) as they **will not work**.

## Usage

### Starting ProxyShell
```bash
python proxyshell.py
You will enter the proxyshell environment, where you can use the following commands after it automatically fetches and verifies proxies.

Commands:

Proxy Management
exit: Exit the proxy shell.
status: Show the current proxy status.
refresh: Refresh the proxy list by removing non-working proxies and adding new ones.

Command Execution
myip: Check the current public IP address.
run <script_path>: Run a Python script using runpy.
firefox: Launch Firefox with the current HTTPS proxy.
firefox_close: Close all instances of Firefox.

Web Scraping
Create a text file urls.txt with URLs to scrape, then run:
scrape <file_path>: Scrape URLs from a provided text file and store data in CSV format:
The scraped data will be saved to scraped_data.csv.

Checking Public IP Address
proxyshell> myip

Running a Python Script
proxyshell> run <python script path>
```
## Dependencies

requests
beautifulsoup4
pandas
tqdm
colorama
aiohttp

Ensure these libraries are installed **before** running ProxyShell:

**pip install requests beautifulsoup4 pandas tqdm colorama aiohttp**

## Contributing
Feel free to open issues or submit pull requests. Contributions are welcome!

### Enjoy using ProxyShell for your proxy usage and web scraping tasks!
