# Instagram Downloader

This is a simple script for downloading instagram posts.

## Installing

- The script has no dependencies.

- Make sure you have python 3 installed and the python path added to system environment variables. I tested the script on python 3.7.

- After that click the green button that says "Clone or download" on the project github page. You can clone the project if you know how to use git or just simply click "Download ZIP" button.

## Usage

- Navigate the downloaded folder on the command line.

- Then copy(ctrl + c) the instagram post url that you want to download.

Type:
```shell
instagram_downloader.py
```

- Or if you want to specify the path where you want to download.

Example:
```shell
instagram_downloader.py -p C:/Users/{Username}/Desktop
```

## Note!

The script depends on the page source code. So if Instagram decides to change their tag names this script will not work until the regular expressions updated.

## Disclaimer

This is an unofficial work, use at your own risk.

## License

Unlicensed aka Public Domain.