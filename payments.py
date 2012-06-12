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
\includegraphics[width=\textwidth]{../femhub_logo.png}
\vspace{1cm}
\end{figure}
\noindent
%(data)s
\noindent
\hbox{} \hfill March 27, 2012\\
\hbox{} \hfill Reno, NV, USA\\
Dear %(name)s,\\
\newline
\noindent
We acknowledge the receipt of your registration fee for the 
third European Seminar on Computing (ESCO 2012) in 
the amount of EUR %(paid)s.
\newline
\vspace{1cm}
\newline
\hbox{}
\hspace{-4mm}
\vspace{2cm}
%\includegraphics[width=3.5cm]{../signature.pdf}
\newline
\noindent
Pavel Solin\\
FEMhub Inc.\\
5490 Twin Creeks Dr.\\
Reno, NV 89523\\
Phone: (775) 848-7892\\
E-mail: esco2012@femhub.com
\begin{figure}[!ht]
\includegraphics[width=\textwidth]{../femhub_footer.png}
\vspace{1cm}
\end{figure}
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

    with open(os.path.join(_output, name + "-receipt-esco.tex"), 'w') as f:
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
    $ for name in $(ls *-receipt-esco.tex); do pdflatex $name; done

""" % (_output, _output)

