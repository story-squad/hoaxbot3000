
# Adding a submodule to a repo
## git submodule add {repo url}
- adds .gitmodules file to the repository
- _Since the URL in the .gitmodules file is what other people will first try to clone/fetch from, make sure to use a URL that they can access if possible._

## git commit -am 'Add submodule'
- commits the change to the repository

## git push origin master
- pushes the change to the remote repository

# Cloning a Project with Submodules
## Fresh clone
- git clone --recurse-submodules {repo url}
## Clone then update submodules
- git clone {repo url}
- git submodule init
- git submodule update

# Working on a Project with Submodules
- from submodule dir
- - git fetch
- git submodule update --remote DbConnector