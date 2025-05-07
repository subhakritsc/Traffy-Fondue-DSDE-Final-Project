import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import random

st.set_page_config(page_title="ภาพรวมปัญหาในกทม", page_icon="🚨", layout="wide")


# ------------------------- LOADING DATA -----------------------------
@st.cache_data
def load_data():
    # 1. map and graph visualization
    df = pd.read_csv("cluster_data.csv")
    df["cluster_id"] = df["cluster_id"].astype(str)

    # 2. example of each cluster_id
    report_df = pd.read_csv("example_comment.csv")
    report_df["cluster"] = report_df["cluster"].astype(str)
    return df, report_df


df, report_df = load_data()
# Get all unique zones and organizations
all_zones = sorted(df["zone"].unique())
all_organizations = sorted(
    set(org.strip() for orgs in df["organization"] for org in orgs.split(","))
)

# ------------------------- GLOBAL -----------------------------


@st.cache_data
def create_zone_colors(zones):
    colors = [
        [255, 0, 0],  # Red
        [0, 255, 0],  # Green
        [0, 0, 255],  # Blue
        [255, 165, 0],  # Orange
        [128, 0, 128],  # Purple
        [255, 192, 203],  # Pink
        [165, 42, 42],  # Brown
        [0, 255, 255],  # Cyan
        [255, 255, 0],  # Yellow
        [70, 130, 180],  # Steel Blue
        [50, 205, 50],  # Lime Green
        [255, 0, 255],  # Magenta
        [210, 105, 30],  # Chocolate
        [128, 128, 0],  # Olive
        [0, 128, 128],  # Teal
    ]

    zone_colors = {}
    for i, zone in enumerate(zones):
        zone_colors[zone] = colors[i % len(colors)]
    return zone_colors


status_colors = {
    "เสร็จสิ้น": [0, 200, 83],  # green
    "กำลังดำเนินการ": [255, 193, 7],  # yellow
    "รอรับเรื่อง": [244, 67, 54],  # red
}

# ------------------------- PAGE CONFIG -----------------------------

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
    <style>
    * {
        font-family: 'Sarabun', sans-serif !important;
    }

    strong, b {
        font-weight: 700 !important;  /* ตัวหนา */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f9f9f9; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ภาพรวมการเกิดปัญหาในพื้นที่กรุงเทพมหานคร")
st.write("")

page = st.radio(
    "**เลือกหน้าที่ต้องการแสดงผล**",
    ["🗺️ แผนที่", "📊 กราฟและตาราง", "🗒️ รายละเอียดปัญหา", "🧠 แนวคิดหลัก"],
    horizontal=True,
)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
st.write("")

# ------------------------- SIDEBAR -----------------------------

if page == "🗺️ แผนที่":
    st.sidebar.write("")
    st.sidebar.subheader("**ตัวเลือกการแสดงผล**")
    st.sidebar.write("")

    viz_mode = st.sidebar.selectbox("**รปแบบ**", ["จุด", "แท่ง", "Heatmap"], index=0)

    map_style = st.sidebar.selectbox(
        "**สไตล์แผนที่**", ["โหมดมืด", "โหมดสว่าง", "แผนที่ถนน", "แผนที่ดาวเทียม"], index=2
    )

    if viz_mode != "Heatmap":
        show_color = st.sidebar.radio("**แสดงสีตาม**", ["โซน", "สถานะของปัญหา"])

    st.sidebar.markdown(
        "<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True
    )
    st.sidebar.write("#### ตัวกรอง")

    selected_zone = st.sidebar.selectbox("**กรองด้วยโซน**", ["-"] + all_zones, index=0)

    selected_org = st.sidebar.selectbox(
        "**กรองด้วยหน่วยงาน**", ["-"] + all_organizations[::-1], index=0
    )

    if viz_mode != "Heatmap":
        limit_num = st.sidebar.slider(
            "**จำนวนการเกิดปัญหาขั้นต่่ำ**", min_value=1, max_value=20, value=10, step=1
        )

elif page == "📊 กราฟและตาราง":
    st.sidebar.write("")
    st.sidebar.subheader("**ตัวเลือกการแสดงผล**")
    st.sidebar.write("")

    top_n = st.sidebar.slider(
        "**จำนวนอันดับสูงสุดที่ให้แสดง**", min_value=3, max_value=15, value=5
    )

    st.sidebar.markdown(
        "<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True
    )

    st.sidebar.write("#### ตัวกรอง")
    selected_zone = st.sidebar.selectbox("**กรองด้วยโซน**", ["-"] + all_zones, index=0)

    selected_org = st.sidebar.selectbox(
        "**กรองด้วยหน่วยงาน**", ["-"] + all_organizations[::-1], index=0
    )

# ------------------------- CONTENT -----------------------------

if page == "🗺️ แผนที่":
    st.subheader("แผนที่แสดงจำนวนการเกิดปัญหา")

    # Filter the data based on selections
    filtered_df = df.copy()
    if selected_zone != "-":
        filtered_df = filtered_df[filtered_df["zone"] == selected_zone]
    if selected_org != "-":
        filtered_df = filtered_df[
            filtered_df["organization"].str.contains(selected_org)
        ]

    if viz_mode != "Heatmap":
        filtered_df = filtered_df[filtered_df["num_times"] >= limit_num]
        if show_color == "โซน":
            # Create color mapping
            zone_colors = create_zone_colors(all_zones)
            # Add color column to the dataframe for visualization
            filtered_df["color"] = filtered_df["zone"].map(lambda x: zone_colors[x])
        elif show_color == "สถานะของปัญหา":
            filtered_df["color"] = filtered_df["status"].map(lambda x: status_colors[x])

    # Define map style dictionary
    MAP_STYLES = {
        "โหมดมืด": "mapbox://styles/mapbox/dark-v10",
        "โหมดสว่าง": "mapbox://styles/mapbox/light-v10",
        "แผนที่ถนน": "mapbox://styles/mapbox/streets-v11",
        "แผนที่ดาวเทียม": "mapbox://styles/mapbox/satellite-v9",
    }

    # Calculate map center (for initial view)
    if not filtered_df.empty:
        center_lat = filtered_df["lat"].mean()
        center_long = filtered_df["long"].mean()
    else:
        center_lat, center_long = 13.75, 100.5  # Default to Bangkok

    # Display the map
    st.write("")
    map_col, space, legend_col = st.columns([1.15, 0.02, 0.43])

    with legend_col:
        if viz_mode == "จุด" or viz_mode == "แท่ง":
            if show_color == "โซน":
                st.write("")
                st.write("**สีของแต่ละโซน**")
                zone_counts = df["zone"].value_counts()
                zone_counts_dict = zone_counts.to_dict()
                for zone in zone_counts.index:
                    r, g, b = zone_colors[zone]
                    count = zone_counts_dict.get(zone, 0)
                    legend_col.markdown(
                        f"""
                        <div style='display: flex; align-items: center; padding: 5px 0;'>
                            <div style='width: 1.2em; height: 1.2em; background-color: rgb({r},{g},{b}); 
                                        margin-right: 10px; flex-shrink: 0; border-radius: 4px;'></div>
                            <div style='flex: 1; font-size: 11px;'>
                                {zone} <span style='color: #7B8A99;'>({count:,} ปัญหา)</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            elif show_color == "สถานะของปัญหา":
                st.write("")
                st.write("**สีของแต่ละสถานะ**")
                status_counts = df["status"].value_counts()
                status_counts_dict = status_counts.to_dict()
                for status, (r, g, b) in status_colors.items():
                    count = status_counts_dict.get(status, 0)
                    legend_col.markdown(
                        f"""
                        <div style='display: flex; align-items: center; padding: 5px 0;'>
                            <div style='width: 1.2em; height: 1.2em; background-color: rgb({r},{g},{b}); 
                                        margin-right: 10px; flex-shrink: 0; border-radius: 4px;'></div>
                            <div style='flex: 1; font-size: 0.85em;'>
                                {status} <span style='color: #7B8A99;'>({count:,} ปัญหา)</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.write("")
            if viz_mode == "จุด":
                st.markdown(
                    "<span style='font-size: 11px; color: #5D7991;'>**ℹ️ ขนาดของจุด** แสดงถึง <b>จำนวนครั้งที่ปัญหานั้นเกิด</b></span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<span style='font-size: 11px; color: #5D7991;'><b>ℹ️ ความสูงของแท่ง</b> แสดงถึง <b>จำนวนครั้งที่ปัญหานั้นเกิด</b></span>",
                    unsafe_allow_html=True,
                )
        else:
            st.write("")
            st.write("**สีของ Heatmap**")

            heatmap_legend = [
                ("แดงเข้ม", "พื้นที่มีปัญหาเกิดบ่อยมาก"),
                ("ส้ม", "พื้นที่มีปัญหาเกิดปานกลาง"),
                ("เหลือง", "พื้นที่มีปัญหาเกิดน้อย"),
                ("ใส", "พื้นที่ไม่มีปัญหา"),
            ]

            for color_name, meaning in heatmap_legend:
                color_map = {
                    "แดงเข้ม": "rgb(255, 0, 0)",
                    "ส้ม": "rgb(255, 165, 0)",
                    "เหลือง": "rgb(255, 255, 0)",
                    "ใส": "rgb(255, 255, 255)",
                }
                color = color_map[color_name]
                legend_col.markdown(
                    f"""
                    <div style='display: flex; align-items: center; padding: 5px 0;'>
                        <div style='width: 1.2em; height: 1.2em; background-color: {color}; 
                                    margin-right: 10px; flex-shrink: 0; border-radius: 4px; border: 1px solid #ccc;'></div>
                        <div style='flex: 1; font-size: 11px;'>
                            <b>{color_name}</b> <span style='color: #7B8A99;'>– {meaning}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    with map_col:
        if viz_mode == "จุด":
            initial_view_state = pdk.ViewState(
                latitude=center_lat, longitude=center_long, zoom=11, pitch=0, bearing=0
            )
            layer = [
                pdk.Layer(
                    "ScatterplotLayer",
                    filtered_df,
                    get_position=["long", "lat"],
                    get_color="color",  # Use the color mapped from zone
                    get_radius="num_times * 10",  # Size based on occurrence count
                    pickable=True,
                    opacity=0.8,
                    stroked=True,
                    filled=True,
                    line_width_min_pixels=1,
                )
            ]
        elif viz_mode == "Heatmap":
            initial_view_state = pdk.ViewState(
                latitude=center_lat, longitude=center_long, zoom=11, pitch=0, bearing=0
            )

            layer = [
                pdk.Layer(
                    "HeatmapLayer",
                    data=filtered_df,
                    get_position="[long, lat]",
                    aggregation=pdk.types.String("SUM"),
                    get_weight="num_times",
                    opacity=0.8,
                )
            ]
        else:
            initial_view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_long,
                zoom=11,
                pitch=45,  # Tilted view for 3D
                bearing=0,
            )

            layer = [
                pdk.Layer(
                    "ColumnLayer",
                    filtered_df,
                    get_position=["long", "lat"],
                    get_elevation="num_times * 100",  # Height based on occurrence count
                    elevation_scale=1,
                    radius=25,
                    get_fill_color="color",  # Use the color mapped from zone
                    pickable=True,
                    auto_highlight=True,
                    extruded=True,
                )
            ]

        # Create and display the map
        deck = pdk.Deck(
            layers=layer,
            initial_view_state=initial_view_state,
            map_style=MAP_STYLES[map_style],
            tooltip={
                "html": """
                <div style="font-size: 12px; line-height: 2;">
                    <b>หมายเลข:</b> {cluster_id}<br/>
                    <b>คำอธิบาย:</b> {cluster_desc}<br/>
                    <b>หน่วยงาน:</b> {organization}<br/>
                    <b>โซน:</b> {zone}<br/>
                    <b>จำนวนการเกิดปัญหา:</b> {num_times}
                </div>
                """
            },
        )
        st.pydeck_chart(deck)

elif page == "📊 กราฟและตาราง":
    st.subheader("กราฟและตารางแสดงจำนวนการเกิดปัญหา")
    st.write("")

    col1, spacer, col2 = st.columns([1, 0.05, 1])

    with col1:
        st.write("##### จำนวนการเกิดปัญหารวมของแต่ละโซน")
        zone_colors = create_zone_colors(all_zones)
        copy_df = df.copy()
        copy_df["color"] = copy_df["zone"].map(lambda x: f"rgb{tuple(zone_colors[x])}")

        zone_counts = (
            copy_df.groupby(["zone", "color"])["num_times"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )
        zone_df = zone_counts.reset_index()
        zone_df.columns = ["zone", "color", "num_times"]
        fig = px.bar(
            zone_df,
            x="zone",
            y="num_times",
            color="zone",  # group by zone name
            color_discrete_map={z: f"rgb{tuple(c)}" for z, c in zone_colors.items()},
            labels={"zone": "โซน", "num_times": "จำนวนการเกิดปัญหารวม"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        top_zone = zone_df.loc[zone_df["num_times"].idxmax(), "zone"]
        top_value = zone_df["num_times"].max()
        st.write("")
        st.markdown(
            f"**โซนที่มีจำนวนการเกิดปัญหารวมมากที่สุด:**<br/>{top_zone} ({top_value:,} ครั้ง)",
            unsafe_allow_html=True,
        )

    with col2:
        st.write("##### จำนวนการเกิดปัญหารวมของแต่ละหน่วยงาน")
        df_exploded = df.copy()
        df_exploded["organization"] = df_exploded["organization"].str.split(
            ","
        )  # split to list
        df_exploded = df_exploded.explode("organization")  # explode to rows
        df_exploded["organization"] = df_exploded[
            "organization"
        ].str.strip()  # clean spaces
        org_counts = (
            df_exploded.groupby("organization")["num_times"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )

        org_df = org_counts.reset_index()
        org_df.columns = ["org", "num_times"]
        fig = px.bar(
            org_df,
            x="org",
            y="num_times",
            labels={"org": "หน่วยงาน", "num_times": "จำนวนการเกิดปัญหารวม"},
            color="num_times",
            color_continuous_scale=[
                [0.0, "#c6dbef"],  # light blue
                [0.5, "#6baed6"],  # medium blue
                [1.0, "#2171b5"],  # dark blue
            ],
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.write("")
        st.markdown(
            f"**หน่วยงานที่มีจำนวนการเกิดปัญหารวมมากที่สุด:**<br/>{org_counts.idxmax()} ({org_counts.max():,} ครั้ง)",
            unsafe_allow_html=True,
        )

    # Filter data
    filtered_df = df.copy()
    if selected_zone != "-":
        filtered_df = filtered_df[filtered_df["zone"] == selected_zone]
    if selected_org != "-":
        filtered_df = filtered_df[
            filtered_df["organization"].str.contains(selected_org)
        ]

    st.markdown("---")

    col1, spacer, col2 = st.columns([1, 0.05, 1])

    with col1:
        st.markdown(
            '<h5>ปัญหาที่มีจำนวนการเกิดมากที่สุด <span style="font-weight: normal; font-size: 0.65em;">(ตามตัวกรอง)</span></h5>',
            unsafe_allow_html=True,
        )

        # Sort by num_times and get the top clusters
        top_clusters = (
            filtered_df[["cluster_id", "num_times"]]
            .sort_values(by="num_times", ascending=False)
            .head(top_n)
            .reset_index()
        )

        # Plot with cluster_id on x and num_times on y
        fig = px.bar(
            top_clusters,
            x="cluster_id",
            y="num_times",
            labels={"cluster_id": "หมายเลขปัญหา", "num_times": "จำนวนปัญหาที่เกิด"},
            color="num_times",
            color_continuous_scale=[
                [0.0, "#c6dbef"],  # light blue
                [0.5, "#6baed6"],  # medium blue
                [1.0, "#2171b5"],  # dark blue
            ],
        )

        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            '<h5>ตารางแสดงปัญหาทั้งหมด <span style="font-weight: normal; font-size: 0.65em;">(ตามตัวกรอง)</span></h5>',
            unsafe_allow_html=True,
        )

        cols = [
            "cluster_id",
            "num_times",
            "cluster_desc",
            "status",
            "organization",
            "zone",
            "lat",
            "long",
        ]
        df_display = (
            filtered_df[cols]
            .sort_values(by="num_times", ascending=False)
            .reset_index(drop=True)
        )
        df_display.columns = [
            "หมายเลข",
            "จำนวนครั้ง",
            "คำอธิบาย",
            "สถานะ",
            "หน่วยงาน",
            "โซน",
            "ละติจูด",
            "ลองจิจูด",
        ]
        st.dataframe(df_display, use_container_width=True, height=450)

elif page == "🗒️ รายละเอียดปัญหา":
    st.subheader("รายละเอียดปัญหา")
    st.write("")
    st.write("")
    col1, spacer1, col2 = st.columns([0.3, 0.1, 1])

    with col1:
        clusters = sorted(
            report_df["cluster"].unique(),
            key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1]))
        )
        selected_cluster = st.selectbox("**เลือกหมายเลขของปัญหา**", clusters)
        max_comments = len(report_df[report_df["cluster"] == selected_cluster])
        st.write("")
        max_shown = max_comments if max_comments > 1 else 2
        num_samples = st.slider(
            "**จำนวนคอมเมนต์ที่ต้องการสุ่มแสดง**",
            min_value=1,
            max_value=min(10, max_shown),
            value=1,
        )
        st.write("")
        random_again = st.button("สุ่มอีกครั้ง")

    with col2:
        df_selected = df[df["cluster_id"] == selected_cluster]
        if not df_selected.empty:
            info = df_selected.iloc[0]
            status = info["status"]
            rgb = status_colors.get(
                status, [0, 0, 0]
            )  # default to black if status not found
            rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

            st.write("**คำอธิบาย:**", info["cluster_desc"])
            st.markdown(
                f"**สถานะ:** <span style='color: {rgb_str};'>{status}</span>",
                unsafe_allow_html=True,
            )
            st.write("**จำนวนการเกิดปัญหา:**", str(info["num_times"]))
            st.write("**หน่วยงาน:**", info["organization"])
            st.write("**โซน:**", info["zone"])
            st.write("**ละติจูด:**", str(info["lat"]))
            st.write("**ลองจิจูด:**", str(info["long"]))

        st.write("**จำนวนคอมเมนต์:**", str(max_comments))
        st.write("**ตัวอย่างคอมเมนต์ของปัญหาที่เลือก:**")
        cluster_comments = report_df[report_df["cluster"] == selected_cluster][
            "comment"
        ]
        num_samples = min(num_samples, len(cluster_comments))

        sampled_comments = cluster_comments.sample(
            n=num_samples, random_state=random.randint(0, 9999)
        )

        if random_again:
            sampled_comments = cluster_comments.sample(
                n=num_samples, random_state=random.randint(0, 9999)
            )

        # Display with bullet points
        for comment in sampled_comments:
            st.markdown(f"- {comment}")

elif page == "🧠 แนวคิดหลัก":
    st.subheader("แนวคิดหลักของการวิเคราะห์")
    st.write("")
    st.write(
        """
    กลุ่มของเราทำการ **จัดกลุ่มปัญหา (Clustering)** ตาม **สถานที่** และ **ลักษณะของปัญหา** เพื่อให้สามารถติดตามและประเมินการเกิดปัญหาในพื้นที่เดิมได้อย่างแม่นยำ โดยในการวิเคราะห์นี้
    - **การเกิดของปัญหา** ถูกนิยามว่าเป็น การที่มี**การรายงานปัญหาใหม่ในตำแหน่งเดิมและลักษณะเดิมหลังจากที่ปัญหานั้นได้รับการแก้ไขแล้ว**
    - หากมีการรายงานหลายครั้งในช่วงเวลาก่อนที่ปัญหาจะถูกแก้ไข จะถูกนับรวมเป็น **เพียง 1 ปัญหา** เพื่อป้องกันการนับซ้ำจากการติดตามของประชาชน
    """
    )
