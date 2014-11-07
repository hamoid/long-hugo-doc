#! /usr/bin/env python3.4
# -*- coding: UTF-8 -*-

# To generate the one page documentation:
# 1. Get the hugo source from https://github.com/spf13/hugo
# 2. Run this script like:
#    ./generateLongDoc.py --input=hugo/docs/content/ --output=README.md

# Why? I find one long doc easier to navigate (less clicks) and
# it's also searchable within the browser (CTRL+F)

import re, os, argparse

parser = argparse.ArgumentParser(description='Generate Hugo documentation in one file')
parser.add_argument('--input', default="./", help='Input path (.../hugo/docs/content/)')
parser.add_argument('--output', default="README.md", help='Output file')
args = parser.parse_args()

folders = ["overview", "content", "templates", "taxonomies", "extras"]

titleRe = re.compile(r'^title: (.*)')
linktitleRe = re.compile(r'^linktitle: (.*)')
weightRe = re.compile(r'^weight: (.*)')
dividerRe = re.compile(r'^---')
linksBeforeRe = re.compile(r'\[(.*?)\]\(\/(.*?)\/(.*?)\/?\)', re.S)

fullDocument = ""
fullIndex = "# Index\n"

for folder in folders:
    documents = {}
    index = {}

    fullIndex = fullIndex + "\n## " + folder + "\n\n"
    fullPath = args.input + folder

    if not os.path.isdir(fullPath):
        print("\nFolder \"" + fullPath + "\"" + " not found.\nUse --in to specify the input path.\n")
        quit()

    for mdfile in os.listdir(fullPath):
        mdFilePath = fullPath + "/" + mdfile

        print("Reading " + mdFilePath)

        dividerCount = 0
        title = ""
        linktitle = ""
        weight = 999
        content = ""
        md = open(mdFilePath, 'r')
        for line in iter(md.readline, ''):
            if dividerCount == 2:
                content = content + line
            else:
                m = re.match(titleRe, line)
                if m: title = m.group(1)

                m = re.match(linktitleRe, line)
                if m: linktitle = m.group(1).strip('"')

                m = re.match(weightRe, line)
                if m: weight = int(m.group(1))

                m = re.match(dividerRe, line)
                if m: dividerCount = dividerCount + 1

        # fix internal links
        content = re.sub(linksBeforeRe, r'[\1](#\2.\3.md)', content)

        # find a unique weight so documents are not overwritten
        found = False
        while not found:
            try:
                index[weight]
                weight = weight + 1
            except KeyError:
                # This is what we're looking for: a weight that's not used yet
                found = True

        # add title, named anchor, content (indexed by weight)
        documents[weight] = '<a name="%s.%s"></a>\n\n# %s\n\n%s' % (folder, mdfile, title, content)
        index[weight] = '  * <a href="#%s.%s">%s</a>\n' % (folder, mdfile, linktitle or title)

    for key in sorted(documents):
        fullDocument = fullDocument + documents[key]
        fullIndex = fullIndex + index[key]

f = open(args.output, "w")
f.write("This is the documentation of [Hugo](http://gohugo.io/) condensed into one long page. I did this to make the documentation easier to search and navigate. This page was automatically generated using a Python script using the documentation available at Hugo's GitHub repository.\n")
f.write(fullIndex)
f.write(fullDocument)
f.close()
