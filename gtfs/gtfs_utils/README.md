Get Started!
------------

Ready to contribute? Here's how to set up `gtfs_utils` for local development.

1. Fork the `open-bus` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/open-bus.git

3. Install your local copy into a virtual env (with conda or virtualenv)::
    $ mkvirtualenv open-bus OR conda create -n open-bus
    $ conda activate open-bus
    $ cd open-bus/
    $ python setup.py develop
    If you experience issues installing `Shapely` see https://pypi.org/project/Shapely/#downloads
4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ python setup.py test or py.test

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.

Tips
----

To run a subset of tests::

$ py.test tests.test_utils
