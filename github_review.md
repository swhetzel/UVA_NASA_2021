## Cloning the Repo

Find the repo on github and find the https website. It should look something like 
```
http://github.com/{username}/{repository}.git
```

Navigate to the folder you want to host your cloned instance - '~' is a shortcut for your 'home' folder; maybe you want to make a folder in your home directory for github and store your repos inside it?

```
cd ~ 
mkdir github
cd github
```

And clone the repo - you'll have to enter a username and password

```
git clone http://github.com/{username}/{repository}.git
```

If this generates an error ('Support for password authentication was removed on August 13, 2021...') then let's go make a 'Personal Access Token'.

https://www.cloudsavvyit.com/14870/how-to-set-up-https-personal-access-tokens-for-github-authentication/

Short version: head to GitHub -> click on your user's logo and choose 'Settings' -> at the bottom of the left on the left is 'Developer Settings' -> Personal Access Tokens. Make a new one, title it as you want (I named mine 'DS5110 Final Project'), choose the 'repo' permission (this allows command line interfacing with github so pull, push, merge, branch, etc), and make your token. Save your token in a safe place as github won't show it to you again - you'll have to regenerate it if you lose it (like I did the first time :X ).

Now try cloning the repo again - this time using your username and personal access token.

```
git clone http://github.com/{username}/{repository}.git
```

## Check out your new repo!

```
cd ~/github/{repository}
```

You should now be inside your repository. I'm going to assume you want to make a new file or make some changes. Let's start with a conversation about branches. Each repository has a single trunk with a seemingly unlimited number of potential branches - we'll call the trunk 'main' (although it used to be called 'master') and every other branch is a 'branch'. Typically, inside organizations, the 'main' branch is protected so no one can write directly to it - rather all work is done on branches which are then put up for a 'Peer Review' (PR) so that other teammates can sign off on the work before it is 'merged' into the 'main' branch. We don't have access to the professional level of github so we don't have a protected 'main' branch - instead, we're just going to be responsible colleagues and never write directly to the 'main' branch. So, lets make a branch so we can play around with the code in a safe environment.

https://github.com/Kunena/Kunena-Forum/wiki/Create-a-new-branch-with-git-and-manage-branches

Always start with a git pull to grab the latest changes.
```
git pull
```

Now check which branch you're on and whether you have uncommited changes.
```
git status
```

This should return something like:
```
# On branch main
nothing to commit, working directory clean
```

## Make a new branch

Now switch to your branch (or create a new one - same line)
```
git checkout -b [name_of_your_new_branch]

# git checkout -b show_branch_example
```

Name your branches something short and descriptive - 'add_cumulative_metric_features' and never use any spaces or dots, only underscores. Trust me, it will make your life way easier.

Do another git status and see what you're working on now:
```
git status
# On branch show_branch_example
nothing to commit, working directory clean
```

## Add new files, commit changes, and push to the origin

Now that we're on a new branch, feel free to save a file you're working on to this folder. When you're ready to save, its time to 'add' changes.

```
git add .
# OR
git add full_file_name.ipynb

# git add PeterTestFile.ipynb
``` 

Now when you run a git status - you'll get something like this:
```
# On branch show_branch_example
# Changes to be committed:
#   (use "git reset HEAD <file>..." to unstage)
#
#       new file:   PeterTestFile.ipynb
```

If you're happy with your files and you want to 'commit' the changes to the repo. The '-m' signals git that you're putting a message on this group of commits - keep it short, active language, and easily understood. If you don't use the '-m' feature, you'll be forced to write a brief commit message before git will actually allow you to commit - if you don't, it will be 'aborted'.

```
git commit -m 'Make a Test File'
```

Now do another git status to see where we are:
```
# On branch show_branch_example
nothing to commit, working directory clean
```

We've committed our changes to our local environment - but that doesn't mean anyone else can see them. We need to push it up to the repo - this will ask for your username and password (actually your personal access token).
```
git push origin [your_branch_name]

# git push origin show_branch_example
```

## Peer Review // Pull Request

Congrats! You've pushed your branch to the repo and other developers can see your branch. Now comes the 'Pull Request' (PR). When you're ready to merge your branch to the 'main' branch, you'll do a quick write up in the GitHub site interface. Be descriptive in your PR about what you're changing and why your changing it - this is what you'll see when you come back to your code in 3 months and have no memory of what you did or why so help future you out by writing something useful :)

Assign some Reviewers (your colleages) and have the discussion around what you're doing and why - the best developers spend a lot of time talking with other developers because no individual has all the best ideas - we're a whole lot smarter as a team. Once the reviewers have 'accepted' the changes, feel free to 'Merge pull request' through the UI and now your changes are a part of the 'main' branch! 

Last but not least, check out the main branch to see the now merged code - and start a new branch for any changes :)

```
git checkout main
git checkout -b my_new_branch_here
```
