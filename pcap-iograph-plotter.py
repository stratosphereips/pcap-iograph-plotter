import subprocess
import argparse
from itertools import cycle

import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file", type=str, help="Pcap file for which you want to create graphs."
    )
    group.add_argument(
        "-l",
        "--list",
        type=argparse.FileType("r"),
        help="File containg the list of pcap files for which you want to create graphs.",
    )
    parser.add_argument(
        "-p",
        "--protocols",
        nargs="+",
        default=["dns", "ipv6", "ssh", "telnet", "irc", "tls", "tcp", "udp", "http"],
        help="Network protocols that you want to analyze. Defaults are TCP and UDP.",
    )
    parser.add_argument(
        "-a",
        "--aggregations",
        nargs="+",
        default=["count"],
        help="Specify aggregation functions to be used by tshark. Specify either one, \
            which should be used for all protocols or for each protocol specift seperate function.",
    )
    parser.add_argument(
        "-s",
        "--step",
        help="Set time step of the graph in seconds. Default is 600 seconds.",
        action="store",
        default="600",
    )
    parser.add_argument(
        "-t",
        "--tshark",
        help="Specify path to tshark if it is not in PATH.",
        default="tshark",
    )
    parser.add_argument(
        "-c", "--csv", help="Generate only CSV file.", action="store_true"
    )

    return parser.parse_args()


def generate_commands(args, pcap):
    stats = []
    for function, protocol in zip(cycle(args.aggregations), args.protocols):
        if function.upper() != "BYTES":
            stats.append(f"{function.upper()}({protocol}) {protocol}")
        else:
            stats.append(f"{function.upper()}() {protocol}")

    tsharkCommand = f"{args.tshark};-r;{pcap};-qz;io,stat,{args.step},\
                {','.join(stats)}"
    grepCommand = "grep;-P;" + r"\d+\s+<>[Dur\s+\d+\s*\|\s+\d+]+"

    tmp = []
    for i in range(5, 5 + len(args.protocols)):
        tmp.append(f"${i}")

    awkCommand = 'awk;-F;[ |]+;{print $4","' + '","'.join(tmp) + "}"

    csvHeader = "time," + ",".join(args.protocols)

    return {
        "tshark": tsharkCommand,
        "grep": grepCommand,
        "awk": awkCommand,
        "header": csvHeader,
    }


def get_statistics(pcap, commands):
    tshark = subprocess.run(commands["tshark"].split(";"), stdout=subprocess.PIPE)
    if tshark.returncode != 0:
        raise Exception("Tshark command failed.")

    grep = subprocess.run(
        commands["grep"].split(";"), stdout=subprocess.PIPE, input=tshark.stdout
    )
    if tshark.returncode != 0:
        raise Exception("Grep command failed.")

    awk = subprocess.run(
        commands["awk"].split(";"), stdout=subprocess.PIPE, input=grep.stdout
    )
    if awk.returncode != 0:
        raise Exception("Awk command failed.")

    data = commands["header"] + "\n" + awk.stdout.decode()

    df = pd.DataFrame(
        [x.split(",") for x in data.split("\n")[1:]],
        columns=[x for x in data.split("\n")[0].split(",")],
    )
    return df


def generate_graphs(df, pcap, protocols):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    size = len(protocols)
    lines = []
    for i in range(0, size):
        protocol = protocols[i]
        lines.append(go.Line(name=protocol.capitalize(), x=df.time, y=df[protocol]))

    fig = go.Figure(data=lines)
    fig.update_layout(title_text=pcap)
    fig.show(renderer="svg")


if __name__ == "__main__":

    args = parse_arguments()

    if len(args.aggregations) != 1 and len(args.aggregations) != len(args.protocols):
        raise Exception(
            "Number of aggregation functions must be either one or same as number of protocols."
        )

    pcaps = [args.file] if args.list is None else args.list.readlines()

    for pcap in pcaps:
        commands = generate_commands(args, pcap.rstrip("\n"))
        df = get_statistics(pcap, commands)
        if args.csv:
            with open(f"{pcap}.csv", "w") as f:
                f.write(df.to_csv(sep=","))
            continue
        generate_graphs(df, pcap, args.protocols)
