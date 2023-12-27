#!/usr/bin/env python3
##############################################
#
#  USEAGE:  ./metastringer.py <domain> <filetype>
#
#  Search Archive.org (The Wayback Machine)
#  for records actd. with a domain and list
#  stats per filetype, provide option for
#  retrieving files and obtaining metadata.
#
#  RAW FILE LIST:
#  https://web.archive.org/web/timemap/?url=http%3A%2F%2Fwww. <DOMAIN>
#  %2F&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype
#  %2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=100000
#
#  ARCHIVED URL:
#  https://web.archive.org/web/*/<file-record>
##############################################
#   >>>  TO DO  <<<
#   - use dictionary to return file records, with number listed in first comma'd column, allow retrieval of #'s [1,5,6,9] etc
#   - script output of list of users and users + their assctd file
#   - search by file desc (i.e. application/pdf instead of pdf)
##############################################

import os
import errno
import re
import requests
import signal
import sys
import json

signal.signal(signal.SIGINT, lambda signal_number, current_stack_frame: sys.exit())

##############################################
def mainMenu():
  global domain
  global choice
  global filetype
  if len(sys.argv) < 3:
    print("useage:  "+sys.argv[0]+" <domain> <file extension>")
    exit()
  domain = sys.argv[1]
  filetype = sys.argv[2].lower()
  rmWww()
  jsonify()
  typeSearch()
  retrieveFile()

##############################################
def rmWww():
  global domain
  prefix = 'www.'
  if domain.startswith(prefix):
    domain = domain[len(prefix):]
##############################################
def jsonify():
  global json
  url = "https://web.archive.org/web/timemap/?url=http%3A%2F%2Fwww."+domain+"%2F&matchType=prefix" \
  "&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2C" \
  "uniqcount&filter=!statuscode%3A%5B45%5D..&limit=100000"
  resp = requests.get(url)
  json = json.loads(resp.text)
##############################################
def typeSearch():
  print()
  count = 0
  for item in json:
    if "."+filetype in item[0]:
      count +=1
  if count == 0:
    print("No "+filetype.upper()+" files were found.")
    quit()
  if count < 6:
    print("*** NOTE:  These are archived URLs, and possibly no longer active.")
    print()
    for item in json:
      if "."+filetype in item[0]:
        print(item[0]+","+item[2])
    print()
    print("Retrieve a file?  [y/N]")
    if input("  ").lower() == "y":
      print("Enter ENTIRE LINE (including numeric date value) for file you wish to retrieve.")
      retrieveFile()
    else:
      quit()
    ############### cutting into new function
  else:
    print(str(count)+" "+filetype.upper()+" files were found.")
    print()
    print(" [P]rint list of files   [NOTE # of files!]")
    print(" [S]ave output to file")
    print(" [Q]uit")
    global outputChoice
    outputChoice = input("  ")
    outputMenuChoice()
##############################################
def retrieveFile():
  getThisFile = input("")
  if getThisFile.lower() == "q":
    quit()
  archivedSelection = getThisFile.split(',')
  urlSelection = archivedSelection[0]
  numSelection = archivedSelection[1]
  shortFileName = urlSelection.rsplit("/", 1)
  global shortFName
  shortFName = shortFileName[1]
  print("If request hangs, it may be following a redirect..")
  getF = "https://web.archive.org/web/"+numSelection+"/"+urlSelection
  response = requests.get(getF)
  # create a dir of client name to put files in
  with open('./'+shortFName, 'wb') as f:
    f.write(response.content)
  print("Saved as ./"+shortFName)
  print()
  retrMeta = input("RETRIEVE [M]ETADATA on "+shortFName+"?\n")
  if retrMeta.lower() == "m":
    retrMeta()
  print("Enter another file or [q]uit.")
  retrieveFile()
##############################################
def outputMenuChoice():
  print()
  if outputChoice.lower() == "p":
    for item in json:
      if "."+filetype in item[0]:
        print(item[1]+","+item[0]+","+item[2])
    print()
    print("Retrieve a file?  [y/N]")
    if input("  ").lower() == "y":
      print()
      print("Enter ENTIRE LINE (including numeric date value) for file you wish to retrieve.")
      retrieveFile()
    else:
      quit()
  elif outputChoice.lower() == "s":
    filename = "./"+domain+"_"+filetype+"_archive.txt"
    f = open('./'+filename,"w+")
    for item in json:
      if "."+filetype in item[0]:
        f.write(item[1]+","+item[0]+","+item[2]+"\n")
    f.close()
    print("Saved to "+filename)
  elif outputChoice.lower() == "q":
    quit()
##############################################
def retrMeta():
  print("Retrieving metadata on:  "+shortFName)
  quit()
##############################################

mainMenu()
