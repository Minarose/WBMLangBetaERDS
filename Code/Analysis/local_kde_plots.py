import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_kde_with_adjustment(df_young, df_adol, var, xlabel, filename, adjust_young=False):
    """
    Plots Kernel Density Estimation (KDE) of local inhibition (c4_verb) for young children and adolescents.
    Includes adjusted KDEs where the mean difference between groups is accounted for.

    Args:
        df_young (DataFrame): Data for young children.
        df_adol (DataFrame): Data for adolescents.
        var (str): Column name representing the variable to plot.
        xlabel (str): Label for the x-axis.
        filename (str): Name of the output file.
        adjust_young (bool): If True, adjusts young children's values; otherwise, adjusts adolescents'.

    Saves:
        A KDE plot as a PNG file.
    """
    # Calculate the mean difference between age groups
    mean_young = df_young[var].mean()
    mean_adol = df_adol[var].mean()
    mean_diff = abs(mean_adol - mean_young)

    # Adjust values based on the specified group
    if adjust_young:
        df_young['adjusted_' + var] = df_young[var] - mean_diff
    else:
        df_adol['adjusted_' + var] = df_adol[var] + mean_diff

    # Initialize the figure
    plt.figure(figsize=(5, 4), dpi=300)

    # KDE for Young Children
    sns.kdeplot(df_young[var], color='mediumaquamarine', label='Young Children (Before)', fill=True, alpha=0.3)
    plt.axvline(df_young[var].mean(), color='aquamarine', linestyle='-', linewidth=2)

    # KDE for Adolescents
    sns.kdeplot(df_adol[var], color='lightpink', label='Adolescents (Before)', fill=True, alpha=0.3)
    plt.axvline(df_adol[var].mean(), color='lightpink', linestyle='-', linewidth=2)

    # KDE for Adjusted Group
    adjusted_label = 'Young Children (After)' if adjust_young else 'Adolescents (After)'
    adjusted_color = 'xkcd:teal' if adjust_young else 'palevioletred'

    sns.kdeplot(df_young['adjusted_' + var] if adjust_young else df_adol['adjusted_' + var],
                color=adjusted_color, label=adjusted_label, fill=True, alpha=0.3)
    plt.axvline((df_young if adjust_young else df_adol)['adjusted_' + var].mean(),
                color=adjusted_color, linestyle='-.', linewidth=2)

    # Customize plot aesthetics
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=6, loc='upper left', frameon=False)

    # Remove top & right spines
    sns.despine()

    # Save and show the plot
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', format='png')
    plt.show()


# ** Plot for Adolescents (Adjusting Adolescents)**
plot_kde_with_adjustment(
    df_young=young_children, df_adol=adolescents, var='c4_verb',
    xlabel='Local I to P Coupling Strength', filename="adol_change_local_i2p_kde_combined.png",
    adjust_young=False  # Adjust adolescents
)

# ** Plot for Young Children (Adjusting Young Children)**
plot_kde_with_adjustment(
    df_young=young_children, df_adol=adolescents, var='c4_verb',
    xlabel='Local I to P Coupling Strength', filename="YC_change_local_i2p_kde_combined.png",
    adjust_young=True  # Adjust young children
)
