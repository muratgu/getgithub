import requests as http
import BeautifulSoup as soup
import os
import sys
import argparse
import zipfile
import time


class GitHubArchive:
    '''
    Walk the tree of a GitHub url
    Download a GitHub file
    '''
    def __init__(self, github_url):
        self.github_url = github_url
        self.GITHUB_ROOT = 'https://github.com'    
        self.RAW_ROOT = 'https://raw.githubusercontent.com'
        self.DIR_CLASS = 'js-directory-link'

       
    def walk(self, url):
        '''
        Traverse the GitHub url
        Generate ['dir|file', url] for all tree nodes
        '''
        yield ['dir', url.replace('/tree/','/').replace(self.GITHUB_ROOT,'')]
        page = soup.BeautifulSoup(http.get(url).content)
        for link in [x['href'] for x in page.findAll('a', {'class': self.DIR_CLASS})]:
            if '/tree/' in link:
                for x in self.walk(self.GITHUB_ROOT+link):
                    yield x
            elif '/blob/' in link:
                yield ['file', link.replace('/blob/', '/')] 
            

    def save_to_zip(self, quiet = False):
        zfn = os.path.basename(self.github_url)+str(int(time.time()))+'.zip'       
        num_dirs, num_files = 0, 0
        with zipfile.ZipFile(zfn, 'w') as zf:
            zf.debug = 3
            for x in self.walk(self.github_url):
                if not quiet: 
                        print x[1]
                if x[0] == 'dir':
                    num_dirs += 1
                if x[0] == 'file':
                    bytes = http.get(self.RAW_ROOT+x[1]).content
                    zf.writestr(x[1].strip('/'), bytes)
                    num_files += 1                
            zf.close()
        if not quiet:
            print '%d file(s) in %d folders archived in %s' % (num_files, num_dirs, zfn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads zip archive of an arbitrary GitHub folder')
    parser.add_argument('url', help='url of GitHub folder')
    parser.add_argument('-q', '--quiet', action='store_true', help='verbose')
    args = parser.parse_args()
    if args.url:
        GitHubArchive(args.url).save_to_zip(quiet=args.quiet)