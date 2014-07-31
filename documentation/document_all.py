
import os
import subprocess

# See http://mainlydata.kubadev.com/python/sphinx-how-to-make-autodoc-really-automatic/

source_directories = [os.path.abspath("..")]
rst_directory = "."

excluded_modules = ["test", "test2", "test3", "doc_inherit", "snippets",
                    "doc_inherit2", "custom_logging", "see_profile"]

# groups = ["propagation_model", "protected_entities", "protected_entity", "region", "ruleset"]
groups = [("Propagation models", "propagation_model"), ("Protected entities", "protected_entities"),
          ("Protected entity", "protected_entity"), ("Region", "region"), ("Ruleset", "ruleset")]


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


def generate_group_rst(group_name, group_str, module_name_list):
    overline = "".center(len(group_name), "#")
    module_name_list_str = ""
    for module_name in module_name_list:
        module_name_list_str += "   %s\n" % module_name
    glob_module_name_list_str = ""
    for module_name in module_name_list:
        glob_module_name_list_str += "   %s\n" % module_name
    output = """
%s
%s
%s


Heritage
========
.. inheritance-diagram:: %s

Modules
=======
Links point to the module's individual page.

.. autosummary::

%s

""" % (overline, group_str, overline, module_name_list_str, glob_module_name_list_str)

    for module_name in module_name_list:
        underline = "".center(len(module_name), '-')
        output += """
%s
%s

.. automodule:: %s
   :members:
""" % (module_name, underline, module_name)

    output += """
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`"""

    with open(os.path.join(rst_directory, "group_" + group_name + ".rst"), "w") as f:
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

print("All modules:", modules)
for (group_str, group_name) in groups:
    print("Adding group %s" % group_name)
    module_name_list = []
    for module_name in modules:
        if module_name.startswith(group_name):
            # print("Found!")
            module_name_list.append(module_name)
    print("  Modules: %s" % str(module_name_list))
    generate_group_rst(group_name, group_str, module_name_list)



module_str = ""
for module in modules:
    module_str += "   %s\n" % module
module_csv = " ".join(modules)

group_str = ""
for (_, group_name) in groups:
    group_str += "   group_%s\n" % group_name

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


Groups:
=======
.. toctree::
   :maxdepth: 1
   :titlesonly:

%s

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
""" % (module_csv, group_str, module_str)

print("Documented the following modules:\n%s" % module_str)

with open(os.path.join(rst_directory, "index.rst"), "w") as f:
    f.write(index_output)

subprocess.call(["make", "html"])
