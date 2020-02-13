# pcap-iograph-plotter

A script to generate either I/O graph or csv file of protocol statistics in pcap file.
Uses tshark for obtaining the infromation and plotly to generate plots.

## Requirements

This script only requires the [pandas](https://pandas.pydata.org/) library installed to run and get csv file. If you also want to plot the data you need to install (plotly)[https://plot.ly/graphing-libraries/] library.

## Usage

To use the script you either pass a pcap file `(-f)` or list of pcap files `(-l)` as an argument:

    usage: pcap-iograph-plotter.py [-h] (-f FILE | -l LIST)
                                  [-p PROTOCOLS [PROTOCOLS ...]]
                                  [-a AGGREGATIONS [AGGREGATIONS ...]] [-s STEP]
                                  [-t TSHARK] [-c]

    optional arguments:
      -h, --help            show this help message and exit
      -f FILE, --file FILE  Pcap file for which you want to create graphs.
      -l LIST, --list LIST  File containg the list of pcap files for which you
                            want to create graphs.
      -p PROTOCOLS [PROTOCOLS ...], --protocols PROTOCOLS [PROTOCOLS ...]
                            Network protocols that you want to analyze. Defaults
                            are TCP and UDP.
      -a AGGREGATIONS [AGGREGATIONS ...], --aggregations AGGREGATIONS [AGGREGATIONS ...]
                            Specify aggregation functions to be used by tshark.
                            Specify either one, which should be used for all
                            protocols or for each protocol seperate specift function.
      -s STEP, --step STEP  Set time step of the graph in seconds. Default is 600
                            seconds.
      -t TSHARK, --tshark TSHARK
                            Specify path to tshark if it is not in PATH.
      -c, --csv             Generate only CSV file.

## Examples

### Default configuration

To use the basic configuration, which will get you information about most of the procols you simply run:

```shell
pcap-iograph-plotter.py -f [pcap-file]
```

or

```shell
pcap-iograph-plooter.py -l [list-of-pcaps]
```

The output will be plot from plotly for each pcap-file.

### CSV and get statistics only for specific protocols with different step size

To get only csv output of the statistics for specific protocols (Here TCP and UDP) and step size of 60 seconds you would ran:

```shell
pcap-iograph-plotter.py -f [pcap-file] -p tcp udp -s 60 -c
```

The location of the csv file is the same as of the `pcap-file` and its name is `pcap-file.csv`. Here is the example content of the csv file:

```csv
,time,tcp,udp
0,60,1661,671
1,120,1659,668
2,180,1648,674
3,240,1659,661
4,300,1665,669
5,360,1666,648
6,420,1657,644
7,480,1662,655
8,540,1684,640
9,600,1645,644
10,660,1667,640
11,720,1666,656
12,780,1636,646
.
.
.
```

### Change the aggregation function for tshark and get statistics only for specific protocols

By default the aggregation function used for each protocol is `COUNT` you can change to any other aggregation function `COUNT|SUM|MIN|MAX|AVG|LOAD|FRAME|BYTES`. Details on the functions can be found in [tshark documentation](https://www.wireshark.org/docs/man-pages/tshark.html).

Change the aggregation function for both TCP and UDP to `BYTES`:

```shell
pcap-iograph-plotter.py -f [pcap-file] -p tcp udp -a bytes
```

or to change thr aggregation function only for UDP to `BYTES` and keep `COUNT` for tcp:

```shell
pcap-iograph-plotter.py -f [pcap-file] -p tcp udp -a count bytes
```