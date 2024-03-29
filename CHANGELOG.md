2.1.0
-----

* Fix looping indefinitely in util.waitForURL. [#38](https://github.com/unt-libraries/codalib/pull/38)
* Add support for Node `status` attribute.
* Upgrade for `tzlocal` 3.0 dependency.
* Drop support for now unsupported Python 3.5.
* Replace Travis with GitHub Actions.
* Add support for Python 3.8 and 3.9.

2.0.0
-----

* Upgrade to python3. [#29](https://github.com/unt-libraries/codalib/issues/29)

1.0.3
-----

* More precise element selection in xml-to-object mapping. [#21](https://github.com/unt-libraries/codalib/issues/21)

1.0.2
-----

* Remove hard-coded reference to `bag` collection in Atom feed entry `alt` links. [#18](https://github.com/unt-libraries/codalib/issues/18)

1.0.1
-----

* Add an optional `alt` argument to wrapAtom [#12](https://github.com/unt-libraries/codalib/issues/12).
* Add an optional `alt_type` argument to wrapAtom [#12](https://github.com/unt-libraries/codalib/issues/12).
* Don't write empty `<start/>` and `<end/>` tags in QueueXML. [#9](https://github.com/unt-libraries/codalib/issues/9).
* Use `xs:dateTime` compatible date strings for `lastChecked` elements in bag xml. [#7](https://github.com/unt-libraries/codalib/issues/7).
* Update requirements for simpler environment prep.
* Better error handling for ANVL parsing [#3](http://github.com/unt-libraries/codalib/issues/3)
* Validation for PREMIS Event XML tests


1.0.0
-----

* Initial release.
