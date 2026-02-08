from agrodesign.plots.interaction_plot import interaction_plot
from agrodesign.plots.mean_plot import mean_plot
from agrodesign.mean_separation.lsd import LSD
from agrodesign.mean_separation.tukey import TukeyHSD
from agrodesign.mean_separation.dmrt import DMRT


def effect_plot(aov, effect, method="tukey", alpha=0.05,
                ylabel=None, title=None, ax=None, show=True):
    """
    Plot main effect OR interaction on provided axis
    """

    # -------------------------
    # Interaction case
    # -------------------------
    if isinstance(effect, (list, tuple)):

        if len(effect) != 2:
            raise ValueError("Currently interaction plot supports 2 factors only")

        fig = interaction_plot(
            aov,
            effect,
            method=method,
            alpha=alpha,
            ylabel=ylabel,
            title=title,
            ax=ax,
            show=show
        )
        return fig

    # -------------------------
    # Main effect case
    # -------------------------
    means = aov.factorial_means(effect)

    if method.lower() == "lsd":
        sep = LSD(aov, effect=effect, alpha=alpha)
        means = sep.test()

    elif method.lower() == "tukey":
        sep = TukeyHSD(aov, effect=effect, alpha=alpha)
        means = sep.test()

    elif method.lower() == "dmrt":
        sep = DMRT(aov, effect=effect, alpha=alpha)
        means = sep.test()

    else:
        raise ValueError("method must be 'lsd', 'tukey', or 'dmrt'")

    fig = mean_plot(
        means,
        ylabel=ylabel,
        title=title,
        ax=ax,
        show=show
    )
    return fig
