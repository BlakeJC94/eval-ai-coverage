import fire

from . import gen_stats, plot_bars, plot_timeline


def main():
    fire.Fire({
        'gen-stats': gen_stats,
        'plot-bars': plot_bars,
        'plot-timeline': plot_timeline,
    })


if __name__ == '__main__':
    main()
