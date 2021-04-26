#!/usr/bin/env python3

import os
import sys
import pprint
import tempfile
import logging
import re
from bs4 import BeautifulSoup
import shutil

class Dir:

    path = None
    htmls=[]
    
    def __init__(self, path, htmls, imgs='.', check_imgs=True):
        self.path = os.fspath(path)
        self.htmls = [os.path.normpath(os.path.join(self.path, os.fspath(f))) for f in htmls]
        self.new_imgs_relpath=imgs
        self.check_imgs = check_imgs


def do_directory(dir_obj):
    logging.info('directory \'%s\'' % dir_obj.path)
    for fname in dir_obj.htmls:
        logging.info('file \'%s\'' % fname)
        with tempfile.NamedTemporaryFile(delete=True, dir=dir_obj.path,  suffix='.html') as ofp:
            logging.debug('Temporary file created: \'%s\'' % ofp.name)
            with open(fname) as ifp:
                process_htmlfile(ifp, ofp, dir_obj)
                ifp.close()
                ofp.flush()
                shutil.copy2(ofp.name, ifp.name)

            

def process_htmlfile(ifp, ofp, dir_obj):

    img_re = re.compile('^https?://web.archive.org/web/(\d+)im_/https?://((?:[^/]*/)*)([^/]*)',re.IGNORECASE)
    pp = pprint.PrettyPrinter(indent=4, depth=4)

    
    soup = BeautifulSoup(ifp, 'html.parser')
    logging.debug("Parsed %s" % (ifp.name))
    images = soup.find_all('img')

    #logging.debug("Images:\n" + pprint.pformat(images))
    for img in images:
        try:
            src=img.attrs['src']
            m = img_re.match(src)
            if m:
                newsrc = dir_obj.new_imgs_relpath + '/' + m.groups()[2]
                img.attrs['src']=newsrc

                logging.debug("%s match %s -> %s" % (src, m.groups(), newsrc))

            else:
                logging.debug("img src does not match wayback machine regex: '%s'" % src)
                        
        except KeyError:
            print("Woah, things went weird in '%s'" % repr(img))

    soup.smooth()
    #print(str(soup)) #.prettify(formatter="html"))
    ofp.write(soup.encode())
    ofp.flush()
    
    




TODO = [Dir('2008/myspace.com/ameya', ['index.html'])]
    
def main():
    logging.basicConfig(level=logging.INFO)
    pp = pprint.PrettyPrinter(indent=4, depth=4)
    pp.pprint(TODO[0].htmls)

    for dir in TODO:
        do_directory(dir)
    
        
if __name__ == "__main__":
    sys.exit(main())


