# codalib [![Build Status](https://github.com/unt-libraries/codalib/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/unt-libraries/codalib/actions)
A helper library for [coda](https://github.com/unt-libraries/coda)

## System Requirements

* python-dev (Python 3)
* libxml2-dev
* libxslt-dev

## Development

In order to ease the pain of ensuring the system requirements above are fulfilled on your development machine, codalib provides a Dockerfile which will build the necessary environment for you. 

**To take advantage of this environment you will need to have Docker >= 1.3 installed.**

Clone the repository.
```sh
$ git clone https://github.com/unt-libraries/codalib
$ cd codalib
```

Build the container.

```sh
$ docker build -t unt-libraries/codalib .
```

Run the tests in the container with Pytest.

```sh
$ ./runtests
```

Run the tests in the container with Pytest and custom flags.

```sh
$ ./runtests py.test -s --pdb
```

Run the tests in the container with Tox.

```sh
$ ./runtests tox
```

---

**Optionally, you may just install the system requirements on your development machine.**

If you choose this course of action:

Install the package requirements.

```sh
$ pip install -r requirements-test.txt
```

Run the tests with Pytest.

```sh
$ py.test
```

Run the tests with Tox.

```sh
$ [sudo] pip install tox

$ tox
```

## License

See LICENSE
