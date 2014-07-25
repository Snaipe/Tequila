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

From an elevated shell, run `pip install -e git+https://github.com/Snaipe/Tequila.git#egg=tequila`.

You may check if Tequila is installed by running `tequila -h`

## Getting started

Make sure you have properly installed Tequila and all of its dependencies.

1. The first thing you might want to change is the directory where Tequila will manage the servers. 
Tequila will try to read the value of the `TEQUILA_HOME` environment variable, and fallback to the value of default_home
specified inside `/etc/tequila/tequila.conf` if the variable is not defined -- this is why you might want to either set 
the variable in your shell startup file or in `/etc/environment`, or change the value of default_home.

2. To create a server, simply enter `tequila create [server name]`, then navigate to the newly created server directory.
There, you will find 3 files:
    * `application.opts`: the executable jar parameters
    * `jvm.opts`: the Java Virtual Machine parameters
    * `tequila.config`: the server configuration
    
    The `application.opts` and `jvm.opts` can be tuned to fit your specifications.
    `tequila.config` is the configuration file where you will put the repositories, plugins, and server artifacts to use
    during production.
3. Once done, deploy your server using `tequila deploy [server name]`. This will try to resolve, download, and copy all of
the artifacts needed for your server.

4. (Optional) If any artifact could not be resolved, you may manually download and install it using `tequila download [url]`, then run
the deploy command once again to copy it to your server.

5. At that point, you are (almost) done. You may start your server with `tequila start [server name]`, and configure your plugins.

This covers the basic use of Tequila.

For more information on all the available commands, run `tequila -h`, and `tequila [command] -h`.

## Pulling plugins from http://dev.bukkit.org/

Tequila only pulls plugins from maven repositories, but since most (if not all) plugins come from [BukkitDev][bukkitdev],
we made a nice tool called [BlackDog][blackdog].

BlackDog, more than being a nice cocktail made with tequila, is a web service that maps plugins from BukkitDev to a
maven repository structure.

You can set it up somewhere and run it (be it locally or remotely), then add the proper repository inside the configuration
file of your server(s):

    ```
    [repositories]
    ...
    blackdog: http://example.com:port/
    ```
    
... and then reference your plugins as normal maven artifacts:

    ```
    [plugins]
    ...
    plugin-a: local.blackdog:plugin-a:1.0.1
    plugin-b: local.blackdog:plugin-b:2.3.6
    ...
    ```

You might notice that in this example, the group ids are set to `local.blackdog` -- this is a consequence of BlackDog
being 'group-id agnostic': since BukkitDev does not have any group id information, you can pretty much set the group id
to the value you want, and BlackDog will respond accordingly.

There are no limitations on the group id you specify, but we advise you to use something unique such as `local.blackdog`
to prevent the plugin from being pulled from something *other* than BukkitDev.

[logo]: ../graphics/logo.png?raw=true
[python]: https://www.python.org/
[screen]: http://www.gnu.org/software/screen/
[maven]: http://maven.apache.org/
[bukkitdev]: http://dev.bukkit.org/bukkit-plugins/
[blackdog]: http://github.com/Snaipe/BlackDog.git