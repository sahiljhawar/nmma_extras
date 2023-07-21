# Repository to add thing which I use in tandem to [NMMA](https://github.com/nuclear-multimessenger-astronomy/nmma)

## Corner plotting
For 2D posterior corner plots, I use [corner.py](https://corner.readthedocs.io/en/latest/). I have modified the code to add a few features which I find useful. It is obvious that while plotting only the posteriors which have same source parameters can be compared.

It can be used to plot single corner plot or multiple corner plots overlaid on top in a single figure. Have a look at different figures generated.

Example usage:
```bash
python ../nmma_extras/plot_all.py -f PChip12dp PChip16dp PChip4dp PChip12dp PChip16dp PChip4dp -p AT2017gfo_ind.prior -o multiple --ext pdf