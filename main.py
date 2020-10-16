import json
import requests


def count_user_commits(user):
    r = requests.get('https://api.github.com/users/%s/repos' % user)
    repos = json.loads(r.content)
    #print(repos)

    for repo in repos:
        if repo['fork'] is True:
            # skip it
            continue
        n = count_repo_commits(repo['url'] + '/commits')
        #print (repo['url']+ '/commits')
        repo['num_commits'] = n
        yield repo


def count_repo_commits(commits_url, _acc=0):
    r = requests.get(commits_url)
    #print (json.loads(r.content))
    parsejson(r.content)
    commits = json.loads(r.content)
    
    n = len(commits)
    if n == 0:
        return _acc
    link = r.headers.get('link')
    if link is None:
        return _acc + n
    next_url = find_next(r.headers['link'])
    if next_url is None:
        return _acc + n
    # try to be tail recursive, even when it doesn't matter in CPython
    return count_repo_commits(next_url, _acc + n)
#writing method to parse json 
def parsejson(jsoncontent):
  json_object =json.loads (jsoncontent)
  print (json_object[0]['commit'])
  

# given a link header from github, find the link for the next url which they use for pagination
def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


if __name__ == '__main__':
    import sys
    user='schamarthy'
    #authtoken='b7116dccbbb3777697ad701f3960954a0290ff5a'
    #print (user)
    total = 0
    for repo in count_user_commits(user):
        print ("Repo `%(name)s` has %(num_commits)d commits, size %(size)d." % repo)
        total += repo['num_commits']
    print ("Total commits: %d" % total)