========
ninjadog
========


.. image:: https://img.shields.io/pypi/v/ninjadog.svg
        :target: https://pypi.org/project/ninjadog/

.. image:: https://img.shields.io/travis/knowsuchagency/ninjadog.svg
        :target: https://travis-ci.org/knowsuchagency/ninjadog

.. image:: https://pyup.io/repos/github/knowsuchagency/ninjadog/shield.svg
     :target: https://pyup.io/repos/github/knowsuchagency/ninjadog/
     :alt: Updates

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg

`Pug`_ template (formerly `jade`_) support in Python


* Documentation: http://journalpanic.com/ninjadog
* GitHub: https://github.com/knowsuchagency/ninjadog



Installation
------------

ninjadog requires Python 3, node-js, npm, and the `pug-cli`_ library

::

    brew install npm
    npm install -g pug-cli
    pip install ninjadog


For use with `Pyramid`_, just add it to the configuration

.. code-block:: python

    config.include('ninjadog')


Usage
-----

ninjadog leverages the `pug-cli`_ library, written in nodejs, to render
`pug`_ templates in Python.

It allows you to take something like this

.. code-block:: pug

    html
        head
            title my pug template
        body
            #content
                h1 Hello #{name}
                .block
                    input#bar.foo1.foo2
                    input(type="text", placeholder="your name")
                    if name == "Bob"
                        h2 Hello Bob
                    ul
                        for book in books
                            li= book
                        else
                            li sorry, no books


and sprinkle some Python over it

.. code-block:: python

    from ninjadog import render

    context = {
        'name': 'Bob',
        'books': ['coloring book', 'audio book', "O'Reilly book"],
        'type': 'text',
    }

    print(render(file=filepath, context=context, pretty=True))

to render this

.. code-block:: html

    <!DOCTYPE html>
    <html>
      <head>
        <title>my pug template</title>
      </head>
      <body>
        <div id="content">
          <h1>Hello Bob</h1>
          <div class="block">
            <input class="foo1 foo2" id="bar">
            <input type="text" placeholder="your name">
            <h2>Hello Bob</h2>
            <ul>
              <li>coloring book</li>
              <li>audio book</li>
              <li>O'Reilly book</li>
            </ul>
          </div>
        </div>
      </body>
    </html>


You can even combine `jinja2`_ syntax for unparalleled
template-rendering power.

.. code-block:: python


    from ninjadog import render


    def stop_believing():
        return False


    context = {
        'stop_believing': stop_believing,
        'happy': {
            'birthday': 'today',
        }
    }

    template_string = """
    h1 hello, world
    if happy.birthday == 'today'
        p it's time to celebrate!
        p {{ "Don't" if not stop_believing() }} stop believing
    """

    print(render(template_string,
                 context=context,
                 pretty=True,
                 with_jinja=True))



.. code-block:: html

    <h1>hello, world</h1>
    <p>it's time to celebrate!</p>
    <p>Don't stop believing</p>


Why?
----

`Pug`_ templates are a super elegant and expressive way to write
html, IMO.

There exists a project, `pyjade`_ and a less-popular fork, `pypugjs`_,
that are pure-python implementations of the pug template engine,
but they have some minor bugs and the maintenance is a bit lacking.

I figured it would be good to have an alternative method to render
`pug`_ templates that used the native javascript rendering engine.

ninjadog does this by spawning the `pug cli`_ as a subprocess.
This means that it can't be as fast as a native template engine
like `pyjade`_, but it will likely be more reliable over time as
it's leveraging the popular and well-maintained nodejs implementation.


Gotchas
-------

Currently, rendering a template with `jinja2`_ syntax goes through the following process:

1. Render elements on the initial template through `jinja2`_
2. Pass the output to the `pug-cli`_, gathering extensions and inclusions in the process
3. Render the output through `jinja2`_ again, since the original template may have extended or included other templates that countained `jinja2`_ syntax themselves.

What this means is that if you want to escape `jinja2`_ syntax, you need to do it twice.

For example, to have a literal ``{{ escaping inception }}`` rendered,
you'll need to have ``{{ "{{ '{{ escaping inception }}' }}" }}`` in your template.

对不起


.. _pug: https://pugjs.org/api/getting-started.html
.. _jade: https://naltatis.github.io/jade-syntax-docs/
.. _pyjade: https://github.com/syrusakbary/pyjade
.. _pypugjs: https://github.com/matannoam/pypugjs
.. _pug-cli: https://www.npmjs.com/package/pug-cli
.. _pug cli: https://www.npmjs.com/package/pug-cli
.. _jinja2: http://jinja.pocoo.org/
.. _jinja 2: http://jinja.pocoo.org/
.. _pyramid: https://trypyramid.com/
