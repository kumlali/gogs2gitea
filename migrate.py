import argparse
import base64
import json
import os
import subprocess
import urllib
import urllib2

arg_src_url = ''
arg_src_token = ''
arg_dst_url = ''
arg_dst_token = ''
arg_dst_owner_user = ''

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src_url', 
                        help='URL of source Gogs/Gitea (e.g. http://gogs.mycompany.com)',
                        required=True)
    parser.add_argument('--src_token', 
                        help='Access token of user that owns the repositories on source Gogs/Gitea',
                        required=True)
    parser.add_argument('--dst_url', 
                        help='URL of destination Gogs/Gitea (e.g. http://gitea.mycompany.com)',
                        required=True)
    parser.add_argument('--dst_token', 
                        help='Access token of user that owns the repositories on destination Gogs/Gitea',
                        required=True)
    parser.add_argument('--dst_owner_user', 
                        help='Owner of all the organizations on destination Gogs/Gitea',
                        required=True)

    args = parser.parse_args()

    global arg_src_url
    global arg_src_token
    global arg_dst_url
    global arg_dst_token
    global arg_dst_owner_user
    arg_src_url = args.src_url
    arg_src_token = args.src_token
    arg_dst_url = args.dst_url
    arg_dst_token = args.dst_token
    arg_dst_owner_user = args.dst_owner_user

def get(url, params, token):
    request = urllib2.Request(url + "?" + urllib.urlencode(params))
    request.add_header("Content-Type",'application/json')
    request.add_header("Authorization", 'token ' + token)
    return json.load(urllib2.urlopen(request))

def post(url, params, token):
    request = urllib2.Request(url, data=json.dumps(params))
    print json.dumps(params)
    request.add_header("Content-Type",'application/json')
    request.add_header("Authorization", 'token ' + token)
    return urllib2.urlopen(request)

def delete(url, token):
    request = urllib2.Request(url)
    request.add_header("Content-Type",'application/json')
    request.add_header("Authorization", 'token ' + token)
    request.get_method = lambda: 'DELETE'
    return urllib2.urlopen(request)

# http://gogs.mycompany.com -> http://gogs.mycompany.com/api/v1
def get_api_url(url):
    return url + '/api/v1'

# http(s)://gogs.mycompany.com -> http(s)://<token>@gogs.mycompany.com
def get_token_inserted_url(url, token):
    first = url.split('/')[0] + '//'
    last = '@' + url.split('/')[2]
    return first + token + last

"""
Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/orgs/<orgname>
"""
def get_org(url, token, org):
    try:
       return get(get_api_url(url) + '/orgs/' + org, '', token)   
    except urllib2.HTTPError as err:
       if err.code == 404:
           return ''
       else:
           raise

"""
Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/user/orgs
"""
def get_orgs(url, token):
    return get(get_api_url(url) + '/user/orgs', '', token)

"""
Equivalent to:
    curl -v -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       -d "{\"username\": \"NewOrg\", \"full_name\": \"NewOrg_Full_Name\",\"description\": \"NewOrg was created by using curl.\",\"website\": \"https://neworg.io\", \"location\": \"TR\"}" \
        http://gogs.mycompany.com/api/v1/admin/users/<owner_user_of_NewOrg>/orgs
"""
def create_org(url, token, owner_user, org, full_name='', description='', website='', location=''):
    print 'Organization will be created -> On Git server: ' + url + ', Owner user: ' + owner_user + ', Organization: ' + org
    if get_org(url, token, org) != '':
        raise Exception('Organization [' + org + '] already exists on ' + url) 
    post(get_api_url(url) + '/admin/users/' + owner_user + '/orgs', {'username': org, 
                                                                        'full_name': full_name, 
                                                                        'description': description, 
                                                                        'website': website, 
                                                                        'location': location}, token)
    print 'Organization has been created -> On Git server: ' + url + ', Owner user: ' + owner_user + ', Organization: ' + org

"""
Copies given org on source server to destination server. Repositories 
are not copied.

Because /orgs/<orgname> (and get_org() accordingly) does not return 
the owner, we need to know it while creating the organization on 
destination server. That is why we need dst_owner_user.
"""
def copy_org(src_url, src_token, dst_url, dst_token, dst_owner_user, org):
    print 'Organization migration has been started -> From:' + src_url + ' To: ' + dst_url + ' Destination owner user: ' + dst_owner_user + ' Organization: ' + org

    orgJson = get_org(src_url, src_token, org)
    if orgJson == '':
        raise Exception('Organization [' + org + '] does not exist on ' + src_url)

    print 'Organization: '
    print '    Name: ' + orgJson['username'].encode('utf-8')
    print '    Full name: ' + orgJson['full_name'].encode('utf-8')
    print '    Description: ' + orgJson['description'].encode('utf-8')
    print '    Website: ' + orgJson['website'].encode('utf-8')
    print '    Location: ' + orgJson['location'].encode('utf-8')
    print '    Avatar URL: ' + orgJson['avatar_url'].encode('utf-8')

    create_org(dst_url, 
               dst_token, 
               dst_owner_user, 
               orgJson['username'].encode('utf-8'), 
               orgJson['full_name'].encode('utf-8'), 
               orgJson['description'].encode('utf-8'), 
               orgJson['website'].encode('utf-8'), 
               orgJson['location'].encode('utf-8'))

    print 'Organization migration has been completed -> From:' + src_url + ' To: ' + dst_url + ' Destination owner user: ' + dst_owner_user + ' Organization: ' + org

"""
Copies all the organizations on source server to destination server.

Repositories are not copied.

Because /orgs/<orgname> (and get_org() accordingly) does not return 
the owner, we need to know it while creating the organization on 
destination server. That is why we need dst_owner_user.
"""
def copy_orgs(src_url, src_token, dst_url, dst_token, dst_owner_user):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        copy_org(src_url, src_token, dst_url, dst_token, dst_owner_user, orgName)

"""
Returns given repository of given owner. Owner can either be an organization or
a user.

Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/repos/MyOrgOrUser/MyRepo
"""
def get_repo(url, token, owner, repo):
    try:
       return get(get_api_url(url) + '/repos/' + owner + '/' + repo, '', token)
    except urllib2.HTTPError as err:
       if err.code == 404:
           return ''
       else:
           raise

"""
Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/orgs/MyOrg/repos
"""
def get_repos(url, token, org):
    return get(get_api_url(url) + '/orgs/' + org + '/repos', '', token)

"""
Returns repositories of given user.

Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/users/MyUser/repos
"""
def get_user_repos(url, token, user):
    return get(get_api_url(url) + '/users/' + user + '/repos', '', token)

"""
Creates given repository under given organization.

Equivalent to:
    curl -v -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       -d '{"name":"MyRepo"}' \
       http://gitea.mycompany.com/api/v1/org/MyOrg/repos
"""
def create_repo(url, token, org, repo):
    print 'Repository will be created -> On Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo
    if get_org(url, token, org) == '':
        raise Exception('Organization [' + org + '] does not exist on ' + url) 
    if get_repo(url, token, org, repo) != '':
        raise Exception('Repository [' + repo + '] of organization [' + org + '] already exists on ' + url)
    post(get_api_url(url) + '/org/' + org + '/repos', {'name': repo}, token)
    print 'Repository has been created -> On Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo

"""
Creates repository for authenticated user whose token is used.

Equivalent to:
    curl -v -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       -d '{"name":"MyUserRepo"}' \
       http://gitea.mycompany.com/api/v1/user/repos
"""
def create_user_repo(url, token, user, repo):
    print 'User repository will be created -> On Git server: ' + url + ', Authenticated User, Repository: ' + repo
    if get_repo(url, token, user, repo) != '':
        raise Exception('Repository [' + repo + '] of user [' + user + '] already exists on ' + url)
    post(get_api_url(url) + '/user/repos', {'name': repo}, token)
    print 'User repository has been created -> On Git server: ' + url + ', Authenticated User, Repository: ' + repo

"""
Equivalent to:
    curl -v -X DELETE \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gitea.mycompany.com/api/v1/repos/MyOrg/MyRepo 
"""
def delete_repo(url, token, org, repo):
    print 'Repository will be deleted -> From Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo
    if get_org(url, token, org) == '':
        raise Exception('Organization [' + org + '] does not exist on ' + url) 
    if get_repo(url, token, org, repo) == '':
        print 'Repository [' + repo + '] of organization [' + org + '] does not exist on ' + url
    else:
        delete(get_api_url(url) + '/repos/' + org + '/' + repo, token)
        print 'Repository has been deleted -> From Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo

"""
Deletes all repositories of given organization.
"""
def delete_repos(url, token, org):
    repos = get_repos(url, token, org)
    for repo in repos:
        repoName = repo['name']
        delete_repo(url, token, org, repoName)

"""
Deletes all repositories of each organization.
"""
def delete_repos(url, token):
    orgs = get_orgs(url, token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(url, token, orgName)
        for repo in repos:
            repoName = repo['name']
            delete_repo(url, token, orgName, repoName)

"""
Creates organization repositories of source server under the same organization 
of destination server. It does not copy the content of the repositories(See 
copy_repos()) 
"""
def create_repos(src_url, src_token, dst_url, dst_token):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(src_url, src_token, orgName)
        for repo in repos:
            repoName = repo['name']
            create_repo(dst_url, dst_token, orgName, repoName)

"""
Migrates repository of an owner(organizaton or user) on source server under to 
an owner on destination server.

Equivalent to:
    $ git -c http.sslVerify=false clone --bare http://<token>@gogs.mycompany.com/src_owner/MyRepo.git
    $ cd MyRepo.git
    $ git -c http.sslVerify=false push --mirror http://<token>@gitea.mycompany.com/dst_owner/MyRepo.git
    $ rm -rf MyRepo.git
"""
def migrate_repo(src_url, src_token, src_owner, dst_url, dst_token, dst_owner, repo):
    print 'Repository migration has been started -> From:' + src_url + ', To: ' + dst_url + ', Source owner: ' + src_owner + ', Destination owner: ' + dst_owner + ', Repository: ' + repo

    repo_dir = repo + '.git'
    if os.path.exists(repo_dir):
        print repo_dir + ' is already exist. It will be deleted...'
        subprocess.check_call(['rm', '-rf', repo_dir])

    src_repo_url = get_token_inserted_url(src_url, src_token) + '/' + src_owner + '/' + repo + '.git'
    dst_repo_url = get_token_inserted_url(dst_url, dst_token) + '/' + dst_owner + '/' + repo + '.git'

    subprocess.check_call(['git', '-c', 'http.sslVerify=false', 'clone', '--bare', src_repo_url])
    os.chdir(repo_dir)
    subprocess.check_call(['git', '-c', 'http.sslVerify=false', 'push', '--mirror', dst_repo_url])
    os.chdir('..')
    subprocess.check_call(['rm', '-rf', repo_dir]) 
    print 'Repository migration has been completed -> From:' + src_url + ', To: ' + dst_url + ', Source owner: ' + src_owner + ', Destination owner: ' + dst_owner + ', Repository: ' + repo

"""
Copies given repository under any organization of source server on to any 
organization of destination server.
"""
def copy_repo(src_url, src_token, src_org, dst_url, dst_token, dst_org, repo):
    if get_org(src_url, src_token, src_org) == '':
        raise Exception('Organization [' + src_org + '] does not exist on ' + src_url) 
    if get_repo(src_url, src_token, src_org, repo) == '':
        raise Exception('Repository [' + repo + '] of organization [' + src_org + '] does not exist on ' + src_url)

    create_repo(dst_url, dst_token, dst_org, repo)
    migrate_repo(src_url, src_token, src_org, dst_url, dst_token, dst_org, repo)

"""
Copies all the repositories of each organization on source server 
under to the same organizations of destination server.

All the organizations of source server must exist on destination 
server. copy_orgs() can be used for this.
"""
def copy_repos(src_url, src_token, dst_url, dst_token):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(src_url, src_token, orgName)
        for repo in repos:
            repoName = repo['name']
            copy_repo(src_url, src_token, orgName, dst_url, dst_token, orgName, repoName)

"""
Copies given public repository of a user on source server under to user having 
dst_token(authenticated user) on destination server.

Nothing is done if repository is private.

If dst_user and dst_token do not match, repository is created under user 
having dst_token and migration fails. If API allowed administrators to create 
a repository under *any* user, we would not have this shortcoming.
"""
def copy_user_repo(src_url, src_token, src_user, dst_url, dst_token, dst_user, repo):
    src_repo = get_repo(src_url, src_token, src_user, repo)
    if src_repo == '':
        raise Exception('Repository [' + repo + '] of user [' + src_user + '] does not exist on ' + src_url)
    if src_repo['private']:
        print 'User repository [' + repo + '] is private. It will not be copied. Please make it public and retry.'
    else:        
        create_user_repo(dst_url, dst_token, dst_user, repo)
        migrate_repo(src_url, src_token, src_user, dst_url, dst_token, dst_user, repo)

"""
Copies all the public repositories of given user on source server 
under to destination authenticated user having dst_token on destination server. 
Ownership of these repositories can manually be transfered to their 
own users.

Skips private user repositories.

If dst_user and dst_token do not match, repositories are created under user 
having dst_token and migration fails. If API allowed administrators to create 
a repository under *any* user, we would not have this shortcoming.   
"""
def copy_user_repos(src_url, src_token, src_user, dst_url, dst_token, dst_user):
    repos = get_user_repos(src_url, src_token, src_user)
    for repo in repos:
        repoName = repo['name']
        copy_user_repo(src_url, src_token, src_user, dst_url, dst_token, dst_user, repoName)

"""
Copies all the repositories of given organization on source server 
to the given organization of destination server.
"""
def copy_repos(src_url, src_token, src_org, dst_url, dst_token, dst_org):
    repos = get_repos(src_url, src_token, src_org)
    for repo in repos:
        repoName = repo['name']
        copy_repo(src_url, src_token, src_org, dst_url, dst_token, dst_org, repoName) 

def print_repos(repos):
    for repo in repos:
        repoName = repo['name']
        private = repo['private']
        if private:
            print "\t" + repoName + " (private)"
        else:
            print "\t" + repoName

def print_orgs_and_repos(url, token):
    orgs = get_orgs(url, token)
    for org in orgs:
        orgName = org['username']
        print orgName
        print_repos(get_repos(url, token, orgName))

def print_user_repos(url, token, user):
    print user
    print_repos(get_user_repos(url, token, user))

parse_arguments()
copy_orgs(arg_src_url, arg_src_token, arg_dst_url, arg_dst_token, arg_dst_owner_user)
copy_repos(arg_src_url, arg_src_token, arg_dst_url, arg_dst_token)