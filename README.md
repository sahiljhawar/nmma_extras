# Repository to add scripts, etc which I use in tandem with [NMMA](https://github.com/nuclear-multimessenger-astronomy/nmma)

## Corner plotting
For 2D posterior plots, I use [corner.py](https://corner.readthedocs.io/en/latest/) to generate `sick` corner plots. I have modified the code to add a few features which I find useful. It is obvious that while plotting only the posteriors with same source parameters can be compared.

It can be used to plot single corner plot or multiple corner plots overlaid on top of each other on a single figure. Have a look at different figures in the `examples` folder.

Example usage:
```bash
python ../nmma_extras/plot_all.py -f PChip12dp PChip16dp PChip4dp PChip12dp PChip16dp PChip4dp -p AT2017gfo_ind.prior -o multiple --ext pdf
```

### Note:
The (1D) histograms are not normalised correctly, sometimes the histograms move out of the axes (only in y axis). If you happen to use this script and figure out a way to scale the histrograms correctly, please open a PR.
