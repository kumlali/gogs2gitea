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
       http://gogs.mycompany.com/api/v1/user/orgs
"""
def get_orgs(url, token):
   return get(get_api_url(url) + '/user/orgs', '', token)

"""
Equivalent to:
    curl -v \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gogs.mycompany.com/api/v1/orgs/<orgname>
"""
def get_org(url, token, org):
   return get(get_api_url(url) + '/orgs/' + org, '', token)

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
   post(get_api_url(url) + '/admin/users/' + owner_user + '/orgs', {'username': org, 
                                                                     'full_name': full_name, 
                                                                     'description': description, 
                                                                     'website': website, 
                                                                     'location': location}, token)
   print 'Organization has been created -> On Git server: ' + url + ', Owner user: ' + owner_user + ', Organization: ' + org

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
Equivalent to:
    curl -v -X POST \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       -d '{"name":"MyRepo"}' \
       http://gitea.mycompany.com/api/v1/org/MyOrg/repos
"""
def create_repo(url, token, org, repo):
   print 'Repository will be created -> On Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo
   post(get_api_url(url) + '/org/' + org + '/repos', {'name': repo}, token)
   print 'Repository has been created -> On Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo

"""
Equivalent to:
    curl -v -X DELETE \
       -H "Content-Type: application/json" \
       -H "Authorization: token <token>" \
       http://gitea.mycompany.com/api/v1/repos/MyOrg/MyRepo 
"""
def delete_repo(url, token, org, repo):
   print 'Repository will be deleted -> From Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo
   delete(get_api_url(url) + '/repos/' + org + '/' + repo, token)
   print 'Repository has been deleted -> From Git server: ' + url + ', Organization: ' + org + ', Repository: ' + repo

def delete_all_repos(url, token):
    orgs = get_orgs(url, token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(url, token, orgName)
        for repo in repos:
            repoName = repo['name']
            delete_repo(url, token, orgName, repoName)

def create_all_repos(src_url, src_token, dst_url, dst_token):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(src_url, src_token, orgName)
        for repo in repos:
            repoName = repo['name']
            create_repo(dst_url, dst_token, orgName, repoName)

"""
Equivalent to:
    $ git -c http.sslVerify=false clone --bare http://<token>@gogs.mycompany.com/MyOrg/MyRepo.git
    $ cd MyRepo.git
    $ git -c http.sslVerify=false push --mirror http://<token>@gitea.mycompany.com/MyOrg/MyRepo.git
    $ rm -rf MyRepo.git
"""
def migrate_repo(src_url, dst_url):
    repo_dir = src_url.split('/')[-1]
    if os.path.exists(repo_dir):
        print repo_dir + ' is already exist. It will be deleted...'
        subprocess.check_call(['rm', '-rf', repo_dir])
    print 'Repository migration has been started -> From:' + src_url + ' To: ' + dst_url
    subprocess.check_call(['git', '-c', 'http.sslVerify=false', 'clone', '--bare', src_url])
    os.chdir(repo_dir)
    subprocess.check_call(['git', '-c', 'http.sslVerify=false', 'push', '--mirror', dst_url])
    os.chdir('..')
    subprocess.check_call(['rm', '-rf', repo_dir]) 
    print 'Repository migration has been completed -> From:' + src_url + ' To: ' + dst_url

def create_and_migrate_all_repos(src_url, src_token, dst_url, dst_token):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        repos = get_repos(src_url, src_token, orgName)
        for repo in repos:
            repoName = repo['name']
            create_repo(dst_url, dst_token, orgName, repoName)
            src_repo_url = get_token_inserted_url(src_url, src_token) + '/' + orgName + '/' + repoName + '.git'
            dst_repo_url = get_token_inserted_url(dst_url, dst_token) + '/' + orgName + '/' + repoName + '.git'
            migrate_repo(src_repo_url, dst_repo_url)

"""
   Because /orgs/<orgname> (and get_org() accordingly) does not return 
   the owner, we need to know it while creating the organization on 
   destination server. That is why we need dst_owner_user.
"""
def create_and_migrate_org(src_url, src_token, dst_url, dst_token, dst_owner_user, org):
    print 'Organization migration has been started -> From:' + src_url + ' To: ' + dst_url + ' Destination owner user: ' + dst_owner_user + ' Organization: ' + org
    orgJson = get_org(src_url, src_token, org)
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
   Because /orgs/<orgname> (and get_org() accordingly) does not return 
   the owner, we need to know it while creating the organization on 
   destination server. That is why we need dst_owner_user.
"""
def create_and_migrate_all_orgs(src_url, src_token, dst_url, dst_token, dst_owner_user):
    orgs = get_orgs(src_url, src_token)
    for org in orgs:
        orgName = org['username']
        create_and_migrate_org(src_url, src_token, dst_url, dst_token, dst_owner_user, orgName)


parse_arguments()
create_and_migrate_all_orgs(arg_src_url, arg_src_token, arg_dst_url, arg_dst_token, arg_dst_owner_user)
create_and_migrate_all_repos(arg_src_url, arg_src_token, arg_dst_url, arg_dst_token)