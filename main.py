import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Rate Calculator", layout="wide")

# ----------------------
# USERS & PASSWORDS
# ----------------------
USERS = {
    "admin": "admin123",
    "business": "business123"
}

# ----------------------
# SESSION STATE INIT
# ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


# ----------------------
# LOAD RATE TABLES
# ----------------------
@st.cache_data(ttl=1800)
def load_rate_tables():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSUIxBeSTWHg5CaTSAPDPo-cBOA_ah9M7sJ-GOpBemYl6VlJyQma9eWPVpLg2uiXk_0LPlHiimfZulz/pub?output=xlsx"

    air_df = pd.read_excel(url, sheet_name="Air Freight - SL")
    sea_df = pd.read_excel(url, sheet_name="Sea Freight - SL")

    latest_air_col = air_df.columns[-1]
    latest_sea_col = sea_df.columns[-1]

    air_rates = {}
    for _, row in air_df.iterrows():
        c = row["Country"]
        o = row["Origin"]
        r = row[latest_air_col]
        air_rates.setdefault(c, {})[o] = r

    sea_rates = {}
    for _, row in sea_df.iterrows():
        c = row["Country"]
        o = row["Origin"]
        r = row[latest_sea_col]
        sea_rates.setdefault(c, {})[o] = r

    return air_rates, sea_rates


air_rates, sea_rates = load_rate_tables()


# ----------------------
# LOGIN PAGE
# ----------------------
if not st.session_state.logged_in:
    st.title("🔑 Freight Calculator Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.role = "Admin" if username == "admin" else "Business"
            st.success(f"Logged in as {st.session_state.role}")
            st.rerun()  # ADD THIS LINE TO FIX DOUBLE CLICK ISSUE
        else:
            st.error("Invalid username or password")

else:

    role = st.session_state.role
    st.title(f"📦 Freight Rate Calculator ({role})")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    # ----------------------
    # CONSTANTS
    # ----------------------
    AIR_MARKUP = 1.2
    SEA_MARKUP = 1.3
    KG_PER_CBM = 166



    # ----------------------
    # INPUTS (MAIN ITEM)
    # ----------------------
    col_item, col_region, col_weight, col_width = st.columns([2, 2, 2, 2])

    all_countries = sorted(set(air_rates.keys()) | set(sea_rates.keys()))

    with col_item:
        st.subheader("📦 Item Information")
        supplier = st.text_input("Supplier", key="main_supplier")
        sqn = st.text_input("SQN", key="main_sqn")

    with col_region:
        st.subheader("🗺️ Region")
        country = st.selectbox("Country", all_countries, key="main_country")
        
        air_origins = set(air_rates.get(country, {}).keys())
        sea_origins = set(sea_rates.get(country, {}).keys())
        all_origins = sorted(air_origins | sea_origins)
        
        origin = st.selectbox("Origin", all_origins, key="main_origin")

    with col_weight:
        st.subheader("🧵 Weight")
        weight_value = st.number_input("Weight Value", min_value=0.0, step=0.1, key="main_weight")
        weight_type = st.selectbox("Weight Type", ["GSM (g/m²)", "GSM (kg/m²)", "GLM (g/m)"], key="main_weight_type")

    with col_width:
        st.subheader("📏 Width")
        width = st.number_input("Width", min_value=0.0, step=0.1, key="main_width")
        unit = st.selectbox("Unit", ["CM", "IN", "M"], key="main_unit")

    # Store main item in results list
    results = [{
        "supplier": supplier,
        "sqn": sqn,
        "country": country,
        "origin": origin,
        "weight_value": weight_value,
        "weight_type": weight_type,
        "width": width,
        "unit": unit
    }]

    # ----------------------
    # ADDITIONAL ITEMS
    # ----------------------
    st.divider()

    # Initialize additional rows in session state
    if "additional_rows" not in st.session_state:
        st.session_state.additional_rows = []

    # Add button for more items
    if st.button("➕ Add Another Item"):
        st.session_state.additional_rows.append({
            "supplier": "",
            "sqn": "",
            "country": "",
            "origin": "",
            "weight_value": 0.0,
            "weight_type": "GSM (g/m²)",
            "width": 0.0,
            "unit": "CM",
            "key": len(st.session_state.additional_rows)
        })

    # Display additional items
    for idx, row in enumerate(st.session_state.additional_rows):
        with st.expander(f"Additional Item {idx + 1}", expanded=True):
            cols = st.columns([2, 2, 2, 2, 1])
            
            with cols[0]:
                st.subheader("📦 Item Info")
                row["supplier"] = st.text_input("Supplier", value=row["supplier"], key=f"add_supplier_{idx}")
                row["sqn"] = st.text_input("SQN", value=row["sqn"], key=f"add_sqn_{idx}")
            
            with cols[1]:
                st.subheader("🗺️ Region")
                row["country"] = st.selectbox("Country", all_countries, key=f"add_country_{idx}")
                
                air_origins = set(air_rates.get(row["country"], {}).keys())
                sea_origins = set(sea_rates.get(row["country"], {}).keys())
                all_origins_add = sorted(air_origins | sea_origins)
                
                row["origin"] = st.selectbox("Origin", all_origins_add, key=f"add_origin_{idx}")
            
            with cols[2]:
                st.subheader("🧵 Weight")
                row["weight_value"] = st.number_input("Weight Value", min_value=0.0, step=0.1, value=row["weight_value"], key=f"add_weight_{idx}")
                row["weight_type"] = st.selectbox("Weight Type", ["GSM (g/m²)", "GSM (kg/m²)", "GLM (g/m)"], key=f"add_weight_type_{idx}")
            
            with cols[3]:
                st.subheader("📏 Width")
                row["width"] = st.number_input("Width", min_value=0.0, step=0.1, value=row["width"], key=f"add_width_{idx}")
                row["unit"] = st.selectbox("Unit", ["CM", "IN", "M"], key=f"add_unit_{idx}")
            
            with cols[4]:
                st.subheader(" ")
                st.write(" ")
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.additional_rows.pop(idx)
                    st.rerun()
            
            # Add to results
            results.append(row)

    # ----------------------
    # CALCULATIONS FOR ALL ITEMS
    # ----------------------
    all_results_data = []

    for idx, item in enumerate(results):
        # CONVERSIONS for each item
        width_m_item = item["width"] / 100 if item["unit"] == "CM" else (item["width"] * 0.0254 if item["unit"] == "IN" else item["width"])
        
        display_gsm_item = None
        
        if item["weight_type"] == "GSM (g/m²)":
            gsm_kg_item = item["weight_value"] / 1000
            display_gsm_item = item["weight_value"]
        elif item["weight_type"] == "GSM (kg/m²)":
            gsm_kg_item = item["weight_value"]
            display_gsm_item = item["weight_value"] * 1000
        else:  # GLM (g/m)
            gsm_g_item = item["weight_value"] / width_m_item if width_m_item > 0 else 0
            gsm_kg_item = gsm_g_item / 1000
            display_gsm_item = gsm_g_item
        
        kg_per_m_item = gsm_kg_item * width_m_item
        
        # RATE AVAILABILITY for each item
        air_rate_item = air_rates.get(item["country"], {}).get(item["origin"])
        sea_rate_item = sea_rates.get(item["country"], {}).get(item["origin"])
        
        air_available_item = air_rate_item is not None
        sea_available_item = sea_rate_item is not None
        
        # CALCULATIONS for each item
        final_air_rate_item = None
        final_sea_rate_item = None
        
        if air_available_item:
            air_freight_per_m_item = air_rate_item * kg_per_m_item
            final_air_rate_item = air_freight_per_m_item * AIR_MARKUP
        
        if sea_available_item:
            cbm_per_m_item = kg_per_m_item / KG_PER_CBM
            sea_freight_per_m_item = sea_rate_item * cbm_per_m_item
            final_sea_rate_item = sea_freight_per_m_item * SEA_MARKUP
        
        # Build result data for this item
        item_data = {
            "Item": f"Item {idx + 1}",
            "Supplier": item["supplier"],
            "SQN": item["sqn"], 
            "Country": item["country"],
            "Origin": item["origin"],
            "Weight Value": item["weight_value"],
            "Weight Type": item["weight_type"],
            "Converted GSM (g/m²)": round(display_gsm_item, 2) if item["weight_type"] == "GLM (g/m)" else None,
            "Width": item["width"],
            "Unit": item["unit"],
            "Width (m)": round(width_m_item, 4),
            "Weight/m (kg)": round(kg_per_m_item, 6),
        }
        
        # ---- Admin sees full rate breakdown
        if role == "Admin":
            if air_available_item:
                item_data.update({
                    "Air Rate ($/kg)": round(air_rate_item, 2),
                    "Final Air Rate ($)": round(final_air_rate_item, 4),
                })
            if sea_available_item:
                item_data.update({
                    "Sea Rate ($/CBM)": round(sea_rate_item, 2),
                    "Final Sea Rate ($)": round(final_sea_rate_item, 4),
                })
        # ---- Business sees ONLY final
        else:
            if air_available_item:
                item_data.update({
                    "Final Air Rate ($)": round(final_air_rate_item, 4),
                })
            if sea_available_item:
                item_data.update({
                    "Final Sea Rate ($)": round(final_sea_rate_item, 4),
                })
        
        all_results_data.append(item_data)

    # Display all results in single summary table
    df = pd.DataFrame(all_results_data)
    st.subheader("📋 Summary Table & Confirmation")
    
    # Display dataframe
    st.dataframe(df)
    
    # Create a copyable text version with table format
    st.divider()
    st.subheader("📋 Copy for Email")
    
    # Create a clean table text version for copying
    summary_text = "FREIGHT RATE CALCULATION SUMMARY\n"
    summary_text += "=" * 50 + "\n\n"
    
    # Header row
    headers = ["Item", "Supplier", "SQN", "Country", "Origin", "Weight", "Width", "Air Rate ($/m)", "Sea Rate ($/m)"]
    summary_text += " | ".join(headers) + "\n"
    summary_text += "-" * 100 + "\n"
    
    # Data rows
    for idx, row in df.iterrows():
        item_num = f"Item {idx + 1}"
        supplier = str(row['Supplier'])[:15] if len(str(row['Supplier'])) > 15 else str(row['Supplier'])
        sqn = str(row['SQN'])[:10] if len(str(row['SQN'])) > 10 else str(row['SQN'])
        country = str(row['Country'])[:10] if len(str(row['Country'])) > 10 else str(row['Country'])
        origin = str(row['Origin'])[:10] if len(str(row['Origin'])) > 10 else str(row['Origin'])
        weight = f"{row['Weight Value']} {row['Weight Type'][:8]}"
        width = f"{row['Width']} {row['Unit']}"
        
        # Get rates
        air_rate = f"${row['Final Air Rate ($)']:.4f}" if 'Final Air Rate ($)' in row and pd.notna(row['Final Air Rate ($)']) else "N/A"
        sea_rate = f"${row['Final Sea Rate ($)']:.4f}" if 'Final Sea Rate ($)' in row and pd.notna(row['Final Sea Rate ($)']) else "N/A"
        
        summary_text += f"{item_num:8} | {supplier:15} | {sqn:10} | {country:10} | {origin:10} | {weight:20} | {width:10} | {air_rate:15} | {sea_rate:15}\n"
    
    summary_text += "\n" + "=" * 50 + "\n\n"
    
    # Add details for each item in a cleaner format
    summary_text += "DETAILED BREAKDOWN:\n"
    summary_text += "-" * 50 + "\n\n"
    
    for idx, row in df.iterrows():
        summary_text += f"{idx + 1}. {row['Supplier']} - {row['SQN']}:\n"
        summary_text += f"   • Country/Origin: {row['Country']} / {row['Origin']}\n"
        summary_text += f"   • Weight: {row['Weight Value']} {row['Weight Type']}"
        if pd.notna(row['Converted GSM (g/m²)']):
            summary_text += f" (Converted: {row['Converted GSM (g/m²)']} g/m²)"
        summary_text += "\n"
        summary_text += f"   • Width: {row['Width']} {row['Unit']} = {row['Width (m)']} m\n"
        summary_text += f"   • Weight per meter: {row['Weight/m (kg)']} kg/m\n"
        
        if 'Final Air Rate ($)' in row and pd.notna(row['Final Air Rate ($)']):
            summary_text += f"   • Air Freight Rate: ${row['Final Air Rate ($)']:.4f} per meter\n"
        if 'Final Sea Rate ($)' in row and pd.notna(row['Final Sea Rate ($)']):
            summary_text += f"   • Sea Freight Rate: ${row['Final Sea Rate ($)']:.4f} per meter\n"
        
        summary_text += "\n"
    
    # Add confirmation at the end
    summary_text += "CONFIRMATION:\n"
    summary_text += "=" * 50 + "\n\n"
    summary_text += "Please find below the approximate per meter/per piece freight cost based on your request.\n\n"
    summary_text += "Kindly note that these costs have been calculated using the material details provided by your team, "
    summary_text += "along with the current market freight rates. However, please be aware that these rates are subject "
    summary_text += "to change and may vary from the actual costs due to high volatility in the freight market.\n\n"
    summary_text += "These outputs are calculated and confirmed by Logistics.\n"
    
    # Display in a text area for easy copying
    st.text_area("📄 Copy the text below for email (Ctrl+A then Ctrl+C):", 
                value=summary_text, 
                height=400,
                key="copyable_summary")
    
    # Also show a clean markdown version for reference
    st.divider()
    st.subheader("📧 Email-ready Format Preview")
    
    # Create markdown table preview
    table_data = []
    for idx, row in df.iterrows():

        # Format weight with type
        weight_display = f"{row['Weight Value']}"
        if pd.notna(row['Converted GSM (g/m²)']):
            weight_display += f" {row['Weight Type']}:-({row['Converted GSM (g/m²)']} g/m²)"
        else:
            weight_display += f" {row['Weight Type']}"
        
        # Format width
        width_display = f"{row['Width']} {row['Unit']}:-({row['Width (m)']} m)"
        
        # Format weight per meter
        weight_per_m = f"{row['Weight/m (kg)']} kg/m"
        air_rate = f"${row['Final Air Rate ($)']:.4f}" if 'Final Air Rate ($)' in row and pd.notna(row['Final Air Rate ($)']) else "N/A"
        sea_rate = f"${row['Final Sea Rate ($)']:.4f}" if 'Final Sea Rate ($)' in row and pd.notna(row['Final Sea Rate ($)']) else "N/A"
        
        table_data.append({
            "Item": idx + 1,
            "Supplier": row['Supplier'],
            "SQN": row['SQN'],
            "Country": row['Country'],
            "Origin": row['Origin'],
            "Weight": weight_display,
            "Width": width_display,
            "Weight/m": weight_per_m,
            "Air Rate": air_rate,
            "Sea Rate": sea_rate
        })
    
    # Display as markdown table (WITHOUT TABULATE - simpler method)
    if table_data:
        # Simple HTML table without tabulate
        html_table = "<table style='width:100%; border-collapse: collapse;'>"
        html_table += "<tr style='background-color: #f2f2f2;'>"
        for col in ["Item", "Supplier", "SQN", "Country", "Origin", "Weight", "Width", "Weight/m", "Air Rate", "Sea Rate"]:
            html_table += f"<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{col}</th>"
        html_table += "</tr>"
        
        for row in table_data:
            html_table += "<tr>"
            for col in ["Item", "Supplier", "SQN", "Country", "Origin", "Weight", "Width", "Weight/m", "Air Rate", "Sea Rate"]:
                html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{row[col]}</td>"
            html_table += "</tr>"
        html_table += "</table>"
        
        st.markdown(html_table, unsafe_allow_html=True)
    
    # Confirmation note below
    st.info("""
    **Confirmation:**  
    Please find below the approximate per meter/per piece freight cost based on your request.  
    
    Kindly note that these costs have been calculated using the material details provided by your team, 
    along with the current market freight rates. However, please be aware that these rates are subject 
    to change and may vary from the actual costs due to high volatility in the freight market.  
    
    These outputs are calculated and confirmed by Logistics.
    """)
    
    # ----------------------
    # DISPLAY RESULTS FOR EACH ITEM
    # ----------------------
    for idx, item_data in enumerate(all_results_data):
        # Get the corresponding original item for GLM info
        item = results[idx]
        
        # Create expander for each item's freight results
        with st.expander(f"📊 Freight Results - Item {idx + 1}: {item['supplier'] or 'No Supplier'} - {item['sqn'] or 'No SQN'}", expanded=idx==0):
            col_air, col_sea = st.columns(2)
            
            # AIR
            with col_air:
                st.markdown("### ✈️ Air Freight")
                
                air_available_item = "Air Rate ($/kg)" in item_data or "Final Air Rate ($)" in item_data
                
                if air_available_item:
                    if role == "Admin":
                        st.metric("Width (m)", f"{item_data['Width (m)']:.3f}")
                        st.metric("Weight/m (kg)", f"{item_data['Weight/m (kg)']:.4f}")
                        st.metric("Air Rate ($/kg)", f"${item_data['Air Rate ($/kg)']:.2f}")
                        air_freight_per_m = item_data['Air Rate ($/kg)'] * item_data['Weight/m (kg)']
                        st.metric("Freight / m ($)", f"${air_freight_per_m:.4f}")
                        st.metric("Final Rate ($)", f"${item_data['Final Air Rate ($)']:.4f}")
                        st.caption(f"Air Markup: {AIR_MARKUP}")
                    else:
                        st.metric("Final Rate ($)", f"${item_data['Final Air Rate ($)']:.4f}")
                else:
                    st.warning("✈️ Air freight not available for this route")
            
            # SEA
            with col_sea:
                st.markdown("### 🚢 Sea Freight")
                
                sea_available_item = "Sea Rate ($/CBM)" in item_data or "Final Sea Rate ($)" in item_data
                
                if sea_available_item:
                    if role == "Admin":
                        cbm_per_m = item_data['Weight/m (kg)'] / KG_PER_CBM
                        st.metric("CBM / m", f"{cbm_per_m:.6f}")
                        st.metric("Sea Rate ($/CBM)", f"${item_data['Sea Rate ($/CBM)']:.2f}")
                        sea_freight_per_m = item_data['Sea Rate ($/CBM)'] * cbm_per_m
                        st.metric("Freight / m ($)", f"${sea_freight_per_m:.4f}")
                        st.metric("Final Rate ($)", f"${item_data['Final Sea Rate ($)']:.4f}")
                        st.caption(f"Sea Markup: {SEA_MARKUP}")
                    else:
                        st.metric("Final Rate ($)", f"${item_data['Final Sea Rate ($)']:.4f}")
                else:
                    st.warning("🚢 Sea freight not available for this route")
            
            # Confirmation text for each item
            st.divider()
            msg = (
                f"Item {idx + 1}: With inputs — weight: {item['weight_value']} {item['weight_type']}, "
                f"width: {item['width']} {item['unit']}, region: {item['country']} - {item['origin']} — "
            )
            
            if air_available_item and sea_available_item:
                msg += f"final Air and Sea rates are ${item_data['Final Air Rate ($)']:.4f} and ${item_data['Final Sea Rate ($)']:.4f} respectively."
            elif air_available_item:
                msg += f"final Air rate is ${item_data['Final Air Rate ($)']:.4f}. Sea freight is not available."
            elif sea_available_item:
                msg += f"final Sea rate is ${item_data['Final Sea Rate ($)']:.4f}. Air freight is not available."
            
            st.text(msg + " These outputs are calculated and confirmed by Logistics.")
            
            # ----------------------
            # CALCULATION EXPLANATION for each item
            # ----------------------
            st.subheader("🧮 How These Charges Were Calculated")
            
            lines = []
            
            # ---- Width
            lines.append(f"• Width converted to meters = {item_data['Width (m)']:.4f} m.")
            
            # ---- GLM case
            if item['weight_type'] == "GLM (g/m)":
                lines.append(f"• GLM to GSM conversion: {item['weight_value']} g/m ÷ {item_data['Width (m)']:.4f} m = {item_data['Converted GSM (g/m²)']:.2f} g/m².")
            
            # ---- kg per meter
            lines.append(f"• Fabric weight per running meter = GSM × width = {item_data['Weight/m (kg)']:.6f} kg/m.")
            
            # ---- AIR
            if air_available_item:
                if role == "Admin":
                    air_freight_per_m = item_data['Air Rate ($/kg)'] * item_data['Weight/m (kg)']
                    lines.append(f"• Air freight per meter = {item_data['Air Rate ($/kg)']:.2f} × {item_data['Weight/m (kg)']:.6f} = {air_freight_per_m:.6f} USD.")
                    lines.append(f"• Final Air rate = {air_freight_per_m:.6f} × markup {AIR_MARKUP} = {item_data['Final Air Rate ($)']:.6f} USD.")
                else:
                    lines.append("• Air freight = (Air base rate × kg per meter) adjusted to final selling rate.")
            
            # ---- SEA
            if sea_available_item:
                if role == "Admin":
                    cbm_per_m = item_data['Weight/m (kg)'] / KG_PER_CBM
                    sea_freight_per_m = item_data['Sea Rate ($/CBM)'] * cbm_per_m
                    lines.append(f"• CBM per meter = {item_data['Weight/m (kg)']:.6f} ÷ {KG_PER_CBM} = {cbm_per_m:.8f}.")
                    lines.append(f"• Sea freight per meter = {item_data['Sea Rate ($/CBM)']:.2f} × {cbm_per_m:.8f} = {sea_freight_per_m:.6f} USD.")
                    lines.append(f"• Final Sea rate = {sea_freight_per_m:.6f} × markup {SEA_MARKUP} = {item_data['Final Sea Rate ($)']:.6f} USD.")
                else:
                    lines.append("• Sea freight = (CBM per meter × Sea base rate) adjusted to final selling rate.")
            
            st.markdown("\n".join(lines))
