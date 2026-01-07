import argparse
import os
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt


def _read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    return rows


def _latest_stats_dir(root="stats_output"):
    if not os.path.isdir(root):
        return None
    dirs = [d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d)]
    if not dirs:
        return None
    return sorted(dirs)[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats_dir", default=None, help="Folder containing stats_frames.csv etc. If omitted: latest in stats_output/")
    ap.add_argument("--real_csv", default=None, help="Optional real data CSV for comparison")
    ap.add_argument("--out", default=None, help="Output folder (default: stats_dir)")
    args = ap.parse_args()

    stats_dir = args.stats_dir or _latest_stats_dir()
    if stats_dir is None:
        raise SystemExit("No stats_output found.")

    frames_path = os.path.join(stats_dir, "stats_frames.csv")
    agents_path = os.path.join(stats_dir, "stats_agents.csv")
    heat_npy = os.path.join(stats_dir, "stats_heatmap.npy")

    out_dir = args.out or stats_dir
    os.makedirs(out_dir, exist_ok=True)

    frames = _read_csv(frames_path)
    t = np.array([float(r["time"]) for r in frames])
    queue_len = np.array([float(r.get("queue_len", 0)) for r in frames])
    entry_rate = np.array([float(r.get("entry_rate_s", 0)) * 60.0 for r in frames])
    exit_rate = np.array([float(r.get("exit_rate_s", 0)) * 60.0 for r in frames])
    inside = np.array([float(r.get("inside_est", 0)) for r in frames])
    density = np.array([float(r.get("density_store", 0)) for r in frames])

    real = None
    if args.real_csv and os.path.isfile(args.real_csv):
        real = _read_csv(args.real_csv)

    def plot_series(y, title, ylabel, fname, y2=None, label2=None):
        plt.figure()
        plt.plot(t, y, label="sim")
        if y2 is not None:
            plt.plot(t, y2, label=label2 or "sim2")
        if real is not None and real and "time_s" in real[0]:
            rt = np.array([float(r["time_s"]) for r in real])
            if fname.startswith("queue") and "queue_len" in real[0]:
                ry = np.array([float(r["queue_len"]) for r in real])
                plt.scatter(rt, ry, s=8, label="real")
            if fname.startswith("flow") and "entries_per_min" in real[0]:
                rin = np.array([float(r["entries_per_min"]) for r in real])
                plt.scatter(rt, rin, s=8, label="real_in")
        plt.title(title)
        plt.xlabel("time (s)")
        plt.ylabel(ylabel)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, fname), dpi=160)
        plt.close()

    plot_series(queue_len, "Queue length over time", "people", "queue_len.png")
    plot_series(entry_rate, "Flow rates (per minute)", "people/min", "flow_rates.png", y2=exit_rate, label2="sim_out")
    plot_series(inside, "Inside (estimated) over time", "people", "inside.png")
    plot_series(density, "Store density over time", "people/m^2", "density.png")

    if os.path.isfile(agents_path):
        agents = _read_csv(agents_path)
        tt = []
        for r in agents:
            v = r.get("travel_time", "")
            if v is None or v == "" or v == "None":
                continue
            tt.append(float(v))
        if tt:
            plt.figure()
            plt.hist(tt, bins=30)
            plt.title("Travel time distribution")
            plt.xlabel("seconds")
            plt.ylabel("count")
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, "travel_time_hist.png"), dpi=160)
            plt.close()

    if os.path.isfile(heat_npy):
        hm = np.load(heat_npy)
        plt.figure()
        plt.imshow(hm, origin="lower", aspect="auto")
        plt.title("Heatmap (person-seconds)")
        plt.colorbar()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "heatmap.png"), dpi=160)
        plt.close()

    print("Saved plots to:", out_dir)


if __name__ == "__main__":
    main()
