import tkinter
import re
import os
import argparse
import pathlib
import json
import urllib
import urllib.request

# Regular Expressions for retrieving contents from page source code.
PHOTOS_EXPRESSION = r'"display_resources":(.*?)]'
VIDEO_EXPRESSION = r'"video_url":"(.*?)"'
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
    with urllib.request.urlopen(url, timeout=5) as response:
        source = response.read()
    source = str(source)

    return source

def find_username(page_source):
    content = re.search(CONTENT_EXPRESSION, page_source).group(0)
    username = re.search(USERNAME_EXPRESSION, content).group(0)[1:-1]

    return username

def download_photos(url, path):
    # Downloads posted photo or photos to specified path or where does this script exists then opens it.
    page_source = get_page_source(url)

    username = find_username(page_source)
    display_resources = re.findall(PHOTOS_EXPRESSION, page_source) # find all display resources
    display_resources = [json.loads("{}]".format(resource)) for resource in display_resources] # Close the bracket and turn str to list with json.loads
    img_urls = [sorted(resource, key=lambda x: x.get('config_width'), reverse=True)[0]['src'] for resource in display_resources] # Get only highest resolution url for images
    img_urls = dict.fromkeys(img_urls).keys() # Remove occurence but keep order. # set() not used because it is disorders the list.
    for i, url in enumerate(img_urls, start=1):
        try:
            decoded_url = urllib.parse.unquote(url.replace('\\\\', '\\')).encode().decode('unicode_escape') # Decode special characters such as \u0026 => &
            with urllib.request.urlopen(decoded_url, timeout=5) as response:
                page_source = response.read()
        except urllib.error.HTTPError as err:
            if err.code == 403:
                # Sometimes urllib.parse.unquote distores the url so we try without it.
                decoded_url = url.replace('\\\\','\\').encode().decode('unicode_escape')
                with urllib.request.urlopen(decoded_url, timeout=5) as response:
                    page_source = response.read()
        with open(str(pathlib.PurePath(path, '{}_photo_{}.jpeg'.format(username, i))), 'wb') as img_file:
            img_file.write(page_source)

    if pathlib.Path(pathlib.PurePath(path, '{}_photo_1.jpeg'.format(username))).exists():
        # Open the first downloaded photo
        os.startfile(str(pathlib.PurePath(path, '{}_photo_1.jpeg'.format(username)))) # Open the first image.
    else:
        raise FileNotFoundError

def download_video(url, path):
    # Downloads posted videos to specified path or where does this script exists.
    # Then opens it.
    # Note : It's also downloads video thumbnail as photo too.
    page_source = get_page_source(url)

    username = find_username(page_source)
    video_urls = re.findall(VIDEO_EXPRESSION, page_source)
    for i, url in enumerate(video_urls, start=1):
        print("Downloading {}. video".format(i))
        try:
            decoded_url = urllib.parse.unquote(url.replace('\\\\', '\\')).encode().decode('unicode_escape') # Decode special characters such as \u0026 => &
            urllib.request.urlretrieve(decoded_url, str(pathlib.PurePath(path, '{}_video_{}.mp4'.format(username, i))))
        except urllib.error.HTTPError as err:
            if err.code == 403:
                # Sometimes urllib.parse.unquote distores the url so we try without it.
                decoded_url = url.replace('\\\\','\\').encode().decode('unicode_escape')
                urllib.request.urlretrieve(decoded_url, str(pathlib.PurePath(path, '{}_video_{}.mp4'.format(username, i))))

    if pathlib.Path(pathlib.PurePath(path, '{}_video_1.mp4'.format(username))).exists():
        # Open the first downloaded video.
        os.startfile(str(pathlib.PurePath(path, '{}_video_1.mp4'.format(username)))) # Open the first video
    else:
        raise FileNotFoundError

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
    except FileNotFoundError:
        print("This post doesn't contain video. The photo will be checked.")
    except Exception as err:
        # For not handling the whole exceptions one by one
        # I just print the exception and leave the issue to user of this script.
        # e.g : wrong website, not correct url etc.
        print(err)
        print("Something goes wrong, please check your url again.")

    try:
        download_photos(url, path)
    except FileNotFoundError:
        print("This post doesn't contain photo. Check your url please.")
    except Exception as err:
        print(err)
        print("Something goes wrong, please check your url again.")
        