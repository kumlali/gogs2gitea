# gogs2gitea
Migration script that helps copy organizations and repositories(with all the history) from Gogs/Gitea to Gogs/Gitea.

What it does?
* Creates all the organizations of source Gogs/Gitea on destination Gogs/Gitea
* Creates all the repositories of each organization of source Gogs/Gitea on destination Gogs/Gitea
* Migrates repositories of source Gogs/Gitea to destination Gogs/Gitea

What it does not?
* It does not create users on destination Gogs/Gitea
* It does not create teams on destination Gogs/Gitea. Owner of all the organizations and repositories is `dst_owner_user`.
* It does not copy keeps avatars from source Gogs/Gitea to destination Gogs/Gitea.

Tested with;
* Python 2.7.5
* Gogs Version: 0.11.4.0405
* Gitea Version: 1.3.0

Prerequisites
* An admin user and its access token must be created on destination Gogs/Gitea to be used as `dst_owner_user`.
* Access token of source must belong to a user which owns all the organizations and repositories. Otherwise, organizations and repositories of the given user are copied only.

Hint

Script was created to be read and modified easily. Just tweak it to suit your needs.

Usage

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