pool = pd.DataFrame(columns=['Functional Area Desc', 'Company Insider Type', 'Reporting_Level_Group', 'Region',  'Email - Work'])

treatment_df = df_cross[df_cross['treatment_group']==1]
control_df = df_cross[df_cross['treatment_group']==0]
treatment_counts = treatment_df.groupby(['Functional Area Desc', 'Company Insider Type', 'Reporting_Level_Group', 'Region']).size().reset_index(name='TreatmentCount')
control_counts = control_df.groupby(['Functional Area Desc', 'Company Insider Type', 'Reporting_Level_Group', 'Region']).size().reset_index(name='ControlCount')
counts = pd.merge(treatment_counts, control_counts, on=['Functional Area Desc', 'Company Insider Type', 'Reporting_Level_Group', 'Region'], how='outer').fillna(0)
counts[counts['TreatmentCount']>0]

# 1st round matching: exact matching
matched_control_df = pd.DataFrame(columns=['Functional Area Desc', 'Company Insider Type', 'Reporting_Level_Group', 'Region',  'Email - Work'])
for _, row in counts.iterrows():
    treatment_count = int(row['TreatmentCount'])
    control_count = int(row['ControlCount'])
    combination_filter = (
        (control_df['Functional Area Desc'] == row['Functional Area Desc'])
        & (control_df['Company Insider Type'] == row['Company Insider Type'])
        & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
        & (control_df['Region'] == row['Region'])
    )
    if treatment_count <= control_count:
        matched = control_df[combination_filter].sample(n=treatment_count, random_state=42)
        matched_control_df = pd.concat([matched_control_df, matched])
        pool = pd.concat([pool,control_df[combination_filter].drop(matched.index)])
    else:
        matched = control_df[combination_filter]
        matched_control_df = pd.concat([matched_control_df, matched])
print(matched_control_df.shape)
print(treatment_df.shape)
print(control_df.shape)

print(pool.shape)

# 2nd round matching: loosen criteria
for _, row in counts.iterrows():
    treatment_count = int(row['TreatmentCount'])
    control_count = int(row['ControlCount'])
    if treatment_count > control_count:
        additional_needed = treatment_count - control_count
        additional_from_pool1 = pool[
        (
            (control_df['Functional Area Desc'] == row['Functional Area Desc'])
            & (control_df['Company Insider Type'] == row['Company Insider Type'])
            & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
        )
        |
        (
            (control_df['Functional Area Desc'] == row['Functional Area Desc'])
            & (control_df['Company Insider Type'] == row['Company Insider Type'])
            & (control_df['Region'] == row['Region'])
        )
        |
        (
            (control_df['Functional Area Desc'] == row['Functional Area Desc'])
            & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
            & (control_df['Region'] == row['Region'])
        )
        |
        (
            (control_df['Company Insider Type'] == row['Company Insider Type'])
            & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
            & (control_df['Region'] == row['Region'])
        )
        ]
        additional1 = additional_from_pool1.shape[0]
        if additional1 >= additional_needed:
            drawed1 = additional_from_pool1.sample(n=additional_needed, random_state=42)
            pool = pool.drop(drawed1.index)
            matched_control_df = pd.concat([matched_control_df, drawed1])
        else:
            drawed1 = additional_from_pool1
            pool = pool.drop(drawed1.index)
            matched_control_df = pd.concat([matched_control_df, drawed1])
            additional2 = additional_needed - additional1
            additional_from_pool2 = pool[
            (
                (control_df['Functional Area Desc'] == row['Functional Area Desc'])
                & (control_df['Company Insider Type'] == row['Company Insider Type'])
            )
            |
            (
                (control_df['Functional Area Desc'] == row['Functional Area Desc'])
                & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
            )
            |
            (
                (control_df['Functional Area Desc'] == row['Functional Area Desc'])
                & (control_df['Region'] == row['Region'])
            )
            |
            (
                (control_df['Company Insider Type'] == row['Company Insider Type'])
                & (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
            )
            |
            (
                (control_df['Company Insider Type'] == row['Company Insider Type'])
                & (control_df['Region'] == row['Region'])
            )
            |
            (
                (control_df['Reporting_Level_Group'] == row['Reporting_Level_Group'])
                & (control_df['Region'] == row['Region'])
            )]
            drawed2 = additional_from_pool2.sample(n=additional2, random_state=42)
            pool = pool.drop(drawed2.index)
            matched_control_df = pd.concat([matched_control_df, drawed2])


print(matched_control_df.shape)
print(treatment_df.shape)
print(control_df.shape)

print(pool.shape)

# plotting
df_plot = pd.concat(
    [treatment_df[matched_control_df.columns.tolist()],
     matched_control_df]
)
print(df_plot.shape)
df_plot['treatment_group'].value_counts()

print(df_plot.groupby('treatment_group')['Company Insider Type'].value_counts(normalize=True))
sns.set(style="whitegrid")
plt.figure(figsize=(10,6))
sns.histplot(df_plot, x='Company Insider Type', hue='treatment_group', bins=10, multiple='dodge', palette={0:'blue', 1:'red'})
control_patch = mpatches.Patch(color='blue', label='Control: 81.5% IC')
treat_patch = mpatches.Patch(color='red', label='Treatment: 76.6% IC')
plt.legend(handles=[treat_patch,control_patch], title="Grouping")
plt.xlabel('Company Insider Type')
plt.ylabel('Count')
plt.show()
