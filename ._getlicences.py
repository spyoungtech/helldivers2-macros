import os
import platform
import re
import sys
import textwrap

this_package = 'hd2_macros'
outdir = 'hd2macros/hd2_macros/_internal'
with open('LICENSE') as f:
    this_license = f.read()
lic_template_header = f'''\
COPYRIGHT
=========

This software is the copyright of Spencer Phillip Young and published by
Young Enterprise Solutions, LLC under the terms of the MIT license as follows:

{textwrap.indent(this_license, "  ")}

NOTICE
======

This software makes use of third-party Open Source software which are the
copyright of their respective author(s). No association or endorsements by
these third parties are expressed or implied.

The remainder of this NOTICE is a summary of the third-party software used in
this software, along with their respective licenses and/or related notices.
License files and other metadata can also be found in the distribution files
contained within this installer, which may contain additional notices.

THIRD-PARTY SOFTWARE
====================
'''


dist_names = []

for name in os.listdir(outdir):
    if name.endswith('.dist-info'):
        dist_names.append(name)


pattern = re.compile(r'^(?P<package_name>[\w_]+)-(?P<version>.*)\.dist-info$')

output = lic_template_header
for distdirname in dist_names:
    package_name, version = re.match(pattern, distdirname).groups()  # type: ignore
    package_info = f'{package_name} {version}'
    output += f'\n{package_name} {version}\n'
    if package_name == this_package:
        continue
    output += f'{"-" * len(package_info)}\n\n'

    dist_dir = os.path.join(outdir, distdirname)
    for root, dirs, files in os.walk(dist_dir):
        for filename in files:
            if 'license' in filename.lower() or 'notice' in filename.lower():
                fp = os.path.join(root, filename)
                output += f'{filename}:\n'
                with open(fp) as f:
                    output += f'\n{textwrap.indent(f.read(), '    ')}\n'
    output += f'{"-" * 80}\n'

python_info = f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}:{platform.python_revision()} [{platform.python_compiler()}]'
output += f'''
{python_info}
{"-" * len(python_info)}

Copyright notice:

{textwrap.indent(sys.copyright, '    ')}

Trademark notice:

    "Python" is a registered trademark of the Python Software Foundation”
{"-" * 80}
'''

with open('INNOLICENSE', 'w', encoding='utf-8') as f:
    f.write(output)
