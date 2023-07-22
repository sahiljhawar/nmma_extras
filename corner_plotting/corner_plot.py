import corner
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import seaborn as sns
import matplotlib.patches as mpatches
import re

params = {
    # latex
    "text.usetex": True,
    # fonts
    "mathtext.fontset": "stix",
    # figure and axes
    "figure.figsize": (14, 7),
    "figure.titlesize": 35,
    "axes.grid": False,
    "axes.titlesize": 10,
    "axes.labelsize": 40,
    # tick markers
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "xtick.major.size": 10.0,
    "ytick.major.size": 10.0,
    "xtick.minor.size": 3.0,
    "ytick.minor.size": 3.0,
    # legend
    "legend.fontsize": 20,
}
plt.rcParams.update(params)
plt.rcParams["font.serif"] = ["Computer Modern"]
plt.rcParams["font.family"] = ["serif", "STIXGeneral"]
plt.rcParams["savefig.bbox"] = None
plt.rcParams.update({"font.size": 22})


def plotting_parameters(prior_filename):
    """
    Extract plotting parameters and latex representation from the given prior file.
    Keys will be used as column names for the posterior samples and values will be used as axis labels.
    Parameters
    ----------
    prior_filename : str
        The file path of the prior file.
    Returns
    -------
    dict
        A dictionary containing the plotting parameters.
    """
    parameters = {}
    with open(prior_filename, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                key_value = line.split("=")
                key = key_value[0].rstrip()
                parameters[key] = (
                    key_value[-1].replace(")", "").replace("\\\\", "\\").strip("'")
                )
        extra_em_sys_pattern = r"em_syserr_val_([a-z]+|[A-Z]+|[0-9]+)"
        extra_params = [
            col for col in parameters.keys() if re.match(extra_em_sys_pattern, col)
        ]
        parameters_to_ignore = []
        for k, v in parameters.items():
            try:
                parameters[k] = float(v.strip())
                parameters_to_ignore.append(k)
            except ValueError:
                pass
        parameters_to_ignore += extra_params
        for param in parameters_to_ignore:
            if param in parameters:
                del parameters[param]
    return parameters


def load_csv(filename_with_fullpath, prior_filename):
    """
    Load posterior samples from a CSV file.
    Parameters
    ----------
    filename_with_fullpath : str
        The file path of the posterior samples in CSV format.
    prior_filename : str
        The file path of the prior file to crossmatch the parameters and only load the (astrophysical) source parameters.
    Returns
    -------
    numpy.ndarray
        A 2D numpy array representing the posterior samples.
    """
    df = pd.read_csv(
        filename_with_fullpath + "/injection_posterior_samples.dat", sep=" "
    )
    columns = plotting_parameters(prior_filename).keys()
    df = df[[col for col in columns if col in df.columns]]
    samples = np.vstack(df.values)
    return samples


def load_injection(prior_filename, injection_file_json):
    """
    Load injection data from a JSON file. (Not useful incase of real data)
    Parameters
    ----------
    prior_filename : str
        The file path of the prior file.
    injection_file_json : str
        The file path of the injection JSON file.
    Returns
    -------
    numpy.ndarray
        A 1D numpy array representing the injection data to be used as truths.
    """
    df = pd.read_json(injection_file_json)
    df = df.from_records(df["injections"]["content"])
    columns = plotting_parameters(prior_filename).keys()
    df = df[[col for col in columns if col in df.columns]]
    samples = np.vstack(df.values).flatten()
    return samples


def corner_plot(data, labels, filename, truths, legendlabel, ext, **kwargs):
    """
    Generate a corner plot for one or multiple datasets.
    Parameters
    ----------
    data : list of numpy.ndarray
        A list of 2D numpy arrays representing multiple datasets.
    labels : dict
        A dictionary containing the labels for each dimension in the datasets. Comes from the plotting_parameters function.
    filename : str
        The file path for saving the corner plot image.
    truths : numpy.ndarray or None
        A 1D numpy array representing the truth values (optional).
    legendlabel : list of str
        A list of legend labels for each dataset.
    ext : str
        The output file extension for the image (e.g., "png", "pdf").
    **kwargs
        Additional keyword arguments for the corner plot.
    Returns
    -------
    None
    """
    cwd = os.getcwd()
    folder_name = "images/"
    check = os.path.dirname(cwd + "/" + folder_name)
    if os.path.exists(check):
        os.chdir(check)
    elif not os.path.exists(check):
        os.makedirs(check)
        os.chdir(check)
    if truths is None:
        truth_values = None
    else:
        truth_values = truths[:, 0]
    color_array = sns.color_palette("deep", n_colors=len(data), desat=0.8)
    limits = (
        (32, 45),
        (30, 80),
        (0, np.pi / 2.0),
        (-2.7, -2.2),
        (-1.45, -1.15),
        (0.48, 8),
    )
    fig = corner.corner(
        data[0],
        labels=list(labels.values()),
        quantiles=[0.16, 0.84],
        title_quantiles=[[0.16, 0.5, 0.84] if len(data) == 1 else None][0],
        show_titles=[True if len(data) == 1 else False][0],
        range=[0.99] * (data[0].shape[1]),
        bins=40,
        color=color_array[0],
        max_n_ticks=3,
        # weights=np.ones(len(data[0])) / len(data[0]),
        hist_kwargs={"density": True, "zorder": len(data)},
        contourf_kwargs={
            "zorder": len(data),
        },
        contour_kwargs={"zorder": len(data)},
        **kwargs,
    )
    axes = fig.get_axes()
    plt.rcParams.update({"font.size": 14})
    for i in range(1, len(data)):
        fig = corner.corner(
            data[i],
            labels=list(labels.values()),
            quantiles=[0.16, 0.84],
            # range=limits,
            range=[0.999] * (data[i].shape[1]),
            bins=40,
            max_n_ticks=3,
            fig=fig,
            color=color_array[i],
            # weights=np.ones(len(data[i])) / len(data[i]),
            hist_kwargs={"density": True, "zorder": len(data) - i},
            contourf_kwargs={"zorder": len(data) - i},
            contour_kwargs={"zorder": len(data) - i},
            **kwargs,
        )
    # Legend
    if all("$" not in i for i in legendlabel):
        legendlabel = [i.split("/")[0].replace("_", " ") for i in legendlabel]
    else:
        legendlabel = [i.split("/")[0] for i in legendlabel]
    lines = []
    for i in range(len(legendlabel)):
        lines.append(
            mpatches.Rectangle(
                (0, 0),
                1,
                1,
                facecolor=color_array[i],
                edgecolor=color_array[i],
                alpha=0.5,
                lw=2,
            )
        )
    axes[2 * int(np.sqrt(len(axes))) - 2].legend(
        lines, legendlabel, loc=3, frameon=True, fancybox=True
    )
    if len(data) == 2:
        title_quantiles_1 = []
        title_quantiles_2 = []
        for i in range(data[0].shape[1]):
            qs1 = corner.quantile(data[0].T[i], [0.16, 0.5, 0.84])
            qs2 = corner.quantile(data[1].T[i], [0.16, 0.5, 0.84])
            q_up1, q_bottom1, qmid1 = qs1[1] - qs1[0], qs1[2] - qs1[1], qs1[1]
            q_up2, q_bottom2, qmid2 = qs2[1] - qs2[0], qs2[2] - qs2[1], qs2[1]
            title_quantiles_1.append([qmid1, q_up1, q_bottom1])
            title_quantiles_2.append([qmid2, q_up2, q_bottom2])
        for i in range(0, len(axes), np.sqrt(len(axes)).astype(int) + 1):
            coords = axes[i].title.get_position()
            axes[i].text(
                x=coords[0],
                y=1.05 * coords[1],
                s=r"${{{0:.2f}}}_{{-{1:.2f}}}^{{+{2:.2f}}}$  ".format(
                    *title_quantiles_1[i // np.sqrt(len(axes)).astype(int)]
                ),
                ha="right",
                color=color_array[0],
                transform=axes[i].transAxes,
            )
            axes[i].text(
                x=coords[0],
                y=1.05 * coords[1],
                s=r"${{{0:.2f}}}_{{-{1:.2f}}}^{{+{2:.2f}}}$".format(
                    *title_quantiles_2[i // np.sqrt(len(axes)).astype(int)]
                ),
                ha="left",
                color=color_array[1],
                transform=axes[i].transAxes,
            )
    fig.savefig(filename, format=ext, bbox_inches="tight", dpi=300)
    print("Saved corner plot:", filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate corner plot")
    parser.add_argument(
        "-f",
        "--posterior_files",
        type=str,
        nargs="+",
        help="CSV file path for posteriors",
    )
    parser.add_argument(
        "-p", "--prior_filename", type=str, help="Prior file path for axes labels"
    )
    parser.add_argument(
        "-l",
        "--label_name",
        type=str,
        nargs="+",
        help="Legend labels (if in latex, use '$label$') or else just use the posterior folder names",
    )
    parser.add_argument(
        "-i", "--injection_json", type=str, help="Injection JSON file path"
    )
    parser.add_argument(
        "-e",
        "--ext",
        default="png",
        type=str,
        help="Output file extension. Default: png",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        type=str,
        help="output file name. If not provided, will be concatenation of input file names",
    )
    args = parser.parse_args()
    posterior_files = args.posterior_files
    prior_filename = args.prior_filename
    injection_json = args.injection_json
    label_name = args.label_name
    ext = args.ext
    output = args.output
    # Generate legend labels from input file names
    legendlabel = []
    if label_name is not None:
        for i in label_name:
            legendlabel.append(i)
    else:
        legendlabel = [file for file in posterior_files]
    # Load posteriors from CSV files
    posteriors = []
    for file in posterior_files:
        posterior = load_csv(file, prior_filename)
        posteriors.append(posterior)
    if injection_json is not None:
        truths = load_injection(prior_filename, injection_json)
    else:
        truths = None
    labels = plotting_parameters(prior_filename)
    folder_name = os.path.dirname(posterior_files[0])
    _filename = [file for file in posterior_files]
    name = "_VS_".join([j for j in _filename])
    if len(posterior_files) == 1:
        output_prefix = output if output is not None else name
    else:
        output_prefix = "multi_" + (output if output is not None else name)
    output_filename = output_prefix + "." + ext
    kwargs = dict(
        plot_datapoints=False,
        plot_density=False,
        plot_contours=True,
        fill_contours=True,
        truth_color="black",
        label_kwargs={"fontsize": 14},
        levels=[0.16, 0.5, 0.84],
        smooth=0.9,
    )
    corner_plot(posteriors, labels, output_filename, truths, legendlabel, ext, **kwargs)
