import streamlit as st
from inventory_manager import InventoryManager
import pandas as pd
from datetime import datetime
import validators

# Initialize inventory manager
inventory = InventoryManager()

# =====================================================================
# CSS (Reorganized, and Updated Colors, Font, and Input Styles)
# =====================================================================
st.markdown("""
<style>
    /* =====================================================================
       Global App Styles - Main area set to a light black (dark gray) with Helvetica font
    ===================================================================== */
    .stApp {
        background-color: #1a1a1a;
        font-family: Helvetica, sans-serif;
    }
    
    /* =====================================================================
       Sidebar Styles - Set to a light blue
    ===================================================================== */
    [data-testid="stSidebar"] {
        background-color: rgba(173, 216, 230, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(60, 60, 67, 0.3) !important;
    }
    
    /* Sidebar Navigation */
    .stRadio [role="radiogroup"] {
        gap: 8px;
    }
    
    .stRadio [role="radio"] div {
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stRadio [role="radio"] div:hover {
        background-color: rgba(120, 120, 128, 0.2) !important;
    }
    
    .stRadio [role="radio"][aria-checked="true"] div {
        background-color: rgba(120, 120, 128, 0.3) !important;
    }
    
    /* =====================================================================
       Product Card Styles
    ===================================================================== */
    .supply-card {
        background: #1c1c1e;
        border: 1px solid #2c2c2e;
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* =====================================================================
       Text Input Field Styles (for Search Supplies, Supply Name, Image URL)
    ===================================================================== */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 12px !important;
    }
    
    /* =====================================================================
       Other Input Field Styles (Number inputs and TextAreas remain dark)
    ===================================================================== */
    .stNumberInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #2c2c2e !important;
        color: #fff !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 12px !important;
    }
    
    /* =====================================================================
       Button Styles - All white background with black text
    ===================================================================== */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 10px !important;
    }
    .stButton > button:hover {
        background-color: #e6e6e6 !important;
    }
    .stButton > button:active {
        background-color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# SIDEBAR (UPDATED LABELS)
# =====================================================================
def create_sidebar():
    with st.sidebar:
        st.title("🛍️ Supply Manager")
        # Using radio buttons with updated labels
        selected = st.radio(
            "Menu",
            ["Dashboard", "Supplies", "Add Supply"],
            label_visibility="collapsed",
            key="main_nav"
        )
    return selected

# =====================================================================
# SUPPLY CARD (NOW USES IMAGE LINKS)
# =====================================================================
def display_supply_card(item):
    """Apple-style supply card with image"""
    description = item.get("description", "No description")
    st.markdown(f"""
    <div class="supply-card">
        <div style="display:flex; gap: 2rem; align-items: center;">
            <div style="flex: 1; min-width: 120px;">
                {f'<img src="{item["image_url"]}" style="border-radius:12px; width:100%; max-height:120px; object-fit:contain; background: #000;">' 
                 if "image_url" in item and item["image_url"] else 
                 '<div style="background: #2c2c2e; border-radius:12px; width:100%; height:120px; display:flex; align-items:center; justify-content:center; color:#a1a1a6;">No Image</div>'}
            </div>
            <div style="flex: 2;">
                <h3 style="margin-top:0; color:#f5f5f7;">{item["name"]}</h3>
                <p style="color:#636366;">{item.get("category", "Uncategorized")}</p>
                <p style="color:#ffffff; font-size: 1.1rem;">
                    <b>${item["price"]:.2f}</b> • 
                    <span style="color:{'#ff453a' if item['quantity'] < 5 else '#30d158'}">
                        {item["quantity"]} in stock
                    </span>
                </p>
                <p style="font-size:14px; color:#636366;">{description}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# MAIN DASH (UPDATED LABELS)
# =====================================================================
def show_dashboard():
    st.header("📊 Dashboard")
    items = inventory.get_all_items()
    
    if not items:
        st.info("No supplies in inventory yet")
        return
    
    df = pd.DataFrame(items)
    # Metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total Supplies", len(items))
    with cols[1]:
        total_value = (df['quantity'] * df['price']).sum()
        st.metric("Inventory Value", f"${total_value:,.2f}")
    with cols[2]:
        low_stock = sum(df['quantity'] < 5)
        st.metric("Low Stock Items", low_stock)
    
    # Recent supplies
    st.subheader("Recent Additions")
    recent_items = sorted(items, key=lambda x: x.get('date_added', ''), reverse=True)[:5]
    for item in recent_items:
        display_supply_card(item)

def show_supplies():
    st.header("📦 Supplies Inventory")
    items = inventory.get_all_items()
    
    if not items:
        st.info("No supplies in inventory yet")
        return
    
    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search supplies", placeholder="Name or category")
    with col2:
        category_filter = st.selectbox(
            "Filter by category",
            ["All"] + sorted(list(set(item["category"] for item in items))),
            index=0
        )
    
    # Filter items
    filtered_items = [
        item for item in items
        if (not search_term or 
            search_term.lower() in item["name"].lower() or 
            search_term.lower() in item["category"].lower())
        and (category_filter == "All" or item["category"] == category_filter)
    ]
    
    if not filtered_items:
        st.info("No supplies match your filters")
        return
    
    # Display supplies
    for item in filtered_items:
        display_supply_card(item)
        # Quick actions
        cols = st.columns(2)
        with cols[0]:
            if st.button(f"📝 Edit {item['name']}", key=f"edit_{item['id']}"):
                st.session_state.edit_item = item
                st.experimental_rerun()
        with cols[1]:
            if st.button(f"🗑️ Delete {item['name']}", key=f"del_{item['id']}", type="primary"):
                inventory.delete_item(item['id'])
                st.experimental_rerun()
        st.divider()
###############################################################
#ADDING SUPPLY FORM
################################################################
def add_supply_form():
    st.header("➕ Add New Supply")
    with st.form("add_form", clear_on_submit=True):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Supply Name*", placeholder="Printer Paper")
        with cols[1]:
            category = st.selectbox(
                "Category*",
                ["Office Supplies", "Electronics", "Furniture", "Other"],
                index=0
            )
        
        image_url = st.text_input(
            "Image URL", 
            placeholder="https://example.com/image.jpg",
            help="Paste a direct image URL"
        )
        
        cols = st.columns(2)
        with cols[0]:
            quantity = st.number_input("Quantity*", min_value=0, value=1)
        with cols[1]:
            price = st.number_input("Price*", min_value=0.0, value=9.99, step=0.01)
        
        description = st.text_area("Description", placeholder="Supply details...")
        
        submitted = st.form_submit_button("Add Supply", type="primary")
        if submitted:
            if not name:
                st.error("Supply name is required")
            elif image_url and not validators.url(image_url):
                st.error("Please enter a valid image URL")
            else:
                new_item = {
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "price": price,
                    "description": description if description else "No description",
                    "image_url": image_url if image_url else None,
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                inventory.add_item(new_item)
                st.success(f"Added {name} to inventory")
                st.session_state.main_nav = "Supplies"  # Switch to Supplies view
                st.experimental_rerun()
#################################################
# EDITING SUPPLY 
#################################################
def edit_supply_form():
    st.header("📝 Edit Supply")
    # Retrieve the item to be edited from session state
    item = st.session_state.edit_item
    with st.form("edit_form", clear_on_submit=True):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Supply Name*", value=item.get("name", ""))
        with cols[1]:
            # Set the default index based on the current category
            categories = ["Office Supplies", "Electronics", "Furniture", "Other"]
            default_index = categories.index(item.get("category", "Office Supplies")) if item.get("category", "Office Supplies") in categories else 0
            category = st.selectbox("Category*", categories, index=default_index)
        
        image_url = st.text_input(
            "Image URL", 
            value=item.get("image_url", ""),
            help="Paste a direct image URL"
        )
        
        cols = st.columns(2)
        with cols[0]:
            quantity = st.number_input("Quantity*", min_value=0, value=item.get("quantity", 1))
        with cols[1]:
            price = st.number_input("Price*", min_value=0.0, value=item.get("price", 9.99), step=0.01)
        
        description = st.text_area("Description", value=item.get("description", ""))
        
        submitted = st.form_submit_button("Update Supply", type="primary")
        if submitted:
            if not name:
                st.error("Supply name is required")
            elif image_url and not validators.url(image_url):
                st.error("Please enter a valid image URL")
            else:
                updated_item = {
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "price": price,
                    "description": description if description else "No description",
                    "image_url": image_url if image_url else None,
                    "date_added": item.get("date_added", datetime.now().strftime("%Y-%m-%d %H:%M"))
                }
                # Assuming InventoryManager has an update_item method
                inventory.update_item(item["id"], updated_item)
                st.success(f"Updated {name} successfully")
                del st.session_state.edit_item
                st.session_state.main_nav = "Supplies"
                st.experimental_rerun()

# =====================================================================
# MAIN APP
# =====================================================================
def main():
    # Initialize navigation state if not already set
    if 'main_nav' not in st.session_state:
        st.session_state.main_nav = "Dashboard"
    
    # If an item is marked for editing, show the edit form
    if "edit_item" in st.session_state:
        edit_supply_form()
    else:
        selected = create_sidebar()
        if selected == "Dashboard":
            show_dashboard()
        elif selected == "Supplies":
            show_supplies()
        elif selected == "Add Supply":
            add_supply_form()

if __name__ == "__main__":
    main()
