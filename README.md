# gogs2gitea
Migration script that helps copy organizations and repositories(with all the history) from Gogs/Gitea to Gogs/Gitea.

## What does it do?
* Creates all the organizations of source Gogs/Gitea on destination Gogs/Gitea
* Creates all the repositories of each organization of source Gogs/Gitea on destination Gogs/Gitea
* Migrates repositories of source Gogs/Gitea to destination Gogs/Gitea

## Limitations
* It does not migrate specific user's organization and repositories. You can use `copy_user_repo()` function, though.
* It does not create users on destination Gogs/Gitea
* It does not create teams on destination Gogs/Gitea. Authenticated user of destination server(`dst_owner_user`) becomes the owner of all the organizations and repositories.
* It does not copy avatars from source Gogs/Gitea to destination Gogs/Gitea.

## Compatibility

Tested with;
* Python 2.7.5
* Gogs Version: 0.11.4.0405
* Gitea Version: 1.3.0 and 1.3.2

## Prerequisites
* An administrator account and its access token must be created on destination Gogs/Gitea to be used as `dst_owner_user`.
* Access token of source must belong to a user which owns all the organizations and repositories. Otherwise, given user's organizations and repositories are copied only.

## Hints

Script was created to be read and modified easily. Just tweak it to suit your needs.

```python
gogs__url = 'http://gogs.mycompany.com' 
gogs_token = '60a4cf0f5c90625c99c14b64392ead3963a9f00dc'
gitea_url = 'http://gitea.mycompany.com' 
gitea_token = '5d7da2370c4b62c99f5c6496391a2ed66f07be3f'
owner_user = 'gitea_admin'

# Prints organizations and repos
print_orgs_and_repos(gogs_url, gogs_token)

# Creates newOrg organization whose owner ise owner_user
create_org(gitea_url, 
           gitea_token, 
           owner_user, 
           'newOrg', 
           'newOrg full name', 
           'newOrg description.', 
           'http://newOrg.mycompany.com', 
           'TR')

# Creates newRepo repository under newOrg organization.
create_repo(gitea_url, gitea_token, 'newOrg', 'newRepo')

# Migrates newRepo of newOrg from Gogs to Gitea.
migrate_repo(gogs_url, gogs_token, 'newOrg', gitea_url, gitea_token, 'newOrg', 'newRepo')

# Deletes newRepo of newOrg.
delete_repo(gitea_url, gitea_token, 'newOrg', 'newRepo')

# Copies testOrg of Gogs to Gitea. Repositories are not copied.
copy_org(gogs_url, gogs_token, gitea_url, gitea_token, owner_user, 'testOrg')

# Copies testRepo of gogsOrg from Gogs to giteaOrg of Gitea.
# It simply calls create_repo() and migrate_repo().
copy_repo(gogs_url, gogs_token, 'gogsOrg', gitea_url, gitea_token, 'giteaOrg', 'testRepo')

# Copies all the organizations from Gogs to Gitea. gitea_owner_user
# becomes the owner of all the organizations.
copy_orgs(gogs_url, gogs_token, gitea_url, gitea_token, gitea_owner_user)

# Copies all the repositories of each organization on Gogs to Gitea.
# All the Gogs organizations must exist on Gitea. copy_orgs() can be used 
# for this.
copy_repos(gogs_url, gogs_token, gitea_url, gitea_token)

# Copies MyRepo of MyUser under to YourUser in the same server.
copy_user_repo(gitea_url, gitea_token, 'MyUser', gitea_url, gitea_token, 'YourUser', 'MyRepo')

# Copies public repositories of MyUser on Gogs under to YourUser on Gitea. 
copy_user_repos(gogs_url, gogs_token, 'MyUser', gitea_url, gitea_token, 'YourUser')

# Prints repositories of YourUser
print_user_repos(gitea_url, gitea_token, 'YourUser')
```

## Usage

        python migrate.py [-h] --src_url SRC_URL --src_token SRC_TOKEN --dst_url
                        DST_URL --dst_token DST_TOKEN --dst_owner_user
                        DST_OWNER_USER

        arguments:
        -h, --help              show this help message and exit

        --src_url SRC_URL       (Required) URL of source Gogs/Gitea 
                                (e.g. http://gogs.mycompany.com)
        
        --src_token SRC_TOKEN   (Required) Access token of user that owns 
                                the repositories on source Gogs/Gitea
        
        --dst_url DST_URL       (Required) URL of destination Gogs/Gitea 
                                (e.g. http://gitea.mycompany.com)
        
        --dst_token DST_TOKEN   (Required) Access token of user that owns 
                                the repositories on destination Gogs/Gitea
        
        --dst_owner_user DST_OWNER_USER  (Required) Owner of all the organizations 
                                         on destination Gogs/Gitea