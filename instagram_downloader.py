import tkinter
import re
import os
import argparse
import pathlib
import html
from urllib.request import urlopen, urlretrieve

# Regular Expressions for retrieving data from page source code.
PHOTO_EXPRESSION = r'<meta property="og:image" content="(.*?)" />'
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

def download_photo(url, path):
    # Downloads posted photo to specified path or where does this script exists.
    # Then opens it.
    page_source = get_page_source(url)

    content = re.search(CONTENT_EXPRESSION, page_source).group(0)
    username = re.search(USERNAME_EXPRESSION, content).group(0)[1:-1]
    image_url = re.search(PHOTO_EXPRESSION, page_source).group(1)
    image_url = html.unescape(image_url) # Decodes special characters
    if path:
        save_path = str(pathlib.PurePath(path, '{}_photo.jpeg'.format(username)))
    else:
        save_path = '{}_photo.jpeg'.format(username)

    with urlopen(image_url, timeout=5) as response:
        page_source = response.read()
    print("Download starting...")
    with open(save_path, 'wb') as img_file:
        img_file.write(page_source)

    os.startfile(save_path)

def download_video(url, path):
    # Downloads posted video to specified path or where does this script exists.
    # Then opens it.
    page_source = get_page_source(url)

    content = re.search(CONTENT_EXPRESSION, page_source).group(0)
    username = re.search(USERNAME_EXPRESSION, content).group(0)[1:-1]
    video_url = re.search(VIDEO_EXPRESSION, page_source).group(1)
    video_url = html.unescape(video_url) # Decodes special characters
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
        download_photo(url, path)
    except AttributeError:
        print("This post doesn't contain photo. Check your url please.")
    except Exception as err:
        print(err)
        print("Something goes wrong, please check your url again.")
        