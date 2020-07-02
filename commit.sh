#!/bin/bash

git pull origin master
git add index.md
git commit -m "Automatic Table Update"
git push -u origin master
