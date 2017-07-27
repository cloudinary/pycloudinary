# Contributing to Pycloudinary

Contributions are welcome and greatly appreciated!

## Reporting a bug

- Ensure that the bug was not already reported by searching in GitHub under [Issues](https://github.com/cloudinary/pycloudinary) and the Cloudinary [Support forms](https://support.cloudinary.com).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/cloudinary/pycloudinary/issues/new).
  Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.
- If you require assistance in the implementation of pycloudinary please [submit a request](https://support.cloudinary.com/hc/en-us/requests/new) in the Cloudinary web site.

## Requesting a feature

We would love to hear your requests!
Please be aware that the package is used in a wide variety of environments and that some features may not be applicable to all users.

- Open a GitHub [issue](https://github.com/cloudinary/pycloudinary) describing the benefits (and possible drawbacks) of the requested feature

## Fixing a bug / Implementing a new feature

- Follow the instructions detailed in [Code contribution](#code-contribution)
- Open a new GitHub pull request
- Ensure the PR description clearly describes the bug / feature. Include the relevant issue number if applicable.
- Provide test code that covers the new code
- Make sure that your code works both with and without Django
- The code should support:
  - Python >= 2.7
  - Django >= 1.4

## Code contribution

When contributing code, either to fix a bug or to implement a new feature, please follow these guidelines:

#### Fork the Project

Fork [project on Github](https://github.com/cloudinary/pycloudinary) and check out your copy.

```
git clone https://github.com/contributor/pycloudinary.git
cd pycloudinary
git remote add upstream https://github.com/cloudinary/pycloudinary.git
```

#### Create a Topic Branch

Make sure your fork is up-to-date and create a topic branch for your feature or bug fix.

```
git checkout master
git pull upstream master
git checkout -b my-feature-branch
```
#### Rebase

If you've been working on a change for a while, rebase with upstream/master.

```
git fetch upstream
git rebase upstream/master
git push origin my-feature-branch -f
```


#### Write Tests

Try to write a test that reproduces the problem you're trying to fix or describes a feature that you want to build. Add to [test](test).

We definitely appreciate pull requests that highlight or reproduce a problem, even without a fix.

#### Write Code

Implement your feature or bug fix.
Try to follow [PEP8](https://pep8.org/).
Make sure that your code works both with and without Django
The code should support:

  - Python >= 2.7
  - Django >= 1.4

Make sure that tests completes without errors.

#### Write Documentation

Document any external behavior in the [README](README.md).

#### Running the tests

Run the basic test suite with::

    CLOUDINARY_URL=cloudinary://apikey:apisecret@cloudname python setup.py test

This only runs the tests for the current environment.
Travis-CI will run the full suite when you submit your pull request.

The full test suite takes a long time to run because it tests multiple combinations of Python and Django.
You need to have Python 2.7, 3.3, 3.4, 3.5, 3.6 installed to run all of the environments. Then run::

    CLOUDINARY_URL=cloudinary://apikey:apisecret@cloudname tox

#### Commit Changes

Make sure git knows your name and email address:

```
git config --global user.name "Your Name"
git config --global user.email "contributor@example.com"
```

Writing good commit logs is important. A commit log should describe what changed and why.

```
git add ...
git commit
```


> Please squash your commits into a single commit when appropriate. This simplifies future cherry picks and keeps the git log clean.

#### Push

```
git push origin my-feature-branch
```

#### Make a Pull Request

Go to https://github.com/contributor/pycloudinary and select your feature branch. Click the 'Pull Request' button and fill out the form. Pull requests are usually reviewed within a few days.
Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

#### Rebase

If you've been working on a change for a while, rebase with upstream/master.

```
git fetch upstream
git rebase upstream/master
git push origin my-feature-branch -f
```

#### Check on Your Pull Request

Go back to your pull request after a few minutes and see whether it passed muster with Travis-CI. Everything should look green, otherwise fix issues and amend your commit as described above.

#### Be Patient

It's likely that your change will not be merged and that the nitpicky maintainers will ask you to do more, or fix seemingly benign problems. Hang on there!

#### Thank You

Please do know that we really appreciate and value your time and work. We love you, really.