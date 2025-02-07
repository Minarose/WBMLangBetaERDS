import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to create a split violin plot
def plot_split_violin(data, x_col, y_col, hue_col, x_labels, filename, y_limits=None):
    """
    Creates a split violin plot comparing two distributions across different categories.

    Args:
        data (DataFrame): The dataset containing the relevant columns.
        x_col (str): Column for x-axis (Age Group).
        y_col (str): Column for y-axis (Coupling Strength).
        hue_col (str): Column for hue (Direction of coupling).
        x_labels (list): Labels for x-axis categories.
        filename (str): Name of the output PNG file.
        y_limits (tuple, optional): Y-axis limits (e.g., (-0.0005, 0.005)).

    Saves:
        The plot as a PNG file.
    """
    plt.figure(figsize=(6, 5), dpi=300)

    # Create the split violin plot with custom styling
    sns.violinplot(
        x=x_col, y=y_col, hue=hue_col, data=data, split=True, gap=0.1,
        palette={'Left to Right': '#e97773', 'Right to Left': 'mistyrose'},
        inner='quart', bw=0.5
    )

    # Formatting
    plt.ylabel('P to I Coupling Strength', fontsize=14)
    plt.xticks(ticks=[0, 1], labels=x_labels, fontsize=12)
    plt.yticks(fontsize=12)

    # Remove top & right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set y-axis limits if provided
    if y_limits:
        plt.ylim(y_limits)

    plt.legend(fontsize=10, loc='lower center')

    # Save and display the plot
    plt.savefig(filename, dpi=300, bbox_inches='tight', format='png')
    plt.show()


# Create the 'Age_Group' column with two categories: young children (4-7) and adolescents (15-18)
bins = [3, 7, 18]  # Age bins for young children (4-7) and adolescents (15-18)
labels = ['4-7 Yrs. Old', '15-18 Yrs. Old']

# Assign age groups based on bins
combined_df['Age_Group'] = pd.cut(combined_df['Age'], bins=bins, labels=labels)

# Reshape the data for violin plot
reshaped_data = pd.melt(
    combined_df, id_vars=['Age_Group'],
    value_vars=['fr_int_p2i_verb_L2R', 'fr_int_p2i_verb_R2L'],
    var_name='Direction', value_name='P to I Coupling Strength'
)

# Rename values in the 'Direction' column for readability
reshaped_data['Direction'] = reshaped_data['Direction'].replace({
    'fr_int_p2i_verb_L2R': 'Left to Right',
    'fr_int_p2i_verb_R2L': 'Right to Left'
})

# ** Plot the violin plot**
plot_split_violin(
    data=reshaped_data, x_col='Age_Group', y_col='P to I Coupling Strength',
    hue_col='Direction', x_labels=labels, filename="p2i_dir.png", y_limits=(-0.0005, 0.005)
)
