![Tequila][logo]
================

Tequila is a command-line Minecraft server manager written in python.

It provides some basic functions to create, deploy, and manage multiple servers on the same host.

## Installation

### Prerequisites

* [python 3][python]
* [GNU Screen][screen]
* [Maven 3][maven]

### With the package manager (recommended)

From an elevated shell, run `pip install tequila`.

### From the source code

From an elevated shell, run `pip install -e git+https://github.com/Snaipe/Tequila.git`.

You may check if Tequila is installed by running `tequila -h`

## Getting started

Make sure you have properly installed Tequila and all of its dependencies.

The first thing you might want to change is the directory where Tequila will manage the servers. 
Tequila will try to read the value of the `TEQUILA_HOME` environment variable, and fallback to `/home/minecraft`
if the variable is not defined -- this is why you might want to set it manually in your shell startup file or in 
`/etc/environment`.

To create a server, simply enter `tequila create [server name]`, then navigate to the newly created server directory.
There, you will find 3 files:

* `application.opts`: the executable jar parameters
* `jvm.opts`: the Java Virtual Machine parameters
* `tequila.config`: the server configuration

The `application.opts` and `jvm.opts` can be tuned to fit your specifications.
`tequila.config` is the configuration file where you will put the repositories, plugins, and server artifacts to use
during production.

Once done, deploy your server using `tequila deploy [server name]`. This will try to resolve, download, and copy all of
the artifacts needed for your server.

If any artifact could not be resolved, you may manually download and install it using `tequila download [url]`, then run
the deploy command once again to copy it to your server.

At that point, you are (almost) done. You may start your server with `tequila start [server name]`, and configure your plugins.

This covers the basic use of Tequila.

For more information on all the available commands, run `tequila -h`, and `tequila [command] -h`.


[logo]: ../graphics/logo.png?raw=true
[python]: https://www.python.org/
[screen]: http://www.gnu.org/software/screen/
[maven]: http://maven.apache.org/