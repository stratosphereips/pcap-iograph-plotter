# pcap-iograph-plotter

A script to generate either I/O graph or csv file of protocol statistics in pcap file.
Uses tshark for obtaining the infromation and plotly to generate plots.

## Usage

To use the script you either pass a pcap file or list of pcap files as an argument:

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
                            protocols or for each protocol seperate function.
      -s STEP, --step STEP  Set time step of the graph in seconds. Default is 600
                            seconds.
      -t TSHARK, --tshark TSHARK
                            Specify path to tshark in it is not in PATH.
      -c, --csv             Generate only CSV file.
