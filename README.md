# Eodermdrome interpreter

This projects aim is to develop proof-of-concept eodermdrome language
interpreter that will be used to demonstrate some basic concepts in
computability theory.

For more information about eodermdrome language, follow [this
link](http://esolangs.org/wiki/eodermdrome).


## Installation

The easiest way of installing this package is by using `virtualenv` and
`pip`.  For example, to create new environment in `$HOME/sandbox` and
install interpreter in it, one can execute this:

    $ cd $HOME
    $ virtualenv --no-site-packages sandbox
    $ source sandbox/bin/activate
    $ pip install -e git+https://github.com/tadeboro/eodermdrome.git#egg=eodermdrome

`pip` will take care of installing package and all required
dependencies. Interpreter can now be run by simply executing `runeo`
command.

In order to be able to run programs in debug mode, one also needs
graphviz installed (it is used to produce snapshots of internal state
graph and offers some aid when starting writing programs in
eodermdrome).

It is also possible to use package without installing it. Just make sure
you have `pyparsing` and `graphviz` python packages installed. Now
execute:

    $ git clone https://github.com/tadeboro/eodermdrome.git
    $ cd eodermdrome
    $ PYTHONPATH=".:$PYTHONPATH" python eodermdrome/__init__.py

Last command should display some short instructions on how to properly
invoke interpreter.


## Running programs

Running programs is relativelly simple. Suppose we have our program
written in `prog.eo` file. To execute it like this:

    $ runeo prog.eo

This command will parse program and start executing it. Any output,
produced by program, will be printed to `stdout`.

To run program in debug mode, add a second parameter to invocation:

    $ runeo prog.eo 1

This will again run specified program, but for each command executed, it
will produce pair of files **execi.gv** and **execi.gv.png**, where *i*
is 0, 1, ... Produced images can be used to get information about state
of the program at various stages of execution.

Programs can also process input. To supply input to program, simply pipe
it to `stdin` of interpreter. For example, provided sample program
`add.eo` expects two strings of ones, separated by zero, as input.
This represents two unary numbers that will be added together. Number of
ones output on `stdout` represent sum. To execute this program, one
would run:

    $ runeo add.eo <<< "111011"

Since not all characters can be passed in like in above example, we can
also use `echo` to produce proper data:

    $ echo -e "00111\n101\n" | runeo bct.eo


## Contributing

If you feel like contributing, fork this repo and send me pull request
with changes. Happy hacking!
