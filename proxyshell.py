import requests

from bs4 import BeautifulSoup

import pandas as pd

import random

import concurrent.futures

from tqdm import tqdm

import time

from colorama import Fore, Style, init

import threading

import os

import cmd

import subprocess

from itertools import cycle

import aiohttp

import asyncio

import runpy



# Initialize colorama

init(autoreset=True)



USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",

    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

]



HTTP_TEST_URL = 'http://example.com'

HTTPS_TEST_URL = 'https://example.com'

INVALID_TITLES = ["No title found", "IIS Windows Server", "Error", "404 Not Found", "502 Bad Gateway", "500 Internal Server Error"]



DISALLOWED_COMMANDS = ["ping", "traceroute", "ssh", "telnet", "nc", "netcat"]



class ProxyShell(cmd.Cmd):

    intro = Fore.CYAN + "Welcome to the proxyshell. Type help or ? to list commands.\n"

    prompt = Fore.CYAN + 'proxyshell> '

    http_proxies = []

    https_proxies = []

    http_proxy_cycle = None

    https_proxy_cycle = None

    current_http_proxy = None

    current_https_proxy = None

    average_response_time = 5  # Initial average response time in seconds



    def preloop(self):

        self.http_proxy_cycle = cycle(self.http_proxies)

        self.https_proxy_cycle = cycle(self.https_proxies)

        self.switch_proxy('http')

        if self.current_http_proxy:

            print(Fore.GREEN + f'Using HTTP proxy: {self.current_http_proxy}')

        if self.current_https_proxy:

            print(Fore.GREEN + f'Using HTTPS proxy: {self.current_https_proxy}')



    def postcmd(self, stop, line):

        return stop



    def switch_proxy(self, protocol='http'):

        if protocol == 'https' and self.https_proxies:

            self.current_https_proxy = next(self.https_proxy_cycle)

            print(Fore.GREEN + f'Switched to new HTTPS proxy: {self.current_https_proxy}')

        elif protocol == 'http' and self.http_proxies:

            self.current_http_proxy = next(self.http_proxy_cycle)

            print(Fore.GREEN + f'Switched to new HTTP proxy: {self.current_http_proxy}')

        else:

            print(Fore.RED + f'No {protocol.upper()} proxies available to switch.')



    def do_exit(self, line):

        """Exit the proxy shell."""

        return True



    def do_status(self, line):

        """Show the current proxy status."""

        print(Fore.CYAN + f'Current HTTP proxy: {self.current_http_proxy if self.current_http_proxy else "None"}')

        print(Fore.CYAN + f'Available HTTP proxies: {len(self.http_proxies)}')

        print(Fore.CYAN + f'Current HTTPS proxy: {self.current_https_proxy if self.current_https_proxy else "None"}')

        print(Fore.CYAN + f'Available HTTPS proxies: {len(self.https_proxies)}')



    def do_refresh(self, line):

        """Refresh the proxy list by removing non-working proxies and adding new ones."""

        print(Fore.CYAN + "Verifying existing proxies...")

        existing_http_proxy_count = len(self.http_proxies)

        existing_https_proxy_count = len(self.https_proxies)



        # Verify old proxies

        verified_old_http_proxies, _ = asyncio.run(verify_proxies(self.http_proxies, HTTP_TEST_URL))

        verified_old_https_proxies, _ = asyncio.run(verify_proxies(self.https_proxies, HTTPS_TEST_URL))



        print(Fore.CYAN + "Fetching new proxies...")

        new_proxies = fetch_all_proxies()



        print(Fore.CYAN + "Verifying new proxies...")

        verified_new_http_proxies, _ = asyncio.run(verify_proxies(new_proxies, HTTP_TEST_URL))

        verified_new_https_proxies, _ = asyncio.run(verify_proxies(new_proxies, HTTPS_TEST_URL))



        # Combine old and new verified proxies

        all_verified_http_proxies = list(set(verified_old_http_proxies + verified_new_http_proxies))

        all_verified_https_proxies = list(set(verified_old_https_proxies + verified_new_https_proxies))



        # Update the shell's proxy list

        initial_http_proxy_count = existing_http_proxy_count

        initial_https_proxy_count = existing_https_proxy_count

        new_http_total_count = len(all_verified_http_proxies)

        new_https_total_count = len(all_verified_https_proxies)



        self.http_proxies = all_verified_http_proxies

        self.https_proxies = all_verified_https_proxies

        self.http_proxy_cycle = cycle(self.http_proxies)

        self.https_proxy_cycle = cycle(self.https_proxies)

        self.current_http_proxy = next(self.http_proxy_cycle) if self.http_proxies else None

        self.current_https_proxy = next(self.https_proxy_cycle) if self.https_proxies else None



        added_http_proxies = new_http_total_count - initial_http_proxy_count

        added_https_proxies = new_https_total_count - initial_https_proxy_count



        print(Fore.GREEN + f'\nRefreshed proxies.\n\nA change of {added_http_proxies} HTTP proxies and {added_https_proxies} HTTPS proxies after verifying all proxies. \n{len(self.http_proxies)} HTTP proxies and {len(self.https_proxies)} HTTPS proxies available after fetching and verifying in total.\n')



        # Save the working proxies to a file

        save_proxies(self.http_proxies, 'working_http_proxies.txt')

        save_proxies(self.https_proxies, 'working_https_proxies.txt')



    def do_myip(self, line):

        """Check the current public IP address using ifconfig.me."""

        protocol = 'https' if 'https' in line else 'http'

        self.switch_proxy(protocol)

        while True:

            current_proxy = self.current_https_proxy if protocol == 'https' else self.current_http_proxy

            if current_proxy:

                proxy_env = {

                    'http_proxy': f'http://{current_proxy}',

                    'https_proxy': f'http://{current_proxy}',

                    'HTTP_PROXY': f'http://{current_proxy}',

                    'HTTPS_PROXY': f'http://{current_proxy}',

                }

                try:

                    result = subprocess.run("curl --silent ifconfig.me", shell=True, capture_output=True, text=True, env={**os.environ, **proxy_env}, timeout=self.average_response_time * 1.5)

                    if result.stdout:

                        print(Fore.GREEN + f'Current public IP: {result.stdout.strip()}')

                        break

                    if result.stderr:

                        print(Fore.RED + result.stderr)

                except subprocess.TimeoutExpired:

                    print(Fore.RED + "Command timed out. Switching proxy...")

                    self.remove_proxy(current_proxy, protocol)

                    self.switch_proxy(protocol)

                except Exception as e:

                    print(Fore.RED + f'Failed to execute command: {e}.')

                    self.remove_proxy(current_proxy, protocol)

                    self.switch_proxy(protocol)

            else:

                print(Fore.RED + f'No {protocol.upper()} proxy is currently set.')

                break



    def default(self, line):

        """Run shell commands using the current proxy chain."""

        protocol = 'https' if 'https' in line else 'http'

        self.switch_proxy(protocol)

        command = line.split()[0]

        if command in DISALLOWED_COMMANDS:

            print(Fore.RED + f"Command '{command}' is not allowed (HTTP/HTTPS proxies do not support TCP commands).")

            return

        

        while True:

            current_proxy = self.current_https_proxy if protocol == 'https' else self.current_http_proxy

            if current_proxy:

                proxy_env = {

                    'http_proxy': f'http://{current_proxy}',

                    'https_proxy': f'http://{current_proxy}',

                    'HTTP_PROXY': f'http://{current_proxy}',

                    'HTTPS_PROXY': f'http://{current_proxy}',

                }

                try:

                    # Check if the command exists

                    command_exists = subprocess.run(f"command -v {command}", shell=True, capture_output=True, text=True)

                    if command_exists.returncode != 0:

                        print(Fore.RED + f"Command not found: {command}")

                        break



                    timeout = self.average_response_time * 1.5  # Use 1.5 times the average response time as timeout

                    result = subprocess.run(line, shell=True, capture_output=True, text=True, env={**os.environ, **proxy_env}, timeout=timeout)



                    if result.stdout:

                        print(result.stdout)

                        break

                    if result.stderr:

                        print(Fore.RED + result.stderr)

                        break



                except subprocess.TimeoutExpired:

                    print(Fore.RED + "Command timed out. Switching proxy...")

                    self.remove_proxy(current_proxy, protocol)

                    self.switch_proxy(protocol)

                except Exception as e:

                    print(Fore.RED + f'Failed to execute command: {e}.')

                    self.remove_proxy(current_proxy, protocol)

                    self.switch_proxy(protocol)

            else:

                print(Fore.RED + f'No {protocol.upper()} proxy is currently set.')

                break



    def remove_proxy(self, proxy, protocol='http'):

        if protocol == 'http' and proxy in self.http_proxies:

            self.http_proxies.remove(proxy)

            self.http_proxy_cycle = cycle(self.http_proxies)

            save_proxies(self.http_proxies, 'working_http_proxies.txt')  # Save updated list to file

            print(Fore.RED + f'Removed HTTP proxy: {proxy}')

        elif protocol == 'https' and proxy in self.https_proxies:

            self.https_proxies.remove(proxy)

            self.https_proxy_cycle = cycle(self.https_proxies)

            save_proxies(self.https_proxies, 'working_https_proxies.txt')  # Save updated list to file

            print(Fore.RED + f'Removed HTTPS proxy: {proxy}')



    def do_run(self, line):

        """Run a Python script using runpy."""

        script_path = line.strip()

        if not os.path.isfile(script_path):

            print(Fore.RED + f"Script {script_path} not found.")

            return

        

        protocol = 'https'

        self.switch_proxy(protocol)

        while True:

            current_proxy = self.current_https_proxy if protocol == 'https' else self.current_http_proxy

            if current_proxy:

                proxy_env = {

                    'http_proxy': f'http://{current_proxy}',

                    'https_proxy': f'http://{current_proxy}',

                    'HTTP_PROXY': f'http://{current_proxy}',

                    'HTTPS_PROXY': f'http://{current_proxy}',

                }

                try:

                    os.environ.update(proxy_env)

                    runpy.run_path(script_path, run_name="__main__")

                    break

                except Exception as e:

                    print(Fore.RED + f"Failed to run script with {protocol.UPPER()} proxy {current_proxy}: {e}")

                    self.remove_proxy(current_proxy, protocol)

                    if protocol == 'https':

                        if not self.https_proxies:

                            protocol = 'http'

                            self.switch_proxy(protocol)

                        else:

                            self.switch_proxy(protocol)

                    else:

                        print(Fore.RED + "No more proxies available.")

                        break

            else:

                print(Fore.RED + f'No {protocol.upper()} proxy is currently set.')

                break



    def do_firefox(self, line):

        """Launch Firefox with the current HTTPS proxy. Use firefox_close to close all instances of Firefox."""

        protocol = 'https'

        self.switch_proxy(protocol)

        while True:

            current_proxy = self.current_https_proxy

            if current_proxy:

                proxy_env = {

                    'http_proxy': f'http://{current_proxy}',

                    'https_proxy': f'http://{current_proxy}',

                    'HTTP_PROXY': f'http://{current_proxy}',

                    'HTTPS_PROXY': f'http://{current_proxy}',

                }

                try:

                    subprocess.Popen(['firefox'], env={**os.environ, **proxy_env}, stderr=subprocess.DEVNULL)

                    print(Fore.GREEN + 'Firefox launched.')

                    break

                except Exception as e:

                    print(Fore.RED + f'Failed to launch Firefox with {protocol.upper()} proxy {current_proxy}: {e}')

                    self.remove_proxy(current_proxy, protocol)

                    self.switch_proxy(protocol)

            else:

                print(Fore.RED + f'No {protocol.upper()} proxy is currently set.')

                break



    def do_firefox_close(self, line):

        """Close all instances of Firefox."""

        try:

            subprocess.run(['pkill', 'firefox'], stderr=subprocess.DEVNULL)

            print(Fore.GREEN + "All Firefox instances have been closed.")

        except Exception as e:

            print(Fore.RED + f"Failed to close Firefox: {e}")



    def do_scrape(self, line):

        """Scrape URLs from a provided text file and store data in CSV format."""

        file_path = line.strip()

        if not os.path.isfile(file_path):

            print(Fore.RED + f"File {file_path} not found.")

            return



        with open(file_path, 'r') as f:

            urls = [url.strip() for url in f.readlines()]



        use_different_proxies = get_valid_input("Do you want to change proxies for every URL? (yes/no): ", ['yes', 'no']) == 'yes'



        scraped_data = asyncio.run(self.scrape_urls(urls, use_different_proxies))



        # Save scraped data to a CSV file using pandas

        df = pd.DataFrame(scraped_data)

        df.to_csv('scraped_data.csv', index=False)

        print(Fore.GREEN + 'Scraped data has been saved to scraped_data.csv')



    async def scrape_urls(self, urls, use_different_proxies):

        scraped_data = []

        protocol = 'https'

        self.switch_proxy(protocol)

        async with aiohttp.ClientSession() as session:

            tasks = [self.fetch_url_with_retry(session, url, protocol, use_different_proxies) for url in urls]

            

            # Use asyncio.gather to maintain order and tqdm for progress bar

            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scraping", unit="URL"):

                result = await task

                if result:

                    scraped_data.append(result)



        return scraped_data



    async def fetch_url_with_retry(self, session, url, protocol, use_different_proxies, retries=3):

        for _ in range(retries):

            proxy = self.current_https_proxy if protocol == 'https' else self.current_http_proxy

            result = await self.fetch_url(session, url, proxy)

            if result:

                return result

            else:

                self.remove_proxy(proxy, protocol)

                self.switch_proxy(protocol)

                if use_different_proxies:

                    self.switch_proxy(protocol)  # Switch to a new proxy for the next request



        print(Fore.RED + f"Failed to fetch {url} after {retries} retries.")

        return None



    async def fetch_url(self, session, url, proxy):

        headers = {'User-Agent': random.choice(USER_AGENTS)}

        try:

            async with session.get(url, headers=headers, proxy=f'http://{proxy}', timeout=self.average_response_time * 1.5) as response:

                if response.status == 200:

                    soup = BeautifulSoup(await response.text(), 'html.parser')

                    title = soup.title.string if soup.title else "No title"

                    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

                    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]

                    tables = [table.get_text(strip=True) for table in soup.find_all('table')]

                    images = [img['src'] for img in soup.find_all('img', src=True)]

                    links = [a['href'] for a in soup.find_all('a', href=True)]



                    return {

                        'URL': url,

                        'Title': title,

                        'Headings': headings,

                        'Paragraphs': paragraphs,

                        'Tables': tables,

                        'Images': images,

                        'Links': links

                    }

                else:

                    print(Fore.RED + f"Request failed for {url}: {response.status}, {response.reason}")

        except Exception as e:

            print(Fore.RED + f"Request failed for {url}: {e}")

        return None



def fetch_proxies_from_proxynova(url):

    headers = {'User-Agent': random.choice(USER_AGENTS)}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    

    proxies = []

    proxy_table = soup.find('table', {'id': 'tbl_proxy_list'})

    if proxy_table:

        for row in proxy_table.find_all('tr'):

            columns = row.find_all('td')

            if len(columns) >= 2:

                ip_tag = columns[0].find('abbr')

                ip = ip_tag['title'] if ip_tag else None

                port = columns[1].text.strip()

                if ip and port.isdigit():

                    proxy = f'{ip}:{port}'

                    proxies.append(proxy)

    return proxies



def fetch_proxies_from_free_proxy_list(url):

    headers = {'User-Agent': random.choice(USER_AGENTS)}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')



    proxies = []

    proxy_table = soup.find('table', {'class': 'table table-striped table-bordered'})

    if proxy_table:

        for row in proxy_table.find_all('tr')[1:]:  # Skip the header row

            columns = row.find_all('td')

            if len(columns) >= 2:

                ip = columns[0].text.strip()

                port = columns[1].text.strip()

                if ip and port.isdigit():

                    proxy = f'{ip}:{port}'

                    proxies.append(proxy)

    return proxies



def fetch_all_proxies():

    urls = [

        'https://www.proxynova.com/proxy-server-list/anonymous-proxies/',

        'https://www.proxynova.com/proxy-server-list/',

        'https://free-proxy-list.net/'

    ]

    

    all_proxies = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        future_to_url = {executor.submit(fetch_proxies_from_proxynova, url): url for url in urls[:2]}

        future_to_url.update({executor.submit(fetch_proxies_from_free_proxy_list, urls[2]): urls[2]})

        

        for future in concurrent.futures.as_completed(future_to_url):

            url = future_to_url[future]

            try:

                proxies = future.result()

                all_proxies.extend(proxies)

            except Exception as e:

                print(Fore.RED + f"Error fetching proxies from {url}: {e}")

    

    return all_proxies



async def test_proxy(session, proxy, test_url):

    try:

        start_time = time.time()

        async with session.get(test_url, proxy=f'http://{proxy}', timeout=10) as response:

            if response.status == 200:

                page = await response.text()

                soup = BeautifulSoup(page, 'html.parser')

                title = soup.title.string if soup.title else "No title found"

                if title not in INVALID_TITLES:

                    end_time = time.time()

                    response_time = end_time - start_time

                    return proxy, response_time

    except Exception:

        pass

    return None, None



async def verify_proxies(proxies, test_url):

    start_time = time.time()

    print(Fore.CYAN + "Verifying proxies...")



    async with aiohttp.ClientSession() as session:

        tasks = [test_proxy(session, proxy, test_url) for proxy in proxies]

        working_proxies = []

        response_times = []



        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Verifying", unit="proxy"):

            proxy, response_time = await future

            if proxy:

                working_proxies.append(proxy)

                response_times.append(response_time)



    elapsed_time = time.time() - start_time

    print(Fore.CYAN + f"Finished verifying {len(proxies)} in {elapsed_time:.2f} seconds")



    average_response_time = sum(response_times) / len(response_times) if response_times else 5

    return working_proxies, average_response_time



def background_proxy_finder(shell):

    time.sleep(180)  # Initial delay before the first run

    while True:

        print(Fore.BLUE + "\nBackground: Fetching new proxies...\n")

        new_proxies = fetch_all_proxies()

        print(Fore.BLUE + "\nBackground: Verifying new HTTP proxies...\n")

        verified_new_http_proxies, _ = asyncio.run(verify_proxies(new_proxies, HTTP_TEST_URL))

        print(Fore.BLUE + "\nBackground: Verifying new HTTPS proxies...\n")

        verified_new_https_proxies, _ = asyncio.run(verify_proxies(new_proxies, HTTPS_TEST_URL))



        # Re-verify old proxies

        if shell.http_proxies:

            print(Fore.BLUE + "\nBackground: Re-verifying existing HTTP proxies...\n")

            verified_old_http_proxies, _ = asyncio.run(verify_proxies(shell.http_proxies, HTTP_TEST_URL))

        else:

            verified_old_http_proxies = []

        

        if shell.https_proxies:

            print(Fore.BLUE + "\nBackground: Re-verifying existing HTTPS proxies...\n")

            verified_old_https_proxies, _ = asyncio.run(verify_proxies(shell.https_proxies, HTTPS_TEST_URL))

        else:

            verified_old_https_proxies = []



        # Combine old and new verified proxies

        all_verified_http_proxies = list(set(verified_new_http_proxies + verified_old_http_proxies))

        all_verified_https_proxies = list(set(verified_new_https_proxies + verified_old_https_proxies))



        # Update the shell's proxy list

        initial_http_proxy_count = len(shell.http_proxies)

        initial_https_proxy_count = len(shell.https_proxies)

        shell.http_proxies = all_verified_http_proxies

        shell.https_proxies = all_verified_https_proxies

        shell.http_proxy_cycle = cycle(shell.http_proxies)

        shell.https_proxy_cycle = cycle(shell.https_proxies)

        shell.current_http_proxy = next(shell.http_proxy_cycle) if shell.http_proxies else None

        shell.current_https_proxy = next(shell.https_proxy_cycle) if shell.https_proxies else None



        new_http_total_count = len(shell.http_proxies)

        new_https_total_count = len(shell.https_proxies)

        added_http_proxies = new_http_total_count - initial_http_proxy_count

        added_https_proxies = new_https_total_count - initial_https_proxy_count



        print(Fore.GREEN + f'\nRefreshed proxies.\n\nA change of {added_http_proxies} HTTP proxies and {added_https_proxies} HTTPS proxies after verifying all proxies. \n{new_http_total_count} HTTP proxies and {new_https_total_count} HTTPS proxies available after fetching and verifying in total.\n')



        # Save the working proxies to a file

        save_proxies(shell.http_proxies, 'working_http_proxies.txt')

        save_proxies(shell.https_proxies, 'working_https_proxies.txt')



        # Refresh the prompt

        print(Fore.CYAN + '\nproxyshell> ', end='')



        time.sleep(180)  # Fetch new proxies every 3 minutes



def get_valid_input(prompt, valid_responses):

    while True:

        response = input(prompt).strip().lower()

        if response in valid_responses:

            return response

        print(Fore.RED + f"Invalid response. Please enter one of: {', '.join(valid_responses)}")



def save_proxies(proxies, filename='working_proxies.txt'):

    with open(filename, 'w') as f:

        for proxy in proxies:

            f.write(f"{proxy}\n")

    print(Fore.GREEN + f'Saved {len(proxies)} working proxies to {filename} \n')



def read_proxies(filename='working_proxies.txt'):

    if os.path.isfile(filename):

        with open(filename, 'r') as f:

            return [line.strip() for line in f.readlines()]

    return []



def main():

    print(Fore.CYAN + "Proxyshell by @thetrueartist")

    print(Style.BRIGHT + "Fetching proxies...")



    http_proxies = read_proxies('working_http_proxies.txt')  # Read existing HTTP proxies from file

    https_proxies = read_proxies('working_https_proxies.txt')  # Read existing HTTPS proxies from file

    new_proxies = fetch_all_proxies()  # Fetch new proxies

    

    print(Fore.GREEN + f'Found {len(new_proxies)} proxies')



    print(Style.BRIGHT + "Testing HTTP proxies...")

    start_time = time.time()

    working_http_proxies, average_http_response_time = asyncio.run(verify_proxies(new_proxies, HTTP_TEST_URL))

    elapsed_time = time.time() - start_time

    print(Fore.CYAN + f"Finished testing {len(new_proxies)} HTTP proxies in {elapsed_time:.2f} seconds")



    print(Style.BRIGHT + "Testing HTTPS proxies...")

    start_time = time.time()

    working_https_proxies, average_https_response_time = asyncio.run(verify_proxies(new_proxies, HTTPS_TEST_URL))

    elapsed_time = time.time() - start_time

    print(Fore.CYAN + f"Finished testing {len(new_proxies)} HTTPS proxies in {elapsed_time:.2f} seconds")



    print(Fore.GREEN + f'Working HTTP proxies: {working_http_proxies}')

    print(Fore.GREEN + f'Working HTTPS proxies: {working_https_proxies}\n')

    save_proxies(working_http_proxies, 'working_http_proxies.txt')

    save_proxies(working_https_proxies, 'working_https_proxies.txt')



    use_proxies = get_valid_input("Do you want to use these proxies? (yes/no): ", ['yes', 'no'])

    if (use_proxies != 'yes'):

        return



    # Start the proxy shell

    shell = ProxyShell()

    shell.http_proxies = working_http_proxies

    shell.https_proxies = working_https_proxies

    shell.average_response_time = (average_http_response_time + average_https_response_time) / 2

    os.system('clear')

    

    # Start the background proxy finder thread

    threading.Thread(target=background_proxy_finder, args=(shell,), daemon=True).start()



    shell.cmdloop()



if __name__ == '__main__':

    main()
