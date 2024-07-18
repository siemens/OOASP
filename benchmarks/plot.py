import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

solving_cm = mpl.colormaps['Pastel2'].resampled(8)
grounding_cm = mpl.colormaps['Set2'].resampled(8)


def get_results(name="bm"):
    """Gets the results for a given benchamrk name

    Parameters:
        name (str, optional): The name/path of the benchmark. Defaults to "bm".

    Returns:
        json: Json with the benchmarks info
    """
    with open(f'benchmarks/results/{name}.json') as outfile:
        return json.load(outfile)


solving_cm = mpl.colormaps['Pastel2'].resampled(8)
grounding_cm = mpl.colormaps['Set2'].resampled(8)


def plot_gs(bm_names, title, cls="element"):
    """Compare different benchmarks outputs

    Parameters:
        bm_names : The name of the benchmark files to compare
        title : The title of the plot and output file
    """

    plt.clf()
    dfs = {}
    width = 0.2
    fig, ax = plt.subplots()

    for bm_name in bm_names:
        data_dic = get_results(bm_name)
        df = pd.DataFrame.from_dict(data_dic, orient="index")
        df['name'] = df.index
        df = df.reset_index()
        dfs[bm_name] = df
    for pos, (bm_name, df) in enumerate(dfs.items()):
        xs = df.index+(width*pos)
        for i, x in enumerate(xs):
            if df['timeout'][i] == 1:
                ax.axvline(x=x, color='red', label='_nolegend_')
        colors = df['timeout'].apply(lambda x: 'red' if x == 1 else 'black')
        ax.bar(xs, df['time'], color=solving_cm(pos), width=width)
        ax.bar(xs, df['time-grounding'], color=grounding_cm(pos), width=width)
        ax.bar_label(ax.containers[pos*2], df['size'].astype(str) + "/" + df['domain_size'].astype(str), fontsize=5)

    ax.set_ylabel('Time (sec)')
    ax.set_xlabel(f'#{cls}s')
    ax.set_title(title)

    legends = []
    for bm_name in dfs.keys():
        legends += [f'solving {bm_name}', f'grounding {bm_name}']
    ax.legend(legends, loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_xticks(df.index, df['name'])
    fig.savefig(f'benchmarks/results/{title}.png', bbox_inches="tight")
    print(f"Saved image in benchmarks/results/{title}.png")


def plot_domain(bm_name, title, name):
    """Plotting the times for a single call devided per domain

    Parameters:
        bm_name : The name of the benchmark file saved
        title : The title of the plot and output file
        name : The domain name (Number)
    """
    plt.clf()
    data_dic = get_results(bm_name)[name]
    d = {
        "grounding": data_dic["per-domain-grounding"],
        "solving": data_dic["per-domain-solving"]
    }

    df = pd.DataFrame.from_dict(d, orient="index")
    df = df.T
    df['time'] = df.sum(axis=1)
    plt.bar(df.index, df['time'], color='lightsteelblue', width=0.3)
    plt.bar(df.index, df['grounding'], color='tan', width=0.3)
    plt.ylabel('Time (sec)')
    plt.xlabel('Domain size')
    plt.title(title)
    plt.legend(['solving', 'grounding'], loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(f'benchmarks/results/{title}.png', bbox_inches="tight")
    print(f"Saved image in benchmarks/results/{title}.png")


plot_gs(['inc_elem', 'inc_elem_overshoot', 'inc_elem_overshoot_assumption',
        'inc_elem_step_4'], "Compare incremental elem", "Element")
plot_gs(['inc_rack', 'inc_rack_overshoot', 'inc_rack_overshoot_assumption',
        'inc_rack_step'], "Compare incremental rack", "RackDouble")
plot_gs(['wagon_people_f', 'wagon_people', 'wagon_people_f_no_external',
        'wagon_people_no_external'], "Compare numerical", "nr_passengers")

plot_domain('inc_rack_overshoot_assumption', "Domain steps for inc overshoot", "6")
plot_domain('inc_elem_overshoot', "Domain steps Elem inc overshoot", "10")
plot_domain('inc_elem_step_4', "Domain steps Elem inc step 4", "10")
