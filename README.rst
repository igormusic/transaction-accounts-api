Transaction Accounts API
==================================================

This is a `transaction-accounts <https://pypi.org/project/transaction-accounts/>`_  example application.

To run locally you need to set value of ACCOUNTS_DB_URL environment variable to the database connection string.

.. code-block:: bash

    export ACCOUNTS_DB_URL=postgresql://postgres:postgres@localhost:5432/accounts

You will also need to create accounts database.

Run
---

Build the Docker image:

.. code-block:: bash

   docker-compose build

Run the docker-compose environment:

.. code-block:: bash

    docker-compose up

After that visit http://127.0.0.1:8000/docs in your browser.

Test
----

This application comes with the unit tests.

To run the tests do:

.. code-block:: bash

   docker-compose run --rm webapp py.test webapp/tests.py --cov=webapp

The output should be something like:

.. code-block::

   platform linux -- Python 3.10.0, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
   rootdir: /code
   plugins: cov-3.0.0
   collected 7 items

   webapp/tests.py .......                                         [100%]

   ---------- coverage: platform linux, python 3.10.0-final-0 ----------
   Name                     Stmts   Miss  Cover
   --------------------------------------------
   webapp/__init__.py           0      0   100%
   webapp/application.py       12      0   100%
   webapp/containers.py        10      0   100%
   webapp/database.py          24      8    67%
   webapp/endpoints.py         32      0   100%
   webapp/models.py            10      1    90%
   webapp/repositories.py      36     20    44%
   webapp/services.py          16      0   100%
   webapp/tests.py             59      0   100%
   --------------------------------------------
   TOTAL                      199     29    85%
