# Overview

Get the track of a CLS NEMO beacon and convert it to a GPX file.

# Installation

## Pre-requisites

1. Import the libraries 'requests' and 'gpxpy'
1. Launch 'git update-index --skip-worktree param.json'
1. Modify the file 'param.json' with the wanted id and password

## First use

1. In 'launcher.py', define the start and end dates of the time window you want to investigate as well as the name of the output gpx file
1. Execute 'launcher.py'