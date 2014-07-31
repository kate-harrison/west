
import os
import subprocess

source_directories = [os.path.abspath("..")]
rst_directory = "."

excluded_modules = ["test", "test2", "test3", "doc_inherit", "snippets",
                    "doc_inherit2", "custom_logging", "see_profile"]
test_suffix = "test.py"

modules = []
# ==========================================================

# Contents
# ========
#
# .. toctree::
# :maxdepth: 2



def generate_rst(module_name):
    overline = "".center(len(module_name), "#")
    output = """
%s
%s
%s


Heritage
========
.. inheritance-diagram:: %s

Members
=======
.. automodule:: %s
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`""" % (overline, module_name, overline, module_name, module_name)

    with open(os.path.join(rst_directory, module_name + ".rst"), "w") as f:
        f.write(output)



for src_dir in source_directories:
    files = os.listdir(src_dir)
    for filename in files:
        if not filename.lower().endswith(".py"):
            continue

        # Skip test files
        if filename.lower().endswith(test_suffix):
            continue

        module_name = filename[:-3]

        if module_name in excluded_modules:
            continue

        rst_string = generate_rst(module_name)
        modules.append(module_name)


module_str = ""
for module in modules:
    module_str += "   %s\n" % module
module_csv = " ".join(modules)

index_output = """
.. Whitespace Evaluation SofTware documentation master file, created by
   sphinx-quickstart on Wed Jul  9 13:12:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########################################################
Welcome to Whitespace Evaluation SofTware's documentation!
##########################################################

Inheritance diagrams
====================
.. inheritance-diagram:: %s
   :parts: 1

Modules:
=========
.. toctree::
   :maxdepth: 1
   :titlesonly:

%s

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""" % (module_csv, module_str)

print("Documented the following modules:\n%s" % module_str)

with open(os.path.join(rst_directory, "index.rst"), "w") as f:
    f.write(index_output)

subprocess.call(["make", "html"])
