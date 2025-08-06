import streamlit as st

st.set_page_config(page_title="Test", layout="wide")
st.title("If you see this, Streamlit and st are working.")

print("OCCUPANCYMAPP IS RUNNING")
import pandas as pd
import json
from pathlib import Path
import os
from typing import Dict, List, Tuple, Optional
import streamlit.components.v1 as components
import plotly.graph_objects as go


# Get the directory where the script is located
script_dir = Path(__file__).parent.absolute()
# Get the parent directory (SPCAAutomation)
parent_dir = script_dir.parent
# Get the path to the files directory
files_dir = parent_dir / '__Load Files Go Here__'
# Create layouts directory if it doesn't exist
layouts_dir = script_dir / 'layouts'
layouts_dir.mkdir(exist_ok=True)

# PetPoint Location & SubLocation data
LOCATION_DATA = {
    "Adoptions Counseling Offices": ["-Dog Counseling 122", "-Dog Counseling 123", "-Krissi's Office"],
    "Adoptions Lobby": ["-Rabbitat 1", "-Rabbitat 2", "-Turtle Tank", "-Adoptions Lobby"],
    "Agents Office": ["-Agents Office", "-Evidence"],
    "Animal Care Office, Room 197": ["-Animal Care Office"],
    "Cat Adoption Condo Rooms": [
        "-Catiat 1", "-Catiat 2", "-Catiat 3", "-Catiat 4", "-Catiat 5",
        "-Condo A", "-Condo B", "-Condo C", "-Condo D", "-Condo E", "-Condo F",
        "-Counselling Room 110", "-Ferret Cage", "-Meet & Greet 109A", "-Meet & Greet 109B",
        "-Rabbitat 1", "-Rabbitat 2"
    ],
    "Cat Adoption Room G": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08"],
    "Cat Adoption Room H": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08"],
    "Cat Behavior Room I": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08"],
    "Cat Behavior, room 174": ["-Cat Behavior 174"],
    "Cat Isolation 230": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5"],
    "Cat Isolation 231": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5", "-Cage 6", "-Cage 7", "-Cage 8", "-Cage 9"],
    "Cat Isolation 232": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5", "-Cage 6"],
    "Cat Isolation 233": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5", "-Cage 6"],
    "Cat Isolation 234": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5", "-Cage 6"],
    "Cat Isolation 235": ["-Cage 1", "-Cage 2", "-Cage 3", "-Cage 4", "-Cage 5", "-Cage 6", "-Cage 7", "-Cage 8", "-Cage 9"],
    "Cat Recovery": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09", "-10", "-11", "-12", "-13", "-14", "-15", "-16", "-17", "-18"],
    "Cat Treatment": [
        "-01", "-01 - A", "-01 - B", "-02", "-02 - A", "-02 - B",
        "-03", "-03 - A", "-03 - B", "-04", "-04 - A", "-04 - B",
        "-05", "-05 - A", "-05 - B", "-06", "-06 - A", "-06 - B",
        "A", "B", "C", "D", "E", "F", "G", "H"
    ],
    "Dental Area": ["-Cage 1", "-Incubtor"],
    "Dog Adoptions A": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09"],
    "Dog Adoptions B": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09"],
    "Dog Adoptions C": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09"],
    "Dog Adoptions D": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09", "-10"],
    "Dog Holding E": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09", "-10", "-11", "-12"],
    "Dog Holding F": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-09", "-10", "-11", "-12"],
    "Feature Room 1": ["-Feature Room 1"],
    "Feature Room 2": ["-Feature Room 2"],
    "Foster Care Room": ["-01", "-02", "-03", "-04", "-05", "-06", "-07", "-08", "-Foster Care Room"],
    "ICU": [
        "-01", "-01 - A", "-01 - B", "-02", "-02 - A", "-02 - B",
        "-03", "-03 - A", "-03 - B", "-04", "-04 - A", "-04 - B",
        "-05", "-05 - A", "-05 - B", "-06", "-06 - A", "-06 - B",
        "-07", "-08", "-Incubator"
    ],
    "Large Dog Recovery": ["-01", "-02", "-03", "-04"],
    "Main Offices": ["-Barb H's Office", "-Gina's Office", "-Sue's Office"],
    "Multi-Animal Holding, Room 227": ["-Bird Cage", "-Boaphile 1", "-Boaphile 2", "-Mammal 1", "-Mammal 2"],
    "Multi-Animal Holding, Room 229": [
        "-Boaphile 1", "-Boaphile 2", "-Cat 1", "-Cat 2", "-Cat 3", "-Cat 4", "-Cat 5", "-Cat 6",
        "-Multi Animal Holding", "-Rabbitat 1", "-Rabbitat 2", "-Room 1", "-Room 2",
        "-Turtle Tank 1", "-Turtle Tank 2"
    ],
    "Small Animals & Exotics": [
        "-Bird Cage 1", "-Bird Cage 2", "-Bird Cage 3", "-Bird Cage 4", "-Bird Cage, Extra",
        "-Coutnertop Cage 1", "-Coutnertop Cage 2", "-Mammal 1", "-Mammal 2", "-Mammal 3", "-Mammal 4",
        "-Reptiles 1", "-Reptiles 2", "-Reptiles 3", "-Reptiles 4", "-Reptiles 5",
        "-Small Animal 1", "-Small Animal 2", "-Small Animal 3", "-Small Animal 4",
        "-Small Animal 5", "-Small Animal 6", "-Small Animal 7", "-Small Animal 8",
        "-Small Animals & Exotics", "-Turtle Tank 2"
    ],
    "Small Dog Recovery": ["-01", "-02", "-03", "-04", "-05", "-06"]
}

# Initialize session state
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'selected_room' not in st.session_state:
    st.session_state.selected_room = None
if 'layout_data' not in st.session_state:
    st.session_state.layout_data = {}
if 'selected_box' not in st.session_state:
    st.session_state.selected_box = None

def load_layout(room_name: str) -> Dict:
    """Load layout data for a specific room."""
    layout_file = layouts_dir / f"{room_name}.json"
    if layout_file.exists():
        with open(layout_file, 'r') as f:
            return json.load(f)
    return {"boxes": []}

def save_layout(room_name: str, layout_data: Dict):
    """Save layout data for a specific room."""
    layout_file = layouts_dir / f"{room_name}.json"
    with open(layout_file, 'w') as f:
        json.dump(layout_data, f, indent=2)

def get_room_list() -> List[str]:
    """Get list of available rooms from the location data."""
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
            "label": "New Box",
            "location": list(LOCATION_DATA.keys())[0],
            "sublocation": LOCATION_DATA[list(LOCATION_DATA.keys())[0]][0],
            "width": 300,
            "height": 300,
            "x": 200,
            "y": 200
        })
        save_layout(room_name, {"boxes": boxes})
        st.experimental_rerun()

    return boxes, selected_box

def display_layout(room_name: str):
    """Display the saved layout using simple Streamlit components."""
    layout_data = load_layout(room_name)
    
    st.subheader(f"Room Layout: {room_name}")
    
    # Create a simple grid layout using Streamlit columns
    for i, box in enumerate(layout_data.get('boxes', [])):
        # Create a container for each box
        with st.container():
            # Add some spacing
            st.write("---")
            
            # Create a styled box using Streamlit components
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Create a large, visible box
                st.markdown(f"""
                <div style="
                    background-color: #e6f3ff;
                    border: 3px solid #0066cc;
                    border-radius: 10px;
                    padding: 30px;
                    margin: 20px 0;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    color: #000;
                    min-height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <div>
                        <strong>{box.get('label', 'BOX')}</strong><br><br>
                        {box.get('location', '')}<br>
                        {box.get('sublocation', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add box details below
            with col2:
                st.write(f"**Box {i+1} Details:**")
                st.write(f"Position: ({box.get('x', 0)}, {box.get('y', 0)})")
                st.write(f"Size: {box.get('width', 0)} x {box.get('height', 0)}")
    
    # If no boxes, show a message
    if not layout_data.get('boxes', []):
        st.info("No boxes configured for this room. Use 'Change Layout' to add boxes.")

def main():
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