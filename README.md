![Tequila][logo]
================

[![Downloads][downloads]][pypi]
[![Python versions][python_versions]][pypi]
[![License][license]](./LICENSE)

**DISCLAIMER: This project is no longer actively maintained. I will still accept pull requests, so feel free to fork the project.**

Tequila is a command-line Minecraft server manager written in python.

It does not aim to be a server wrapper, though it provides a simple one using GNU screen.

It provides some basic functions to create, deploy, and manage multiple servers on the same host.

## Features

* Plugins and server jars are pulled from maven repositories, and are managed as maven dependencies.
* Everything is command-line (no GUI) and can be done over SSH.
* Every server is highly configurable and automated.
* Compatible with all kinds of servers (Bukkit, Vanilla, Spigot, ...)

## Installation

### Prerequisites

* [python 3][python]
* [GNU Screen][screen] (Optional if using a custom server wrapper)
* [Maven 3][maven]

### With the package manager (recommended)

From an elevated shell, run `pip install tequila`.

### From the source code

From an elevated shell, run `pip install -e git+https://github.com/Snaipe/Tequila.git#egg=tequila`.

You may check if Tequila is installed by running `tequila -h`

## Getting started

Make sure you have properly installed Tequila and all of its dependencies.

1. **Configure Tequila's home directory**  
    The first thing you might want to change is the directory where Tequila will manage the servers. 
    Tequila will try to read the value of the `TEQUILA_HOME` environment variable, and fallback to the value of default_home
    specified inside `/etc/tequila/tequila.conf` if the variable is not defined -- this is why you might want to either set 
    the variable in your shell startup file or in `/etc/environment`, or change the value of default_home.

2. **Create a server**  
    To create a server, simply enter `tequila init [server name]`, then navigate to the newly created server directory.
    There, you will find 3 files:
    * `application.opts`: the executable jar parameters
    * `jvm.opts`: the Java Virtual Machine parameters
    * `tequila.config`: the server configuration
    
    The `application.opts` and `jvm.opts` can be tuned to fit your specifications.
    `tequila.config` is the configuration file where you will put the repositories, plugins, and server artifacts to use
    during production.
    
3. **Deploy the server**  
    Once done, deploy your server using `tequila deploy [server name]`. This will try to resolve, download, and copy all of
    the artifacts needed for your server.

5. **Start the server**  
    At that point, you are (almost) done. You may start your server with `tequila start [server name]`, and configure your plugins.

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

As a side note, all artifacts visible on the web service are *releases* and must be considered as such when entering
the plugin version (i.e. don't put '-SNAPSHOT' at the end of the plugin version if you pull the plugin from BlackDog).

## FAQ

**Q: How can I access my server's console ?**  
A: If you left the `wrapper-type` option to 'screen', then Tequila will use [Screen][screen] to manage the server, 
so for the moment you only need to attach to the associated screen.
This may be done with the command `screen -r tequila_<name>`, where `<name>` is your server's name.  
Otherwise, attach to your console using the method provided by your wrapper.

**Q: Help, I attached to the console, but I can't get out !**  
A: You need to detach from the screen by pressing "Ctrl-a, d".

**Q: I changed some settings in tequila.config, how do I update the server again ?**  
A: First, make sure your server is stopped, then run again `tequila deploy <name>`.

**Q: How do I get \<Plugin X\> ?**  
A: See answer below.

**Q: Most plugins are not on maven repositories, how do I get Tequila to download those ?**  
A: Consider using [Blackdog][blackdog] with tequila, or manually download all the needed non-maven dependencies with
`tequila download [url]`. You could also set-up your own maven repository and put all the needed plugins in there.

**Q: Why is Tequila missing \<Insert feature name here\> ?**  
A: We gladly take suggestions on the [issue management system][issues], if you'd like to see a new feature on Tequila
and you're a developer, feel free to fork this repository and submit a pull request -- see section [Contributing](#contributing)
to know how to get yours accepted.

**Q: I have an issue / bug, what do I do ?**  
A: Go to the [issue management system][issues], then search if the problem has already been documented. If not, feel free to open a new ticket.

## Contributing

You need to observe the following rules for pull requests:

* Your modifications must be working and tested.
* Follow python's official formatting rules and be consistent with the project style.
* Squash your commits into one if you can.
* If new files are added, please say so in the commit message, and add the license header.
* Keep your commit messages simple and concise. Good commit messages start with a verb ('Add', 'Fix', ...).
* Your branch must be based off an up-to-date master, or at least must be able to be merged automatically.
* Sign off your pull request message by appending 'Signed-off-by: \<name\> \<email\>' to the message.

By submitting a pull request you accept to license your code under the GNU Public License version 3.

## Donating

If you like Tequila, consider [buying me a beer](https://www.paypal.com/cgi-bin/webscr&cmd=_s-xclick&hosted_button_id=DTNKSED9ZRY3N) !


[logo]: ../graphics/logo.png?raw=true
[downloads]: https://pypip.in/d/tequila/badge.svg
[python_versions]: https://pypip.in/py_versions/tequila/badge.svg
[license]: https://pypip.in/license/tequila/badge.svg

[pypi]: https://pypi.python.org/pypi/tequila/
[python]: https://www.python.org/
[screen]: http://www.gnu.org/software/screen/
[maven]: http://maven.apache.org/
[bukkitdev]: http://dev.bukkit.org/bukkit-plugins/
[blackdog]: http://github.com/Snaipe/BlackDog.git
[issues]: https://github.com/Snaipe/Tequila/issues
