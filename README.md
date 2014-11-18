Whitespace Evaluation SofTware (WEST)
-------------------------------------

WEST is a tool which makes it easy to evaluate
[whitespace](http://en.wikipedia.org/wiki/White_spaces_%28radio%29) 
opportunities with different regulatory sets and for wide variety of 
geographies. It can be used to make color-coded maps showing the amount of 
available whitespace like the ones in [my research](http://kateharrison.net/).

See below for an overview of the module's structure and instructions for 
getting started.


Using this software?
--------------------
Please [send me an email](mailto:harriska@eecs.berkeley.edu) if you have any 
questions or requests. If your work is also open source (highly encouraged), 
I'd love to link to your project.

If you use this software for an academic paper, please cite it using this 
github page:
>     @misc{west_software,
>      author = {Kate Harrison}
>      title = {{Whitespace Evaluation SofTware}},
>      url={https://github.com/kate-harrison/west}
>     }

Please also make sure you read and abide by the terms of the license (GPLv2).
If the terms of the license are not suitable for your application,
please contact me: I may be willing to release under a more permissive 
license if necessary.


Want to contribute?
-------------------
Please feel free to fork this code and send me a pull request if you make any
changes you'd like to share with the world. I'm very interested in seeing 
this code base develop further.


Author information
------------------
**Kate Harrison**

 * UC Berkeley graduate student in EECS
 * harriska at eecs dot berkeley dot edu
 * [kateharrison.net](http://kateharrison.net/)



History
-------
WEST was inspired by the author's experience with [her previous whitespace 
evaluation software](https://github.com/kate-harrison/whitespace-eval) which 
is written in Matlab and is very US-centric. WEST is intended to be modular and
extensible so that users can easily add their own support for different 
propagation models, rulesets, and geographies.


Getting started
---------------

1. Clone this repository.
2. Install the west module by running ```sh install_west.sh``` from the root 
directory.
2. Install dependencies: ```pip install -r requirements.txt```
3. In ```$REPO_ROOT/documentation```, run ```python document_all.py```. View 
documentation at ```$REPO_ROOT/documentation/_build/html/index.html```.
4. *Outside* of the repository, use ```import west``` to import the module. 
Working inside the repository may compromise your ability to generate 
documentation.
5. Look at the code samples in the ```examples/``` directory for next steps.


Overview
--------

There are several key module types in WEST.

 - **DataMap** (DataMap2D or DataMap3D): the standard format for data is a 
 2-D matrix with geographical metadata. A DataMap3D allows for aggregation of
  DataMap2D objects.
 - **Population**: reads in population data and creates a population DataMap2D.
 - **Region**: specifies various parameters about a region such as which 
 channels are available for whitespace use and the set of protected entities.
 - **Boundary**: specifies the boundary of the given region; mostly used for 
 plotting purposes. 
 - **ProtectedEntity**: specifies an entity (e.g. TV station) that may be 
 eligible for protection.
 - **ProtectedEntities**: a collection of ProtectedEntity objects (e.g. the 
 set of all TV stations in the United States).
 - **Ruleset**: describes how to protect various entities.
 - **Specification**: describes an experiment in a parametrized way; used to 
 quickly recall or generate data.

Further documentation on each of these modules can be found via step 3 in the
 "Getting started" section.


Current support
---------------

 - Regions
    - Continental United States (2010 census data)
 - Rulesets and protected entities 
    - FCC's 2012 ruleset for TV whitespaces
    - TV, PLMRS, and radioastronomy protections
 - Propagation models
    - FCC's F-curves (without terrain)

I am very interested in expanding support. Please
[send me an email](mailto:harriska@eecs.berkeley.edu) if you'd like to 
collaborate.
