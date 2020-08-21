import tkinter
import re
import os
import argparse
import pathlib
import json
import urllib
from urllib.request import urlopen, urlretrieve

# Regular Expressions for retrieving data from page source code.
PHOTOS_EXPRESSION = r'"display_resources":(.*?)]'
VIDEO_EXPRESSION = r'<meta property="og:video" content="(.*?)" />'
CONTENT_EXPRESSION = r'<meta content="(.*?)"' # Needed for username
USERNAME_EXPRESSION = r'\@.*?(\s|\))'

def clipboard_text():
    # Returns last copied text.
    tk = tkinter.Tk()
    tk.withdraw()
    try:
        clipboard_text = tk.clipboard_get()
    except tkinter.TclError:
        clipboard_text = ""

    return clipboard_text

def get_page_source(url):
    # Returns page source code as a string.
    with urlopen(url, timeout=5) as response:
        source = response.read()
    source = str(source)

    return source

def download_photos(url, path):
    # Downloads posted photo or photos to specified path or where does this script exists.
    # Then opens it.
    page_source = get_page_source(url)

    content = re.search(CONTENT_EXPRESSION, page_source).group(0)
    username = re.search(USERNAME_EXPRESSION, content).group(0)[1:-1]
    display_resources = re.findall(PHOTOS_EXPRESSION, page_source) # find all display resources
    display_resources = [json.loads("{}]".format(resource)) for resource in display_resources] # Close bracket and turn str to list with json.loads
    img_urls = [sorted(resource, key=lambda x: x.get('config_width'), reverse=True)[0]['src'] for resource in display_resources] # Get only highest resolution url for images
    img_urls = [urllib.parse.unquote(url).encode().decode('unicode_escape') for url in img_urls] # Decode special characters such as \u0026 => &
    img_urls = dict.fromkeys(img_urls).keys() # Remove occurence but keep order. # set() not used because it is disorders the list.
    for i, url in enumerate(img_urls, start=1):
        with urlopen(url, timeout=5) as response:
            page_source = response.read()
        with open(str(pathlib.PurePath(path, '{}_photo_{}.jpeg'.format(username, i))), 'wb') as img_file:
            img_file.write(page_source)

    os.startfile(str(pathlib.PurePath(path, '{}_photo_1.jpeg'.format(username)))) # Open first image.

def download_video(url, path):
    # Downloads posted video to specified path or where does this script exists.
    # Then opens it.
    # Note : It's also downloads video thumbnail as photo too.
    page_source = get_page_source(url)

    content = re.search(CONTENT_EXPRESSION, page_source).group(0)
    username = re.search(USERNAME_EXPRESSION, content).group(0)[1:-1]
    video_url = re.search(VIDEO_EXPRESSION, page_source).group(1)
    video_url = urllib.parse.unquote(video_url).encode().decode('unicode_escape') # Decode special characters such as \u0026 => &
    if path:
        save_path = str(pathlib.PurePath(path, '{}_video.mp4'.format(username)))
    else:
        save_path = '{}_video.mp4'.format(username)

    print("Download starting...")
    urlretrieve(video_url, save_path)

    os.startfile(save_path)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(conflict_handler="resolve")
    arg_parser.add_argument('-u', '--url',
                            nargs='?',
                            default=clipboard_text(),
                            type=str,
                            help="Instagram post url address, default gets url from clipboard")
    arg_parser.add_argument('-p', '--path',
                            nargs='?',
                            default="",
                            type=str,
                            help="Saving path, default saves to where does this script exists")
    args = arg_parser.parse_args()

    url = args.url
    path = args.path

    try:
        download_video(url, path)
    except AttributeError:
        print("This post doesn't contain video. The photo will be checked.")
    except Exception as err:
        # For not handling the whole exceptions one by one
        # I just print the exception and leave the issue to user of this script.
        # e.g : HTTP 403, wrong website, non url etc.
        print(err)
        print("Something goes wrong, please check your url again.")

    try:
        download_photos(url, path)
    except AttributeError:
        print("This post doesn't contain photo. Check your url please.")
    except Exception as err:
        print(err)
        print("Something goes wrong, please check your url again.")
        