# Meet Checker

Run various data-quality checks against a Hytek Meet Manager swim meet database, to identify potentially incorrect times.

## Example Operation

Create config file for a meet, which specifies:

* The location of the meet database file (ie. the .mdb file used by Meet Manager)
* An output file path to which to write its results (html format)
* A set of checks + configurations for those checks to apply.

See config-sample.yaml for an example meet config file.

With a config file created, you can run checkmeet in 2 modes:
* one-off: read the mdb file once, apply checks, generate results and exit
* daemon mode: do this continually, on an interval, updating the results file each time the checks run

Example invocations:

```sh
# run one-off, the location of the .mdb file and the output file are specified in the config file
checkmeet --config /path/to/meet-config.yaml 

# run in daemon mode, with a 60-second refresh interval
checkmeet --config /path/to/meet-config.yaml  --daemon --interval 60
```

## Accessing the data in the .mdb file

The Hytek Meet Manager .mdb file is a generic Access database, *but* with a password applied.  Hytek do not share
what this password is, and without it, it is not possible to open the database with regular database drivers.

Although the database is password protected, the data itself is not encrypted, and the 
[mdb-tools](https://github.com/mdbtools/mdbtools) set of tools can read / export it.  So meetchecker uses the 
mdb-export utility from this suite to dump out raw table data in csv format, read it into pandas dataframes, 
and then do the necessary joins / filtering in pandas.  See datasourcing.py for details.

In order to access the data the .mdb file **cannot be locked**, which means that you cannot have it open in Meet Manager
in single user mode.  ie. If you are accessing the file in Meet Manager while you run checks in the background you 
need to have opened the database in Meet Manager in **Multi-User mode**.

## Html Output files

The output file generated by **checkmeet** comes in 2 versions, which vary only by the order in which it shows events.
For example, if you specify an output file of **/path/to/meetresults.html**, checkmeet will create that file, but also
 **/path/to/meetresults_rev.html**, which will start with the latest event run, and carry on in reverse order to 
 the first event.  This is useful during a meet when you can just monitor the top of the results output to see new
 anomalies as they are detected.

 A second feature of the html files is that they can auto-refresh themselves by adding a ?refresh=1 parameter to 
 the url.  This will cause the browser to reload the page on an interval (currently hardcoded to 30 seconds).  Again
 this can be useful during a meet, where you can keep the browser window open alongside meetmanager and refer to it 
 occasionally as events complete.
 
