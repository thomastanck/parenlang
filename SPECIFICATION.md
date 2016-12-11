`paren` Specification
=====================

Introduction
------------

`paren`, as its name suggests, relies heavily on `paren`s (parentheses). It's
a not so subtle nod to Lisp's so called "crazy brackets". It turns out however,
that "crazy brackets" aren't so bad, as `paren` is a perfectly readable language
especially suitable for systems and web programming.

Character set
-------------

`paren`'s philosophy is simplicity and power. The simpler something is, the
fewer bugs it has, and chances are, the faster it'll run. In a similar vein, the
more powerful a language is, the more extensible it is, the more freedom you
will get as a programmer, and the more efficient you will be. `paren` is
designed with these two goals in mind, and is now the fastest, most error
resistant, and most efficient language.

This is why `paren` only uses two characters in its character set, `(` and `)`,
as having more characters only increases the chances of a typo and easily
creates crashing builds, which is obviously no good. All other characters raise
an error in development as `paren` adopts a fail-fast philosophy. However, in
production, non `paren`s are gracefully handled by the interpreter and thus will
not crash your services if a developer accidentally commits a stray non `paren`.
