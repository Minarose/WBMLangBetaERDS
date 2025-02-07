import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression



# Function to plot linear regression between two variables
def plot_regression(x, y, x_label, y_label, filename, color, marker='o', linestyle='--', ylim=None):
    """
    Plots a regression scatter plot with a fitted regression line.
    
    Args:
        x (array-like): Independent variable (X-axis).
        y (array-like): Dependent variable (Y-axis).
        x_label (str): Label for X-axis.
        y_label (str): Label for Y-axis.
        filename (str): Name of the file to save the plot.
        color (str): Color for scatter points and regression line.
        marker (str): Marker style for scatter points.
        linestyle (str): Line style for regression line.
        ylim (tuple, optional): Y-axis limits for the plot.
    
    Saves:
        The plot as a PNG file.
    """
    # Compute linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Create the plot
    plt.figure(figsize=(6, 5), dpi=300)
    sns.regplot(
        x=x, y=y,
        scatter_kws={'color': color, 's': 50, 'marker': marker},
        line_kws={'color': color, 'linestyle': linestyle, 'label': f'r={r_value:.2f}, p={p_value:.3f}'}
    )

    # Formatting
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.xticks(fontsize=12, rotation=45)
    plt.yticks(fontsize=12)
    
    # Remove top & right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if ylim:
        plt.ylim(ylim)

    plt.legend(fontsize=12)
    
    # Save and display the plot
    plt.savefig(filename, dpi=300, bbox_inches='tight', format='png')
    plt.show()


# Load parameters
all_data = params_df  

# Define Y-axis limits for LI plots
li_ylim = (-0.6, 0.6)

### ** 1. Age vs. P to I Coupling**
plot_regression(
    x=all_data['Age'], y=all_data['fr_int_p2i_verb'],
    x_label='Age', y_label='P to I Coupling Strength',
    filename="p2i_age.png", color='#e97773'
)


### ** 2. Age vs. P to P Coupling**
plot_regression(
    x=all_data['Age'], y=all_data['fr_int_p2p_verb'],
    x_label='Age', y_label='P to P Coupling Strength',
    filename="p2p_age_noun.png", color='#6a9ef9'
)

### ** 3. Age vs. P to E Coupling **
plot_regression(
    x=all_data['Age'], y=all_data['fr_int_p2e_verb'],
    x_label='Age', y_label='P to E Coupling Strength',
    filename="p2e_age_noun.png", color='#6aab98'
)

# Function to compute residuals by regressing out the effect of Age
def compute_residuals(y, control):
    """
    Regresses out the effect of a control variable (e.g., Age) from the dependent variable.

    Args:
        y (array-like): Dependent variable (e.g., Laterality Index).
        control (array-like): Control variable (e.g., Age).

    Returns:
        residuals (array-like): Age-independent residuals of y.
    """
    model = LinearRegression().fit(control.values.reshape(-1, 1), y)
    residuals = y - model.predict(control.values.reshape(-1, 1))
    return residuals

# Function to plot regression after controlling for Age
def plot_regression(x, y_residual, x_label, filename, color, marker='o', linestyle='--'):
    """
    Plots a scatter plot with linear regression line after controlling for Age.

    Args:
        x (array-like): Independent variable (X-axis).
        y_residual (array-like): Age-independent dependent variable (Y-axis).
        x_label (str): Label for X-axis.
        filename (str): Name of the file to save the plot.
        color (str): Color for scatter points and regression line.
        marker (str, optional): Marker style for scatter points.
        linestyle (str, optional): Line style for regression line.

    Saves:
        The plot as a PNG file.
    """
    # Compute linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y_residual)

    # Create the plot
    plt.figure(figsize=(6, 5), dpi=300)
    sns.regplot(
        x=x, y=y_residual,
        scatter_kws={'color': color, 's': 50, 'marker': marker},
        line_kws={'color': color, 'linestyle': linestyle, 'label': f'r={r_value:.2f}, p={p_value:.3f}'}
    )

    # Formatting
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel('Age-Independent Laterality Index', fontsize=14)
    plt.xticks(fontsize=12, rotation=45)
    plt.yticks(fontsize=12)
    
    # Remove top & right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.ylim(-0.6, 0.6)
    plt.legend(fontsize=12)

    # Save and display the plot
    plt.savefig(filename, dpi=300, bbox_inches='tight', format='png')
    plt.show()


# Load parameters
all_data = params_df  

# Define the control variable (Age) and compute residuals for Laterality Index (LI)
control_variable = all_data['Age']
y_residual = compute_residuals(all_data['t_LI_sim'], control_variable)

### ** 1. P to I Coupling vs. Laterality Index (Age-Independent)**
plot_regression(
    x=all_data['fr_int_p2i_verb'], y_residual=y_residual,
    x_label='P to I Coupling Strength', filename="p2i_lat_nounPC.png",
    color='#e97773'
)

### **2. P to P Coupling vs. Laterality Index (Age-Independent)**
plot_regression(
    x=all_data['fr_int_p2p_verb'], y_residual=y_residual,
    x_label='P to P Coupling Strength', filename="p2p_lat_nounPC.png",
    color='#6a9ef9'
)

### ** 3. P to E Coupling vs. Laterality Index (Age-Independent)**
plot_regression(
    x=all_data['fr_int_p2e_verb'], y_residual=y_residual,
    x_label='P to E Coupling Strength', filename="p2e_lat_nounPC.png",
    color='#6aab98'
)
