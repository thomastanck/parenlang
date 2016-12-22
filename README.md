Introduction
------------

This is paren, a Lisp with a lisp.

The only two syntactic characters are `(` and `)`. All other characters are
treated as comments.

Summary
-------

The idea behind paren is to use nested parens to define operators and numbers.
These operators and numbers are then used like in Lisp, but since I don't
actually know Lisp it'll basically be a stupid version of Lisp.

Running tests
-------------

First install `parenlang` with

    python3 setup.py develop

or

    pip3 install parenlang

Then install the dependencies in `parenlangtest/requirements.txt` with

    pip3 -r parenlangtest/requirements.txt

Now you can run the tests by simply running the scripts

    parenlangtest/bench.sh
