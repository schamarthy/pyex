import json
import requests
import csv


def count_user_commits(gh_session,user):
    #repos_url = 'https://api.github.com/user/repos'
    r = gh_session.get('https://api.github.com/users/%s/repos' % user)
    repos = json.loads(r.content)
    file = open('commitDates.csv', 'w+', newline='\n')
    
   # print(repos)
    for repo in repos:
        if repo['fork'] is True:
            # skip it
            continue
        n = count_repo_commits(gh_session,repo['url'] + '/commits')
        #print (repo['url']+ '/commits')
        repo['num_commits'] = n
        yield repo


def count_repo_commits(gh_session,commits_url, _acc=0):
    r = gh_session.get(commits_url)
    #print (json.loads(r.content))
    print ("Dates for repo")
    commitDate=parsejson(r.content)
    print (commitDate, "\n")
    file = open('commitDates.csv', 'a+', newline='\n') 
  
  # writing the data into the file 
    with file:     
        write = csv.writer(file) 
        write.writerows(commitDate) 

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
#writing method to parse json and write to csv file
def parsejson(jsoncontent):
    json_object =json.loads (jsoncontent)
    commitDate=[]
    for key in json_object:
      #print ("inside for parsejson")
      
      commitDate.append(key['commit']['author']['date'])

    return commitDate
  

# given a link header from github, find the link for the next url which they use for pagination
def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


if __name__ == '__main__':
    import sys
    username='schamarthy'
    authtoken='b628609a7e4717ce95f6ab2132e28b8fc96e797f'
    # create a re-usable session object with the user creds in-built
    gh_session = requests.Session()
    gh_session.auth = (username, authtoken)
    
    #print (user)
    total = 0
    for repo in count_user_commits(gh_session,username):
        print ("Repo `%(name)s` has %(num_commits)d commits, size %(size)d." % repo)
        total += repo['num_commits']
    print ("Total commits: %d" % total)