# My Dropbox

## Project Description

A client-server pipeline implemented with python socket programming to serve basic file sharing functionality with automatic syncing.

## Features

There are several command line commands implemented. 

- index longlist: to list files residing on the other side, along with their details
- index shortlist: to list files residing on the other side, between two specific timestamps
- index regex: to list files residing on the other side, matching some patterns in their names
- hash verify: get the hash of specific file residing on the other side
- hash checkall: get the hash of all files residing on the other side
- download UDP: UDP download of specific file until full file is downloaded without error
- download TCP: TCP download of specific file

