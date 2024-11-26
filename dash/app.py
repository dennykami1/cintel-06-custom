import faicons as fa
from plotly.express import line_polar
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

# Load data and compute static values
from shared import app_dir, Depressioncsv
from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly

# Add page title and sidebar
ui.page_opts(title="Insights into Depression & the Workplace", fillable=True)

ICONS = {
    "user": fa.icon_svg("users"),
    "brain": fa.icon_svg("brain"),
    "work": fa.icon_svg("briefcase"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

age_rng = (min(Depressioncsv.Age), max(Depressioncsv.Age))

JOB_SATISFACTION_MAP = {
    1: "Very Dissatisfied",
    2: "Dissatisfied",
    3: "Neutral",
    4: "Satisfied",
    5: "Very Satisfied",
}

with ui.sidebar(open="desktop"):
    ui.h6("This app explores how work-related factors impact mental health, focusing on depression and its connection to work environments.")
    ui.h6("Click on ellipsis icons,  ", ICONS["ellipsis"], ui.br(), "in graph headers to edit variables or axes for additional views of the data.")
    ui.h6("Use the controls below to filter the dataset based on age and gender.")
    ui.hr()
    ui.input_slider(
        "age_slider",
        "Filter Data by Age",
        min=age_rng[0],
        max=age_rng[1],
        value=age_rng,
        pre="",
    )
    ui.input_checkbox_group(
        "Gender_Check",
        "Filter Data by Gender",
        ["Male", "Female"],
        selected=["Male", "Female"],
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")
    


# Add main content

# Define color dictionary
COLOR_DICT = {
    "Yes": "#4cc9f0",
    "No": "#907ad6"
}


#Explore the Data: Use the controls below to filter the dataset based on age and gender.
#Customize Visualizations: Click on the ellipses (...) icons in graph headers to edit variables or axes for a personalized view of the data.
#Understanding Depression in the Workplace: This app explores how work-related factors such as job satisfaction, work pressure, and financial stress impact mental health, focusing on depression and its connection to work environments.

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"]):
        "Count of Individuals with Depression"

        @render.express
        def CountDepressed():
            # Assuming filtereddata() is a reactive function that provides the data
            d = filtereddata()
            
            # Calculate the count of individuals with depression
            depressed_count = len(d[d["Depression"] == "Yes"])  # Adjust column name if necessary
            f"{depressed_count}"

    with ui.value_box(showcase=ICONS["brain"]):
        "Percent of Depressed Individuals"

        @render.express
        def PercentDepressed():
            # Assuming filtereddata() is a reactive function that provides the data
            d = filtereddata()
            
            # Calculate the percentage of depressed individuals (assuming 'depressed' column exists in the data)
            total_individuals = len(d)
            depressed_individuals = len(d[d['Depression'] == 'Yes'])  # Adjust depending on your dataset
            percent_depressed = (depressed_individuals / total_individuals) * 100

            f"{percent_depressed:.2f}%"  # Return the percentage as a formatted string
            

    with ui.value_box(showcase=ICONS["work"]):
        "Average Job Satisfaction"

        @render.express
        def AvgSatisfactionWithDescription():
            # Get the filtered data
            d = filtereddata()

            # Check if data is available
            if d.empty:
                ui.markdown("No data available")
                return

            if "Job Satisfaction" in d.columns:
                # Calculate the average satisfaction level
                avg_satisfaction = d["Job Satisfaction"].mean()
                
                # Round the average to the nearest integer
                rounded_avg = round(avg_satisfaction)
                
                # Map the rounded value to the dictionary
                satisfaction_label = JOB_SATISFACTION_MAP.get(rounded_avg, "Unknown")
                
                # Render the label with average satisfaction value
                ui.markdown(
                    f"**{satisfaction_label}** (Average: {avg_satisfaction:.2f})"
                )
            else:
                ui.markdown("Field 'Job Satisfaction' not found in the dataset")


with ui.layout_columns(col_widths=[6, 6, 12]):
    with ui.card(full_screen=True):
        ui.card_header("Depression Data Frame")

        @render.data_frame
        def table():
            return render.DataGrid(filtereddata())

    with ui.card(full_screen=True):
        with ui.card_header("Visualization of Depression and Work-Related Factors", class_="d-flex justify-content-between align-items-center"):
            
            with ui.popover(title="Edit Radar Variable"):
                ICONS["ellipsis"]
                # Add a radio button to select the Variable
                ui.input_radio_buttons(
                    "Radar_Variable",
                    None,
                    ["Depression", "Family History of Mental Illness", "Have you ever had suicidal thoughts ?"],
                    selected="Depression",  # Set default to "Depression"
                    inline=False,
                )
        @render_plotly
        def spider_plot():
            # Fetch the filtered data
            data = filtereddata()

            # Get the selected radar variable
            radar_variable = input.Radar_Variable()

            # Ensure relevant columns are retained
            selected_data = data[[radar_variable, 'Work Pressure', 'Job Satisfaction', 'Financial Stress']]

            # Group by the selected radar variable and calculate the mean for each group
            grouped_data = selected_data.groupby(radar_variable).mean().reset_index()

            # Prepare data for the radar chart
            radar_data_yes = grouped_data[grouped_data[radar_variable] == 'Yes'].melt(id_vars=[radar_variable], var_name='Metric', value_name='Value')
            radar_data_no = grouped_data[grouped_data[radar_variable] == 'No'].melt(id_vars=[radar_variable], var_name='Metric', value_name='Value')

            # Create the radar chart using Plotly Graph Objects
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=radar_data_yes['Value'],
                theta=radar_data_yes['Metric'],
                fill='toself',
                name=f'{radar_variable}: Yes',
                line_color=COLOR_DICT["Yes"]
            ))

            fig.add_trace(go.Scatterpolar(
                r=radar_data_no['Value'],
                theta=radar_data_no['Metric'],
                fill='toself',
                name=f'{radar_variable}: No',
                line_color=COLOR_DICT["No"]
            ))

            fig.update_layout(
                title=radar_variable,
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(radar_data_yes['Value'].max(), radar_data_no['Value'].max())]
                    )
                ),
                showlegend=True
            )

            return fig

                        

    

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Violin Plot of Categorical Data"
            with ui.popover(title="Change Y Axis Variable"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "cat_variable",
                    "",
                    ["Dietary Habits", "Sleep Duration", "Work Hours"],
                    selected="Work Hours",
                    inline=False,
                )

        @render_plotly
        def tip_perc():
            # Fetch the filtered data
            data = filtereddata()

            # Get the selected variable for the y-axis
            yvar = input.cat_variable()

            # Order the Dietary Habits if selected
            if yvar == "Dietary Habits":
                data[yvar] = pd.Categorical(data[yvar], categories=["Healthy", "Moderate", "Unhealthy"], ordered=True)

            # Create the violin plot using Plotly Express
            fig = px.violin(data, y=yvar, x="Depression", color="Depression", box=True, points="all", hover_data=data.columns,
                            color_discrete_map=COLOR_DICT)

            fig.update_layout(
                title=f"Violin Plot of Depression Data by {yvar}",
                yaxis_title=yvar,
                xaxis_title="",
                legend=dict(
                    orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5
                )
            )

            return fig


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def filtereddata():
    age_range = input.age_slider()  # Get the selected age range from the slider
    print(f"Selected Age Range: {age_range}")  # Debugging: Print selected age range

    # Ensure 'Age' is a numeric column
    if not pd.api.types.is_numeric_dtype(Depressioncsv['Age']):
        Depressioncsv['Age'] = pd.to_numeric(Depressioncsv['Age'], errors='coerce')

    # Apply the filter based on the selected age range
    idx1 = Depressioncsv['Age'].between(age_range[0], age_range[1])
    print(f"Age filter applied: {idx1.sum()} rows")  # Debugging: Number of rows after age filtering

    # Apply the filter based on the Gender field
    idx2 = Depressioncsv['Gender'].isin(input.Gender_Check())  # Correct column name
    print(f"Gender filter applied: {idx2.sum()} rows")  # Debugging: Number of rows after gender filtering

    # Combine both filters and return the filtered data
    return Depressioncsv[idx1 & idx2]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("age_slider", value=age_rng)
    ui.update_checkbox_group("Gender_Check", selected=["Male", "Female"])