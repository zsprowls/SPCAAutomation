print("OCCUPANCYMAPP IS RUNNING")
import streamlit as st
import json
from pathlib import Path
import plotly.graph_objects as go

# --- Directory setup ---
script_dir = Path(__file__).parent.absolute()
layouts_dir = script_dir / 'layouts'
layouts_dir.mkdir(exist_ok=True)

# --- PetPoint Location & SubLocation data (shortened for brevity, add all as needed) ---
LOCATION_DATA = {
    "Adoptions Lobby": ["-Rabbitat 1", "-Rabbitat 2", "-Turtle Tank", "-Adoptions Lobby"],
    "Cat Adoption Room G": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08"],
    "Dog Adoptions A": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09"],
    # ... add all your locations here ...
}

def load_layout(room_name: str):
    layout_file = layouts_dir / f"{room_name}.json"
    if layout_file.exists():
        with open(layout_file, 'r') as f:
            return json.load(f)
    return {"boxes": []}

def save_layout(room_name: str, layout_data):
    layout_file = layouts_dir / f"{room_name}.json"
    with open(layout_file, 'w') as f:
        json.dump(layout_data, f, indent=2)

def get_room_list():
    return list(LOCATION_DATA.keys())

def create_layout_editor(room_name: str):
    # Always load from disk for the selected room
    layout_data = load_layout(room_name)
    boxes = layout_data.get('boxes', [])
    selected_box = st.session_state.get("selected_box", None)

    # --- Canvas UI (dummy, not interactive in this minimal version) ---
    st.write("**Canvas would go here.** (For demo, select a box below to edit properties.)")
    if boxes:
        box_labels = [f"{i+1}: {b.get('label','') or 'Box'}" for i, b in enumerate(boxes)]
        selected_box = st.selectbox("Select Box", list(range(len(boxes))), format_func=lambda i: box_labels[i], key="box_select")
    else:
        selected_box = None

    # --- Add a new box (for demo) ---
    if st.button("Add Box"):
        boxes.append({
            "label": "",
            "location": list(LOCATION_DATA.keys())[0],
            "sublocation": LOCATION_DATA[list(LOCATION_DATA.keys())[0]][0],
            "width": 100,
            "height": 100,
            "x": 50,
            "y": 50
        })
        save_layout(room_name, {"boxes": boxes})
        st.experimental_rerun()

    return boxes, selected_box

def display_layout(room_name: str):
    layout_data = load_layout(room_name)
    fig = go.Figure()
    for box in layout_data.get('boxes', []):
        fig.add_shape(
            type="rect",
            x0=box['x'],
            y0=box['y'],
            x1=box['x'] + box['width'],
            y1=box['y'] + box['height'],
            line=dict(color="Black", width=2),
            fillcolor="LightGray",
        )
        fig.add_annotation(
            x=box['x'] + box['width']/2,
            y=box['y'] + box['height']/2,
            text=f"{box.get('label','')}\n{box.get('location','')}\n{box.get('sublocation','')}",
            showarrow=False,
            font=dict(size=12)
        )
    fig.update_layout(
        title=f"Room Layout: {room_name}",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(page_title="Room Layout Editor", layout="wide")
    st.title("Room Layout Editor")

    rooms = get_room_list()
    selected_room = st.selectbox("Select Room", rooms)

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if st.button("Change Layout"):
        st.session_state.edit_mode = not st.session_state.edit_mode

    if st.session_state.edit_mode:
        st.subheader(f"Editing Layout: {selected_room}")
        boxes, selected_box = create_layout_editor(selected_room)
        st.subheader("Box Properties")
        if selected_box is not None and 0 <= selected_box < len(boxes):
            box = boxes[selected_box]
            label = st.text_input("Label", value=box.get('label', ''), key=f"label_{selected_room}_{selected_box}")
            location = st.selectbox(
                "Location",
                list(LOCATION_DATA.keys()),
                index=list(LOCATION_DATA.keys()).index(box.get('location', '') or list(LOCATION_DATA.keys())[0]),
                key=f"location_{selected_room}_{selected_box}"
            )
            sublocation_options = LOCATION_DATA[location]
            sublocation = st.selectbox(
                "SubLocation",
                sublocation_options,
                index=sublocation_options.index(box.get('sublocation', '') or sublocation_options[0]),
                key=f"sublocation_{selected_room}_{selected_box}"
            )
            width = st.number_input("Width", min_value=10, max_value=800, value=int(box.get('width', 100)), key=f"width_{selected_room}_{selected_box}")
            height = st.number_input("Height", min_value=10, max_value=600, value=int(box.get('height', 100)), key=f"height_{selected_room}_{selected_box}")
            x = st.number_input("X", min_value=0, max_value=800, value=int(box.get('x', 0)), key=f"x_{selected_room}_{selected_box}")
            y = st.number_input("Y", min_value=0, max_value=600, value=int(box.get('y', 0)), key=f"y_{selected_room}_{selected_box}")
            if st.button("Update Box", key=f"update_{selected_room}_{selected_box}"):
                boxes[selected_box] = {
                    "label": label,
                    "location": location,
                    "sublocation": sublocation,
                    "width": width,
                    "height": height,
                    "x": x,
                    "y": y
                }
                save_layout(selected_room, {"boxes": boxes})
                st.success("Box updated and saved!")
            if st.button("Delete Box", key=f"delete_{selected_room}_{selected_box}"):
                boxes.pop(selected_box)
                save_layout(selected_room, {"boxes": boxes})
                st.success("Box deleted and saved!")
        if st.button("Save Layout", key=f"save_{selected_room}"):
            save_layout(selected_room, {"boxes": boxes})
            st.success("Layout saved to disk!")
    else:
        st.subheader(f"Viewing Layout: {selected_room}")
        display_layout(selected_room)

if __name__ == "__main__":
    main()