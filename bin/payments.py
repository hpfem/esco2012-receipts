#!/usr/bin/env python

import sys, os, re

try:
    _, _input, _output = sys.argv
except ValueError:
    print "usage: payments.py <input-file> <output-dir>"
    sys.exit(1)

re_paid = re.compile(r"^\\noindent\s+(.+)$")
re_name = re.compile(r"^{\\bf (.+)}")
re_subs = re.compile(r"[ ,\\\r\n]*$")

S_NONE = 0
S_PAID = 1
S_NAME = 2

status = S_NONE

stack = []
data = {}

print ">>> Collecting data"

with open(_input) as f:
    for line in f.readlines():
        if status == S_NONE:
            line = re_subs.sub("", line)
            r = re_paid.match(line)

            if r is not None:
                data = { 'paid': r.groups()[0] }
                status = S_PAID

            continue

        if status == S_PAID:
            r = re_name.match(line)

            if r is not None:
                data['name'] = r.groups()[0].strip()
                data['data'] = []
                status = S_NAME
            else:
                status = S_NONE

            continue

        if status == S_NAME:
            line = re_subs.sub("", line)

            if line:
                data['data'].append(line)
            else:
                stack.append(data)
                status = S_NONE

            continue

prefix = r'''
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\topmargin=1cm
\leftmargin=0cm
\pagestyle{empty}
\begin{document}
'''

template = r'''
\vbox{}
\vspace{-2cm}
\begin{figure}[!ht]
\includegraphics[width=7cm]{../horizon_no_slogan.jpg}
\end{figure}
\noindent
%(data)s
\noindent
\hbox{} \hfill May 10, 2010\\
\hbox{} \hfill Reno, NV, USA\\
Dear Mr. %(name)s,\\
\noindent
The Department of Mathematics and Statistics, University of Nevada, Reno
acknowledges the receipt of your registration fee for the ESCO 2010
conference in the amount of USD %(paid)s. \\
\begin{figure}[!ht]
\includegraphics[width=3.5cm]{../signature.pdf}
\vspace{-4mm}
\end{figure}
\noindent
Eric Herzik, Ph.D., Chair\\
Department of Mathematics and Statistics\\
University of Nevada, Reno\\
1664 N Virginia Street\\
Reno, NV 89557\\
Phone: (775) 848-7892\\
E-mail: esco2010@unr.edu
'''

postfix = r'''
\end{document}
'''

re_clean = re.compile(r"\.| |{|}|\\.|");

includes = []

print ">>> Writing output"

for item in stack:
    name = re_clean.sub("", item['name'])

    item['data'].insert(0, item['name'])
    item['data'] = "".join([ d + "\\\\\n" for d in item['data'] ])

    content = template % item

    with open(os.path.join(_output, name + ".tex"), 'w') as f:
        f.write(content)

    with open(os.path.join(_output, name + "-complete.tex"), 'w') as f:
        f.write(prefix + content + postfix)

    includes.append("\\include{%s}\n" % name)

with open(os.path.join(_output, "__all__.tex"), 'w') as f:
    f.write(prefix + "".join(includes) + postfix)

print "=== Wrote %s items" % len(stack)
print """
To compile all items into one PDF, issue:

    $ cd %s
    $ pdflatex __all__.tex

To compile all items into separate PDFs, issue:

    $ cd %s
    $ for name in $(ls *-complete.tex); do pdflatex $name; done

""" % (_output, _output)

