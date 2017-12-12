# gogs2gitea
Migration script that helps copy organizations and repositories(with all the history) from Gogs/Gitea to Gogs/Gitea.

## What it does?
* Creates all the organizations of source Gogs/Gitea on destination Gogs/Gitea
* Creates all the repositories of each organization of source Gogs/Gitea on destination Gogs/Gitea
* Migrates repositories of source Gogs/Gitea to destination Gogs/Gitea

## Limitations
* It does not migrate specific user's organization and repositories. You can use `copy_repo()` function, though.
* It does not create users on destination Gogs/Gitea
* It does not create teams on destination Gogs/Gitea. Owner of all the organizations and repositories is `dst_owner_user`.
* It does not copy avatars from source Gogs/Gitea to destination Gogs/Gitea.

## Compatibility

Tested with;
* Python 2.7.5
* Gogs Version: 0.11.4.0405
* Gitea Version: 1.3.0

## Prerequisites
* An administrator account and its access token must be created on destination Gogs/Gitea to be used as `dst_owner_user`.
* Access token of source must belong to a user which owns all the organizations and repositories. Otherwise, organizations and repositories of the given user are copied only.

## Hints

Script was created to be read and modified easily. Just tweak it to suit your needs.

```python
gogs__url = 'http://gogs.mycompany.com' 
gogs_token = '60a4cf0f5c90625c99c14b64392ead3963a9f00dc'
gitea_url = 'http://gitea.mycompany.com' 
gitea_token = '5d7da2370c4b62c99f5c6496391a2ed66f07be3f'
owner_user = 'gitea_admin'

# Prints organizations and repos of Gogs
print_orgs_and_repos(gogs_url, gogs_token)

# Prints organizations and repos of Gitea
print_orgs_and_repos(gitea_url, gitea_token)

# Creates newOrg organization whose owner ise owner_user
create_org(gitea_url, 
           gitea_token, 
           owner_user, 
           'newOrg', 
           'newOrg full name', 
           'newOrg description.', 
           'http://newOrg.mycompany.com', 
           'TR')

# Creates newRepo repository under newOrg organization
create_repo(gitea_url, gitea_token, 'newOrg', 'newRepo')

# Migrates newRepo of newOrg from Gogs to Gitea
migrate_repo(gogs_url, gogs_token, gitea_url, gitea_token, 'newOrg', 'newRepo')

# Deletes newRepo of newOrg
delete_repo(gitea_url, gitea_token, 'newOrg', 'newRepo')

# Copies testOrg of Gogs to Gitea. Repositories are not copied.
copy_org(gogs_url, gogs_token, gitea_url, gitea_token, owner_user, 'testOrg')

# Copies testRepo of testOrg from Gogs to Gitea.
# It simply does create_repo() and migrate_repo().
copy_repo(gogs_url, gogs_token, gitea_url, gitea_token, 'testOrg', 'testRepo')

# Copies all the organizations from Gogs to Gitea
copy_all_orgs(gogs_url, gogs_token, gitea_url, gitea_token, owner_user)

# Copies all the repositories of each organization on Gogs to Gitea
copy_all_repos(gogs_url, gogs_token, gitea_url, gitea_token)
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