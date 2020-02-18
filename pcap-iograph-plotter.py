import subprocess
import argparse
from itertools import cycle

import pandas as pd
from plotly import subplots
import plotly.graph_objs as go


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
        default=["tcp", "udp"],
        help="Network protocols that you want to analyze. Defaults are TCP and UDP.",
    )
    parser.add_argument(
        "-s",
        "--step",
        help="Set time step of the graph in seconds. Default is 1 second.",
        action="store",
        default="1",
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
    ag_count = []
    ag_bytes = []
    for protocol in args.protocols:
        ag_count.append(f"COUNT({protocol.lower()}) {protocol.lower()}")
        ag_bytes.append(f"BYTES() {protocol.lower()}")
    tshark_cmd_count = f"{args.tshark};-r;{pcap};-qz;io,stat,{args.step},\
                {','.join(ag_count)}"
    tshark_cmd_bytes = f"{args.tshark};-r;{pcap};-qz;io,stat,{args.step},\
                {','.join(ag_bytes)}"

    grep_cmd = "grep;-P;" + r"\d+\s+<>[Dur\s+\d+\s*\|\s+\d+]+"

    tmp = []
    for i in range(5, 5 + len(args.protocols)):
        tmp.append(f"${i}")

    awk_cmd = 'awk;-F;[ |]+;{print $4","' + '","'.join(tmp) + "}"

    csv_head = "time," + ",".join(args.protocols)

    return {
        "tshark_count": tshark_cmd_count,
        "tshark_bytes": tshark_cmd_bytes,
        "grep": grep_cmd,
        "awk": awk_cmd,
        "csv_head": csv_head,
    }


def get_statistics(pcap, commands):
    dfs = []
    for tshark_cmd in ["tshark_count", "tshark_bytes"]:
        tshark = subprocess.run(commands[tshark_cmd].split(";"), stdout=subprocess.PIPE)
        if tshark.returncode != 0:
            raise Exception("Tshark count command failed.")

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

        data = commands["csv_head"] + "\n" + awk.stdout.decode()

        dfs.append(
            pd.DataFrame(
                [x.split(",") for x in data.split("\n")[1:]],
                columns=[x for x in data.split("\n")[0].split(",")],
            )
        )
    return dfs


def generate_graphs(df, pcap, protocols):
    colors = {
        "dns": "#636EFA",
        "ipv6": "#EF553B",
        "ssh": "#00CC96",
        "telnet": "#AB63FA",
        "irc": "#19D3F3",
        "tls": "#E763FA",
        "tcp": "#FECB52",
        "udp": "#FFA15A",
        "http": "#FF6692",
    }
    traces_count = []
    traces_bytes = []
    for protocol in protocols:
        traces_count.append(
            go.Scatter(
                name=protocol,
                x=dfs[0].time,
                y=dfs[0][protocol],
                line=dict(color=colors[protocol]),
                xaxis="x1",
                yaxis="y1",
                legendgroup="{}".format(protocol),
                showlegend=True,
            )
        )
        traces_bytes.append(
            go.Scatter(
                name=protocol,
                x=dfs[1].time,
                y=dfs[1][protocol],
                line=dict(color=colors[protocol]),
                xaxis="x1",
                yaxis="y1",
                legendgroup="{}".format(protocol),
                showlegend=False,
            )
        )

    fig = subplots.make_subplots(rows=2, cols=1)

    for trc, trb in zip(traces_count, traces_bytes):
        fig.append_trace(trc, 1, 1)
        fig.append_trace(trb, 2, 1)

    fig["layout"]["xaxis1"].update(title="Time (Seconds)")
    fig["layout"]["xaxis2"].update(title="Time (Seconds)")
    fig["layout"]["yaxis1"].update(title="Packets")
    fig["layout"]["yaxis2"].update(title="Bytes")
    fig.update_layout(title="{}".format(pcap))

    fig.show()


if __name__ == "__main__":

    args = parse_arguments()

    pcaps = [args.file] if args.list is None else args.list.readlines()

    for pcap in pcaps:
        commands = generate_commands(args, pcap.rstrip("\n"))
        dfs = get_statistics(pcap, commands)
        for i, typ in enumerate(["packets", "bytes"]):
            with open(f"{pcap}-{typ}.csv", "w") as f:
                f.write(dfs[i].to_csv(index=False, sep=","))
        if args.csv:
            continue
        generate_graphs(dfs, pcap, list(map(str.lower, args.protocols)))
