# (streamlit_app.py - improved Streamlit app)
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import csv

st.set_page_config(page_title="Swimming Pool Designer", layout="wide")

st.title("🏊 Swimming Pool Designer (Abu Dhabi Code)")
st.write("Enter the pool dimensions below and click **Generate Drawing** to visualize it and compute volumes.")

# --- Inputs ---
length = st.number_input("Pool Length (m)", 0.0, 50.0, 7.25, 0.01)
width = st.number_input("Pool Width (m)", 0.0, 20.0, 4.25, 0.01)
depth_kids = st.number_input("Kids Depth (m)", 0.0, 5.0, 1.00, 0.01)
depth_adults = st.number_input("Adults Depth (m)", 0.0, 5.0, 1.50, 0.01)
kids_zone_length = st.number_input("Kids Zone Length (m)", 0.0, float(length), max(1.0, length * 0.3), 0.01)
wall_thickness = st.number_input("Wall Thickness (m)", 0.0, 1.0, 0.25, 0.01)
floor_thickness = st.number_input("Floor Thickness (m)", 0.0, 1.0, 0.30, 0.01)
soil_thickness = st.number_input("Soil Depth (m)", 0.0, 5.0, 0.50, 0.01)

# Validation
if depth_kids > depth_adults:
    st.warning("Kids depth is greater than adults depth. Please check depths.")

if kids_zone_length > length:
    st.warning("Kids zone length cannot exceed total length. It will be clamped to the pool length.")
    kids_zone_length = length

if st.button("Generate Drawing"):
    # Derived geometry
    outer_length = length + 2 * wall_thickness
    outer_width = width + 2 * wall_thickness
    outer_depth = depth_adults + floor_thickness + soil_thickness

    # Volumes & quantities
    # Water volume: two rectangular zones (kids zone + remaining adults zone)
    adults_zone_length = max(0.0, length - kids_zone_length)
    water_volume_m3 = (kids_zone_length * width * depth_kids) + (adults_zone_length * width * depth_adults)
    water_volume_l = water_volume_m3 * 1000.0

    # Excavation volume: approximate as outer box (includes soil)
    excavation_volume_m3 = outer_length * outer_width * outer_depth

    # Concrete estimate: floor slab + walls (simplified)
    floor_concrete_m3 = outer_length * outer_width * floor_thickness
    inner_perimeter = 2 * (length + width)
    wall_concrete_m3 = inner_perimeter * wall_thickness * (depth_adults + floor_thickness)
    concrete_total_m3 = floor_concrete_m3 + wall_concrete_m3

    # Display computed values
    st.subheader("Computed Quantities")
    st.write(f"- Water volume: {water_volume_m3:.3f} m³ ({water_volume_l:.0f} L)")
    st.write(f"- Excavation volume (approx): {excavation_volume_m3:.3f} m³")
    st.write(f"- Concrete volume (floor + walls, approx): {concrete_total_m3:.3f} m³")
    st.write(f"- Kids zone length: {kids_zone_length:.2f} m, Adults zone length: {adults_zone_length:.2f} m")

    # --- Create drawings in memory and provide download buttons ---
    # PLAN
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title("Plan View", fontsize=12, fontweight="bold")
    # Ground/soil (outer)
    ax.add_patch(patches.Rectangle((-wall_thickness, -wall_thickness),
                                   outer_length, outer_width,
                                   edgecolor='saddlebrown', facecolor='#f0d9b5', lw=2))
    # Pool water (inner)
    ax.add_patch(patches.Rectangle((0, 0), length, width,
                                   edgecolor='blue', facecolor='#a7d8ff', lw=2))
    # Annotations: outer dims and inner dims
    ax.annotate(f"{length:.2f} m", (length/2, -0.3), ha='center')
    ax.annotate(f"{width:.2f} m", (-0.5, width/2), rotation=90, va='center')
    # Wall thickness annotation (sample arrow)
    ax.annotate("", xy=(length + 0.05, -wall_thickness/2), xytext=(length + wall_thickness - 0.05, -wall_thickness/2),
                arrowprops=dict(arrowstyle="<->", color="saddlebrown"))
    ax.text(length + wall_thickness/2, -wall_thickness, f"wall {wall_thickness:.2f} m", ha='center', va='top', color='saddlebrown', fontsize=8)
    ax.set_aspect('equal')
    ax.grid(True, linestyle="--", alpha=0.3)
    buf_plan = io.BytesIO()
    fig.savefig(buf_plan, format="png", bbox_inches="tight")
    buf_plan.seek(0)
    st.image(buf_plan, caption="Plan View", use_container_width=True)
    st.download_button("Download Plan PNG", data=buf_plan.getvalue(), file_name="plan_view.png", mime="image/png")
    plt.close(fig)

    # LONGITUDINAL SECTION
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.set_title("Longitudinal Section", fontsize=12, fontweight="bold")
    # Ground/soil rectangle (from left -wall_thickness to right length+wall)
    ax.add_patch(patches.Rectangle((-wall_thickness, -soil_thickness - floor_thickness - depth_adults),
                                   outer_length, soil_thickness + floor_thickness + depth_adults,
                                   edgecolor='saddlebrown', facecolor='#f0d9b5', lw=2))
    # Pool interior (water + floor)
    ax.add_patch(patches.Rectangle((0, -floor_thickness - depth_adults),
                                   length, floor_thickness + depth_adults,
                                   edgecolor='black', facecolor='#a7d8ff', lw=2))
    # Show kids/adults extents with lines
    ax.axvline(kids_zone_length, color='black', linestyle='--', alpha=0.6)
    ax.annotate(f"Kids: {depth_kids:.2f} m", (kids_zone_length * 0.5, -depth_kids/2), color='blue')
    ax.annotate(f"Adults: {depth_adults:.2f} m", (kids_zone_length + adults_zone_length * 0.5, -depth_adults/2), color='blue')
    # Annotate floor slab thickness
    ax.annotate("", xy=(length + wall_thickness - 0.05, -floor_thickness), xytext=(length + wall_thickness - 0.05, 0),
                arrowprops=dict(arrowstyle="<->", color="gray"))
    ax.text(length + wall_thickness - 0.02, -floor_thickness/2, f"floor {floor_thickness:.2f} m", va='center', ha='left', fontsize=8, color='gray')
    ax.set_xlim(-wall_thickness * 1.2, length + wall_thickness * 1.2)
    ax.set_ylim(-outer_depth - 0.1, 0.2)
    ax.grid(True, linestyle="--", alpha=0.3)
    buf_long = io.BytesIO()
    fig.savefig(buf_long, format="png", bbox_inches="tight")
    buf_long.seek(0)
    st.image(buf_long, caption="Longitudinal Section", use_container_width=True)
    st.download_button("Download Longitudinal PNG", data=buf_long.getvalue(), file_name="longitudinal_view.png", mime="image/png")
    plt.close(fig)

    # TRANSVERSE SECTION (at mid-length)
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_title("Transverse Section (mid-length)", fontsize=12, fontweight="bold")
    ax.add_patch(patches.Rectangle((-wall_thickness, -soil_thickness - floor_thickness - depth_adults),
                                   outer_width, soil_thickness + floor_thickness + depth_adults,
                                   edgecolor='saddlebrown', facecolor='#f0d9b5', lw=2))
    ax.add_patch(patches.Rectangle((0, -floor_thickness - depth_adults),
                                   width, floor_thickness + depth_adults,
                                   edgecolor='black', facecolor='#a7d8ff', lw=2))
    # Annotate inner width and wall
    ax.annotate(f"Width: {width:.2f} m", (width/2, -outer_depth - 0.02), ha='center', va='top')
    ax.set_xlim(-wall_thickness * 1.2, width + wall_thickness * 1.2)
    ax.set_ylim(-outer_depth - 0.1, 0.2)
    ax.grid(True, linestyle="--", alpha=0.3)
    buf_trans = io.BytesIO()
    fig.savefig(buf_trans, format="png", bbox_inches="tight")
    buf_trans.seek(0)
    st.image(buf_trans, caption="Transverse Section", use_container_width=True)
    st.download_button("Download Transverse PNG", data=buf_trans.getvalue(), file_name="transverse_view.png", mime="image/png")
    plt.close(fig)

    # CSV of computed values for download
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(["parameter", "value", "units"])
    writer.writerow(["length", f"{length:.3f}", "m"])
    writer.writerow(["width", f"{width:.3f}", "m"])
    writer.writerow(["kids_depth", f"{depth_kids:.3f}", "m"])
    writer.writerow(["adults_depth", f"{depth_adults:.3f}", "m"])
    writer.writerow(["kids_zone_length", f"{kids_zone_length:.3f}", "m"])
    writer.writerow(["water_volume_m3", f"{water_volume_m3:.3f}", "m3"])
    writer.writerow(["excavation_volume_m3", f"{excavation_volume_m3:.3f}", "m3"])
    writer.writerow(["concrete_volume_m3", f"{concrete_total_m3:.3f}", "m3"])
    st.download_button("Download computed quantities (CSV)", data=csv_buf.getvalue(), file_name="pool_quantities.csv", mime="text/csv")

    st.success("✅ Drawings generated successfully!")