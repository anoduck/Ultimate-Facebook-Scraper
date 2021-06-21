```html
<!--
#-----------------------------------------------------------#
#  _   _ ___ ___    ___               _   _  __ _        _  #
# | | | | __/ __|  / _ \ _  _ __ _ __| |_(_)/ _(_)___ __| | #
# | |_| | _|\__ \ | (_) | || / _` / _| / / |  _| / -_) _` | #
#  \___/|_| |___/  \__\_\\_,_\__,_\__|_\_\_|_| |_\___\__,_| #
#                                                           #
#-----------------------------------------------------------#
-->
```

## UFS Scraper: Quackified Edition  

----

*This repository is no longer compatible with the original UFS scraper written by harismuneer.*

*The original repository for UFS created by harismuneer is empty and the code is now closed source*

*HarisMuneer still provides access to his source code for payment.*

*We support keeping code Open Source.*

----

### New Changes to come
Since the last update of this repo the developer has removed the script from github and closed the source code. He now requires payment for access to this script. 

#### What this means for the future of this script?
Unfortunately, the book of face has changed it's design and nearly all of the references that were used to scrape profiles are no longer present, many once important sections have now been completely removed. Many things the script once scraped were never used and were completely unneeded. For now the script is primarly focues on scraping a user's images, their friends, and their friend's images. 

### Open for suggested features

If you would like this script to scrape other parts of the profile than images, please fill out a feature request by opening an issue in the issues tab of this repository. The process of scraping other parts of a user's profile is relatively the same as scraping a user's images, so features can be added if desired.

### Features

A bot which scrapes a profiles for images:

- All user photos
- All Photo Albums
- Friends of user
- filters list of friends by gender
- scrapes all the photos and photo albums of friends
- Prevention of getting banned by the book of facey face.

### Notable Changes

#### Guess what? Zuckerberg still hates you.

There is little doubt that the zuckerberg hates anyone who attempts to scrape data from the book of faceness. So, by using this script strictly for educational purposes, you will not recieve a christmas card from the zuckerberg, and there is the potential that you will either be blocked from usage or temporarily suspended for it's use. 

#### Chromedriver is no more

For some undiscovered reason chromedriver stopped working locally and it was already desired to move the project from chrome to firefox. So chrome has been axed from the project and in it's place is geckodriver. So, you will need gecko driver to successfully run this script.

#### Geckodriver executable '/usr/local/bin': !IMPORTANT STUFF!

Since we have moved from chrome driver to geckodriver the location of geckodriver needs to remain consistent if you desire to run this program. In my distrobution geckodriver is located in `/usr/local/bin`, yours needs to be the same to successfully execute.

#### No Longer run scraper, but photo-scraper: !Also Uber Important!

In order to maintain a copy of the original script, I created a new script and have made all my modifications to it. It is photo-scraper.py, and it is what you will need to run for the forseeable future. So remember this, it is not `python3 scraper.py`, but is `python3 photo-scraper.py`. 

### Running the script

1. Perform a shallow clone of the repo, like a boss!

```bash
 git clone --depth=1 https://www.github.com/anoduck/UFS-Quackified
```

2. Download the geckodriver

3. Install all the necessary requirements with pip

```bash
sudo pip3 install -r requirements.txt
```

4. Change Directory to the repo you just cloned and copy `input.txt.example` to `scraper/input.txt` and copy `credentials.yml.example` to `scraper/credentials.yml`. Then open up those files making desired changes.

```bash
cd to/the/repository/UFS-Quackified
cp input.txt.example scraper/input.txt
cp credentials.yml.example scraper/credentials.yml
cd scraper
nvim input.txt
# Add usernames to scrape
nvim credentials.yml
# Enter credential information
```

5. You are ready to scrape, so strap on your seatbelt and launch the script.

```bash
python3 photo-scraper.py
```

6. Watch it scrape away for a few, then you might want to go to a movie or something.

7. If for some reason you discover that your profile has been blocked for using this script or a feature on facebook has been disabled preventing you from successfully completing the scrape. Please submit a new issue to this repository so that we may make concessions and corrections to prevent this from further occurring again.

### Tips and Tricks (but no treats)...

There are a few things that are recommended in order to encourage successful scraping and avoid being blocked or having a feature temporarily disabled on your account. They are:

1. Do not fiddle with the website inside of the chromedriver window while the script is running.

2. Do not open up another browser and visit the book of face-ness while the script is running.

3. Avoid using the book of facey face on your mobile device while the script is running.

5. Attempt to scrape a single profile at a time until you have full knowledge that the script will not result in your profile being blocked and you are comfortable running the script.

6. Since currently, the script will not exit on being notified that your account has been blocked, do keep an eye on the scraping process from time to time. If ever you are notified that your account has been blocked, exit the script immediately.

### License, Copyright, and ClarificationAnd the original repository for UFS created by harismuneer is empty.

This script was originally written by Haris Muneer and associates, but what remains of the original work is less than ten percent of the original code base, the remaining 90% was written by yours truly. This was done before the license to the code was changed unknowingly from being open source to closed source. The remaining portions of the original code base is from the open source version and not the closed. Being in such state, this repository is free from all and any claims made upon it by the previous authors, and will be placed under the MIT license. 

```txt
# Copyright (c) 2021 anoduck

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
 #
```
