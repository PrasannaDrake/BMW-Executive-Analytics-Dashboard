import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# DATA PREP

FILE_PATH = "bmw_global_sales_dataset.csv"  # keep CSV in same folder

def load_data():
    df = pd.read_csv(FILE_PATH)
    df = df.drop_duplicates().copy()
    df.columns = [c.strip().lower() for c in df.columns]

    num_cols = df.select_dtypes(include="number").columns
    cat_cols = df.select_dtypes(exclude="number").columns

    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    for c in cat_cols:
        df[c] = df[c].fillna(df[c].mode().iloc[0])

    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["revenue_usd"] = df["price_usd"] * df["units_sold"]
    return df


def build_dashboard(root, df):
    BG = "#121212"
    CARD = "#1E1E1E"
    FG = "#E0E0E0"
    ACCENT = "#0066CC"
    ACCENT2 ="#00FFFF"
    GOOD = "#20C997"
    WARN = "#E76F51"

    root.title("Executive Summary Dashboard")
    root.configure(bg=BG)
    root.state("zoomed")

    df_2024 = df[df["year"] == 2024].copy()
    total_revenue = df_2024["revenue_usd"].sum()
    total_units = int(df_2024["units_sold"].sum())

    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=15, pady=10)
    left_header = tk.Frame(header, bg=BG)
    left_header.pack(side="left")
    try:
        logo_img = Image.open('/mnt/data/BMW.svg.png')
        logo_img = logo_img.resize((48, 48))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(left_header, image=logo_photo, bg=BG)
        logo_label.image = logo_photo
        logo_label.pack(side='left', padx=(0,10))
    except Exception:
        pass
    tk.Label(left_header, text="Executive Summary Dashboard", bg=BG, fg=FG,
             font=("Segoe UI", 24, "bold")).pack(side="left")
    try:
        car_img = Image.open("download (1).png")
        car_img = car_img.resize((240, 110))
        car_photo = ImageTk.PhotoImage(car_img)
        img_label = tk.Label(header, image=car_photo, bg=BG)
        img_label.image = car_photo
        img_label.pack(side="right")
    except Exception:
        tk.Label(header, text="BMW", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(side="right")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=CARD, foreground=FG,
                    padding=(20, 10), font=("Segoe UI", 11, "bold"))
    style.map("TNotebook.Tab", background=[("selected", ACCENT)])

    notebook = ttk.Notebook(root, style="TNotebook")
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= PAGE 1 =================
    page1 = tk.Frame(notebook, bg=BG)
    notebook.add(page1, text="Executive Dashboard")

    main = tk.Frame(page1, bg=BG)
    main.pack(fill="both", expand=True)

    left = tk.Frame(main, bg=BG, width=300)
    left.pack(side="left", fill="y", padx=(0, 15))
    left.pack_propagate(False)

    center = tk.Frame(main, bg=BG)
    center.pack(side="left", fill="both", expand=True)

    # KPI LEFT PANEL
    best_country = df_2024.groupby('country')['revenue_usd'].sum().idxmax()
    best_model = df_2024.groupby('model')['revenue_usd'].sum().idxmax()
    kpis = [
        ("2024 Revenue", f"${total_revenue/1e9:.2f}B"),
        ("2024 Units", f"{total_units:,}"),
        ("Top Country (2024)", best_country),
        ("Top Revenue Model (2024)", best_model),
    ]
    for title, value in kpis:
        card = tk.Frame(left, bg=CARD, padx=18, pady=18)
        card.pack(fill="x", pady=8)
        tk.Label(card, text=title, bg=CARD, fg="#9E9E9E", font=("Segoe UI", 11)).pack(anchor="w")
        tk.Label(card, text=value, bg=CARD, fg=FG, font=("Segoe UI", 20, "bold")).pack(anchor="w")

    fig = Figure(figsize=(14, 8), dpi=100)
    fig.patch.set_facecolor(BG)

    ax1 = fig.add_subplot(231)
    rev_5y = df[df["year"].between(2019, 2024)].groupby("year")["revenue_usd"].sum()
    ax1.plot(rev_5y.index, rev_5y.values / 1e9, marker="o")
    ax1.set_title("Revenue Trend (2019–2024, All Markets)", color=FG)
    ax1.set_facecolor(CARD)
    ax1.tick_params(colors=FG)

    ax2 = fig.add_subplot(232)
    monthly = df_2024.groupby("month")["units_sold"].sum()
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ax2.plot(month_names, monthly.values, marker="o")
    ax2.set_title("2024 Monthly Sales", color=FG)
    ax2.set_facecolor(CARD)
    ax2.tick_params(colors=FG)

    ax3 = fig.add_subplot(233)
    top5 = df_2024.groupby("country")["revenue_usd"].sum().sort_values(ascending=False).head(5) / 1e6
    ax3.bar(top5.index, top5.values)
    ax3.set_title("Top 5 Countries by 2024 Revenue (M USD)", color=FG)
    ax3.set_facecolor(CARD)
    ax3.tick_params(colors=FG, axis='x', rotation=25)
    ax3.tick_params(axis='y', colors=FG)

    ax4 = fig.add_subplot(234)
    top6 = df_2024.groupby("model")["units_sold"].sum().sort_values().tail(6)
    ax4.barh(top6.index, top6.values)
    ax4.set_title("Top 6 Models by 2024 Units", color=FG)
    ax4.set_facecolor(CARD)
    ax4.tick_params(colors=FG)

    ax5 = fig.add_subplot(235)
    seg = df_2024.groupby("segment")["revenue_usd"].sum()
    ax5.pie(
        seg.values,
        labels=[f"{name}{val/sum(seg.values)*100:.1f}%" for name, val in zip(seg.index, seg.values)],
        textprops={'color': FG},
        wedgeprops=dict(width=0.45)
    )
    ax5.set_title("Revenue by Segment", color=FG)
    ax5.set_facecolor(CARD)

    ax6 = fig.add_subplot(236)
    ax6.axis("off")
    ax6.set_facecolor(CARD)
    ax6.text(0.05, 0.88, "Executive Summary", color=FG, fontsize=18, weight="bold")
    ax6.text(0.05, 0.2, "• 2024 highest revenue year\n• UK leads revenue\n• 7 Series top-selling\n• EV strongest segment", color=FG, fontsize=12)

    fig.tight_layout(pad=3)
    canvas = FigureCanvasTkAgg(fig, master=center)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= PAGE 2 =================
    page2 = tk.Frame(notebook, bg=BG)
    notebook.add(page2, text="Regional Performance")

    title = tk.Label(page2, text="Regional Revenue Performance (2020–2024)", bg=BG, fg=FG,
                     font=("Segoe UI", 22, "bold"))
    title.pack(anchor="w", padx=20, pady=(20, 5))
    sub = tk.Label(page2, text="Country-wise yearly revenue trend and current YoY business status",
                   bg=BG, fg="#9E9E9E", font=("Segoe UI", 10))
    sub.pack(anchor="w", padx=20)

    # Build country-year revenue table from CSV
    years = [2020, 2021, 2022, 2023, 2024]
    country_year = (
        df[df['year'].isin(years)]
        .groupby(['country', 'year'])['revenue_usd']
        .sum()
        .unstack(fill_value=0)
    ) / 1e6

    content2 = tk.Frame(page2, bg=BG)
    content2.pack(fill="both", expand=True, padx=20, pady=20)

    table = tk.Frame(content2, bg=CARD)
    table.pack(side='left', fill="both", expand=True, padx=(0,10))

    headers = ['COUNTRY', '2020 (M USD)', '2021 (M USD)', '2022 (M USD)', '2023 (M USD)', '2024 (M USD)', 'YOY GROWTH', 'STATUS']
    for i, h in enumerate(headers):
        tk.Label(table, text=h, bg=CARD, fg=ACCENT2,
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=i, padx=18, pady=12)

    top_countries = country_year[2024].sort_values(ascending=False).head(8).index
    rows = []
    status_rank = {'OPTIMAL': 0, 'STABLE': 1, 'REVIEW': 2}
    for country in top_countries:
        vals = country_year.loc[country]
        yoy = ((vals[2024] - vals[2023]) / vals[2023] * 100) if vals[2023] else 0
        status = 'OPTIMAL' if yoy > 8 and vals[2024] > 600 else 'STABLE' if yoy > 0 else 'REVIEW'
        rows.append([
            country,
            f"{vals[2020]:.0f}", f"{vals[2021]:.0f}", f"{vals[2022]:.0f}",
            f"{vals[2023]:.0f}", f"{vals[2024]:.0f}",
            f"{yoy:+.1f}%", status
        ])

    rows = sorted(rows, key=lambda x: (status_rank[x[7]], -float(x[5])))

    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            color = FG
            if c == 6:
                color = GOOD if '+' in val else WARN
            if c == 7:
                color = GOOD if val in ('OPTIMAL', 'STABLE') else WARN
            tk.Label(table, text=val, bg=CARD, fg=color,
                     font=("Segoe UI", 10)).grid(row=r, column=c, padx=18, pady=14, sticky='w')

    # Right-side trend chart for top countries
    chart2 = tk.Frame(content2, bg=CARD)
    chart2.pack(side='left', fill='both', expand=True, padx=(10,0))

    fig2 = Figure(figsize=(6, 5), dpi=100)
    fig2.patch.set_facecolor(CARD)
    axp2 = fig2.add_subplot(111)
    axp2.set_facecolor(CARD)

    top5_chart = list(top_countries[:5])
    for country in top5_chart:
        vals = country_year.loc[country, years]
        axp2.plot(years, vals.values, marker='o', label=country)

    axp2.set_xticks(years)
    axp2.set_xticklabels([str(y) for y in years], rotation=0)
    axp2.set_title('Top 5 Country Revenue Trends', color=ACCENT2)
    axp2.tick_params(colors=FG)
    axp2.legend(fontsize=8)
    for spine in axp2.spines.values():
        spine.set_color(FG)

    canvas_p2 = FigureCanvasTkAgg(fig2, master=chart2)
    canvas_p2.draw()
    canvas_p2.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)


    # ================= PAGE 3 =================
    page3 = tk.Frame(notebook, bg=BG)
    notebook.add(page3, text="Model Performance")

    title3 = tk.Label(page3, text="2024 Model Performance Intelligence", bg=BG, fg=FG,
                      font=("Segoe UI", 22, "bold"))
    title3.pack(anchor="w", padx=20, pady=(20, 10))

    # Build richer model intelligence table
    cur = df_2024.groupby('model').agg(units=('units_sold','sum'), revenue=('revenue_usd','sum'))
    prev = df[df['year']==2023].groupby('model').agg(prev_units=('units_sold','sum'), prev_revenue=('revenue_usd','sum'))
    model_perf = cur.join(prev, how='left').fillna(0)
    model_perf['rev_share'] = model_perf['revenue'] / model_perf['revenue'].sum() * 100
    model_perf['yoy_growth'] = ((model_perf['revenue'] - model_perf['prev_revenue']) / model_perf['prev_revenue'].replace(0, 1)) * 100

    def tier(row):
        if row['rev_share'] > 12 and row['yoy_growth'] > 0:
            return 'STAR'
        elif row['yoy_growth'] > -5:
            return 'CORE'
        return 'WATCHLIST'

    model_perf['tier'] = model_perf.apply(tier, axis=1)
    model_perf = model_perf.sort_values('revenue', ascending=False).head(10)

    content3 = tk.Frame(page3, bg=BG)
    content3.pack(fill="both", expand=True, padx=20, pady=20)

    table3 = tk.Frame(content3, bg=CARD)
    table3.pack(side='left', fill="both", expand=True, padx=(0,10))
    headers3 = ['MODEL', 'UNITS', 'REVENUE (M USD)', 'REV SHARE %', 'YOY %', 'TIER']
    for i, h in enumerate(headers3):
        tk.Label(table3, text=h, bg=CARD, fg=ACCENT2, font=("Segoe UI", 9, "bold")).grid(row=0, column=i, padx=18, pady=12)

    for r, (model, row) in enumerate(model_perf.iterrows(), start=1):
        vals = [
            model,
            f"{int(row['units']):,}",
            f"{row['revenue']/1e6:.1f}",
            f"{row['rev_share']:.1f}%",
            f"{row['yoy_growth']:+.1f}%",
            row['tier']
        ]
        for c, val in enumerate(vals):
            color = FG
            if c == 4:
                color = GOOD if '+' in val else WARN
            if c == 5:
                color = GOOD if val in ('STAR','CORE') else WARN
            tk.Label(table3, text=val, bg=CARD, fg=color, font=("Segoe UI", 10)).grid(row=r, column=c, padx=18, pady=10, sticky='w')

    # Revenue contribution pie chart based on 2024 model performance intelligence
    chart3 = tk.Frame(content3, bg=CARD)
    chart3.pack(side='left', fill='both', expand=True, padx=(10,0))

    fig3 = Figure(figsize=(5.5, 5.5), dpi=100)
    fig3.patch.set_facecolor(CARD)
    ax3p = fig3.add_subplot(111)
    ax3p.set_facecolor(CARD)

    pie_data = model_perf.copy()  # uses the 2024 intelligence table data
    wedges, texts, autotexts = ax3p.pie(
        pie_data['revenue'],
        labels=pie_data.index,
        autopct='%1.1f%%',
        pctdistance=0.78,
        textprops={'color': FG},
        wedgeprops=dict(width=0.42)
    )
    ax3p.set_title('2024 Model Revenue Contribution', color=ACCENT2)
    ax3p.text(0, 0, '2024 Revenue\n  Mix', ha='center', va='center', color=FG, fontsize=12, weight='bold')

    canvas_p3 = FigureCanvasTkAgg(fig3, master=chart3)
    canvas_p3.draw()
    canvas_p3.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    # ================= PAGE 4 =================
    page4 = tk.Frame(notebook, bg=BG)
    notebook.add(page4, text="Segment Intelligence")

    title4 = tk.Label(page4, text="2024 Segment Performance Intelligence", bg=BG, fg=FG,
                      font=("Segoe UI", 22, "bold"))
    title4.pack(anchor="w", padx=20, pady=(20, 10))

    seg_container = tk.Frame(page4, bg=BG)
    seg_container.pack(fill="both", expand=True, padx=20, pady=10)

    for seg_name in ['Electric', 'SUV', 'Sedan']:
        seg_frame = tk.Frame(seg_container, bg=CARD, bd=1, relief='flat')
        seg_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        tk.Label(seg_frame, text=seg_name, bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=4, sticky='w', padx=12, pady=10)

        seg_df = df_2024[df_2024['segment'] == seg_name]
        cur_seg = seg_df.groupby('model').agg(units=('units_sold','sum'), revenue=('revenue_usd','sum'))
        prev_seg = df[(df['year']==2023) & (df['segment']==seg_name)].groupby('model').agg(prev_revenue=('revenue_usd','sum'))
        perf = cur_seg.join(prev_seg, how='left').fillna(0)
        if len(perf) == 0:
            continue
        perf['share'] = perf['revenue'] / perf['revenue'].sum() * 100
        perf['yoy'] = ((perf['revenue'] - perf['prev_revenue']) / perf['prev_revenue'].replace(0,1))*100
        perf = perf.sort_values('revenue', ascending=False).head(5)

        headers = ['MODEL', 'SALES', 'REV (M USD)']
        for c, h in enumerate(headers):
            tk.Label(seg_frame, text=h, bg=CARD, fg=ACCENT2,
                     font=("Segoe UI", 9, "bold"), width=14, anchor='w').grid(row=1, column=c, padx=10, pady=6, sticky='w')

        for r_idx, (model, row) in enumerate(perf.iterrows(), start=2):
            vals = [model, f"{int(row['units']):,}", f"{row['revenue']/1e6:.1f}"]
            for c, val in enumerate(vals):
                color = FG
                cell_bg = '#232323' if r_idx % 2 == 0 else CARD
                tk.Label(seg_frame, text=val, bg=cell_bg, fg=color,
                         font=("Segoe UI", 9), width=14, anchor='w').grid(row=r_idx, column=c, padx=10, pady=4, sticky='w')

    # ================= PAGE 5 =================
    page4 = tk.Frame(notebook, bg=BG)
    notebook.add(page4, text="Engine Trends")

    title4 = tk.Label(page4, text="Engine Type Trend Analysis (2019–2024)", bg=BG, fg=FG,
                      font=("Segoe UI", 22, "bold"))
    title4.pack(anchor="w", padx=20, pady=(20, 10))

    if 'engine_type' in df.columns:
        fig4 = Figure(figsize=(12, 6), dpi=100)
        fig4.patch.set_facecolor(BG)
        ax = fig4.add_subplot(111)
        engine_trend = df[df['year'].between(2019, 2024)].groupby(['year', 'engine_type'])['units_sold'].sum().unstack(fill_value=0)
        for col in engine_trend.columns:
            ax.plot(engine_trend.index, engine_trend[col], marker='o', label=col)
        ax.set_facecolor(CARD)
        ax.set_title('Engine Popularity by Units Sold', color=ACCENT2)
        ax.tick_params(colors=FG)
        ax.legend()
        canvas4 = FigureCanvasTkAgg(fig4, master=page4)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
    else:
        tk.Label(page4, text='Engine type column not found in dataset.', bg=BG, fg=FG,
                 font=("Segoe UI", 14)).pack(padx=20, pady=20)

if __name__ == "__main__":
    df = load_data()
    root = tk.Tk()
    build_dashboard(root, df)
    root.mainloop()
