from dash import html, dcc, dash_table
import io
import re
import base64
import pandas as pd
import datetime
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, HRFlowable

def blankFigure():
# blank figure when no data is present
    return {
        'data': [],
        'layout': go.Layout(
            xaxis={
                'showticklabels': False,
                'ticks': '',
                'showgrid': False,
                'zeroline': False
            },
            yaxis={
                'showticklabels': False,
                'ticks': '',
                'showgrid': False,
                'zeroline': False
            }
        )
    }

def generate_tab_fig(day, tab, fig):
    if fig is None:
        fig = blankFigure()

    modeBarButtonsToRemove = ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                              'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian',
                              'zoom3d', 'pan3d', 'resetCameraDefault3d', 'resetCameraLastSave3d', 'hoverClosest3d',
                              'orbitRotation', 'tableRotation', 'zoomInGeo', 'zoomOutGeo', 'resetGeo',
                              'hoverClosestGeo', 'sendDataToCloud', 'hoverClosestGl2d', 'hoverClosestPie',
                              'toggleHover', 'resetViews', 'toggleSpikelines', 'resetViewMapbox']

    day_abbrv = day.lower()[:3]
    div_style = {'background': 'white', 'display': 'block' if day_abbrv == tab[-3:] else 'none', 'width': '100%'}

    return html.Div([
        dcc.Loading(id='loading-icon-'+day_abbrv, children=[
            dcc.Graph(
                figure=fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': modeBarButtonsToRemove,
                    'showAxisDragHandles': True,
                    'toImageButtonOptions': {'filename': day_abbrv},
                    'responsive': True,
                },
                id='schedule_'+day_abbrv,
            )], type='circle', color='#0f172a')],
        style=div_style,
        id='schedule_' + day_abbrv + '_div',
    )


def generate_weekday_tab(day):
    tab_style = {
        'height': '44px',
        'padding': '10px 24px',
        'backgroundColor': '#f8fafc',
        'border': 'none',
        'borderBottom': '1px solid #e2e8f0',
        'fontFamily': '"Inter", sans-serif',
        'fontWeight': '500',
        'fontSize': '1.5rem',
        'color': '#64748b',
        'cursor': 'pointer',
        'transition': 'all 0.15s ease'
    }
    selected_tab_style = {
        'height': '44px',
        'padding': '10px 24px',
        'backgroundColor': '#ffffff',
        'border': 'none',
        'borderTop': '3px solid #0f172a',
        'borderLeft': '1px solid #e2e8f0',
        'borderRight': '1px solid #e2e8f0',
        'fontFamily': '"Inter", sans-serif',
        'fontWeight': '700',
        'fontSize': '1.5rem',
        'color': '#0f172a',
    }

    return dcc.Tab(
        label=day,
        value='tab-'+day.lower()[:3],
        style=tab_style,
        selected_style=selected_tab_style,
    )



def convert_term_title_to_code(term_title):
    """
    Converts a descriptive term title (e.g., "Fall Semester 2026" or "Spring 2025")
    into a standard Banner code format (YYYY50, YYYY30, or YYYY40).
    """
    if not term_title:
        return "Unknown"

    # Standardize to lowercase for resilient matching
    title_lower = str(term_title).lower()

    # Extract any 4-digit sequence representing the year
    year_match = re.search(r'\b(\d{4})\b', title_lower)
    if not year_match:
        return "Unknown"
    year = year_match.group(1)

    # Map key words to their respective Banner code suffixes
    semester_mapping = {
        'spring': '30',
        'summer': '40',
        'fall': '50'
    }

    # Check which suffix matches the text string
    suffix = ""
    for term_keyword, code_suffix in semester_mapping.items():
        if term_keyword in title_lower:
            suffix = code_suffix
            break

    # Return formatted string if suffix found, otherwise return just the year
    return f"{year}{suffix}" if suffix else year


def apply_custom_course_titles(df):
    """
    Overwrites the 'Title' column in the DataFrame with custom academic naming rules.
    Safely handles duplicate course rows (multiple sections) using a relational merge.
    """
    course_titles = [
        ["MTH 1051", "Principles of Math in Chem Lab"],
        ["MTH 1080", "Mathematics for Liberal Arts"],
        ["MTH 1081", "Math. for Lib. Arts with Lab"],
        ["MTH 1082", "Math. for Liberal Arts Lab"],
        ["MTH 1101", "College Algebra for Calc Lab"],
        ["MTH 1108", "College Algebra Stretch Part I"],
        ["MTH 1109", "College Alg. Stretch Part II"],
        ["MTH 1110", "College Algebra for Calculus"],
        ["MTH 1111", "College Alg. for Calc with Lab"],
        ["MTH 1112", "College Algebra thru Modeling"],
        ["MTH 1115", "College Alg thru Mdlng w Lab"],
        ["MTH 1116", "College Alg thru Mdlng Lab"],
        ["MTH 1120", "College Trigonometry"],
        ["MTH 1210", "Introduction to Statistics"],
        ["MTH 1310", "Finite Math - Mgmt & Soc Scncs"],
        ["MTH 1311", "Finite Math-Mgmt -with Lab"],
        ["MTH 1312", "Finite Mathematics Lab"],
        ["MTH 1320", "Calculus - Mgmt & Soc Sciences"],
        ["MTH 1400", "Precalculus Mathematics"],
        ["MTH 1410", "Calculus I"],
        ["MTH 1610", "Integrated Mathematics I"],
        ["MTH 2140", "Computational Matrix Algebra"],
        ["MTH 2410", "Calculus II"],
        ["MTH 2420", "Calculus III"],
        ["MTH 2520", "R Programming"],
        ["MTH 2540", "Scientific Computing"],
        ["MTH 2620", "Integrated Mathematics II"],
        ["MTH 3100", "Intro to Mathematical Proofs"],
        ["MTH 3110", "Abstract Algebra I"],
        ["MTH 3130", "Applied Methods in Linear Algebra"],
        ["MTH 3140", "Linear Algebra"],
        ["MTH 3170", "Discrete Math for Comp Science"],
        ["MTH 3210", "Probability and Statistics"],
        ["MTH 3220", "Statistical Methods"],
        ["MTH 3230", "Stochastic Processes"],
        ["MTH 3240", "Environmental Statistics"],
        ["MTH 3270", "Data Science"],
        ["MTH 3400", "Chaos & Nonlinear Dynamics"],
        ["MTH 3420", "Differential Equations"],
        ["MTH 3430", "Mathematical Modeling"],
        ["MTH 3440", "Partial Differential Equations"],
        ["MTH 3450", "Complex Variables"],
        ["MTH 3470", "Intro Discrete Math & Modeling"],
        ["MTH 3510", "SAS Programming"],
        ["MTH 3640", "History of Mathematics"],
        ["MTH 3650", "Foundations of Geometry"],
        ["MTH 4110", "Abstract Algebra II"],
        ["MTH 4150", "Elementary Number Theory"],
        ["MTH 4210", "Probability Theory"],
        ["MTH 4230", "Regression/Computational Stats"],
        ["MTH 4250", "Statistical Theory"],
        ["MTH 4290", "Senior Statistics Project"],
        ["MTH 4410", "Real Analysis I"],
        ["MTH 4420", "Real Analysis II"],
        ["MTH 4440", "Partial Differential Equations"],
        ["MTH 4480", "Numerical Analysis I"],
        ["MTH 4490", "Numerical Analysis II"],
        ["MTH 4640", "History of Mathematics"],
        ["MTH 4660", "Introduction to Topology"],
        ["MTL 3600", "Mathematics of Elementary Curriculum"],
        ["MTL 3620", "Mathematics of Secondary Curriculum"],
        ["MTL 3630", "Teaching Secondary Mathematics"],
        ["MTL 3638", "Secondry Mathematics Field Experience"],
        ["MTL 3750", "Number & Alg in the K-8 Curriculum"],
        ["MTL 3760", "Geom & Stats in the K-8 Curriculum"],
        ["MTL 3850", "STEM Teaching and Learning"],
        ["MTL 3858", "STEM Practicum"],
        ["MTL 4630", "Teaching Secondary Mathematics"],
        ["MTL 4690", "Student Teaching & Seminar: Secondary 7-12"],
        ["MTLM 5020", "Integrated Mathematics II"],
        ["MTLM 5600", "Mathematics of the Elementary Curriculum"],
        ["MTLM 5610", "Elementary Mathematics from an Advanced Perspective"]
    ]

    # Save exact layout structure to guarantee no columns drop or swap places
    original_columns = list(df.columns)
    if 'Title' not in original_columns:
        original_columns.append('Title')

    # Convert lookup mapping array to a dedicated dataframe
    df_titles = pd.DataFrame(course_titles, columns=["Class", "CleanTitle"])
    df_titles['MatchKey'] = df_titles['Class'].str.replace(" ", "", regex=False)
    df_titles = df_titles.drop_duplicates(subset=['MatchKey'])

    # Build join key on your active data frame
    if 'Course' in df.columns:
        df['MatchKey'] = df['Course'].astype(str).str.replace(" ", "", regex=False)
    else:
        df['MatchKey'] = df['Subj'].astype(str).str.strip() + df['Nmbr'].astype(str).str.strip()

    # Left join custom titles database onto your schedule entries frame
    df = df.merge(df_titles[['MatchKey', 'CleanTitle']], on='MatchKey', how='left')

    # Overwrite your Title column. If no match exists, revert to original spreadsheet title.
    if 'Title' in df.columns:
        df['Title'] = df['CleanTitle'].combine_first(df['Title'])
    else:
        df['Title'] = df['CleanTitle']

    # Remove operational workspace columns and cleanly output the frame
    df = df.drop(columns=['MatchKey', 'CleanTitle'], errors='ignore')

    # Fill remaining text empty cells to maintain Datatable integrity
    df['Title'] = df['Title'].fillna("")

    return df[original_columns]


def convert_to_24hr(time_str):
    if not time_str or time_str.strip() == "TBA" or "-" not in time_str:
        return time_str

    time_str = time_str.strip()
    match = re.match(r'(\d{4})-(\d{4})(AM|PM)', time_str)
    if not match:
        return time_str

    start_str, end_str, meridian = match.groups()
    start_hour, start_min = int(start_str[:2]), int(start_str[2:])
    end_hour, end_min = int(end_str[:2]), int(end_str[2:])

    if meridian == "PM" and end_hour != 12:
        end_hour += 12
    elif meridian == "AM" and end_hour == 12:
        end_hour = 0

    if meridian == "PM":
        if start_hour != 12 and (start_hour > (end_hour - 12) or start_hour >= 11):
            pass
        elif start_hour != 12:
            start_hour += 12
    elif meridian == "AM" and start_hour == 12:
        start_hour = 0

    return f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}"

# def parse_enrollment_file(file_content):
    # if not file_content or not file_content.strip():
        # return {}, pd.DataFrame()

    # lines = file_content.split('\n')
    # header_metadata = {}
    # cleaned_rows = []

    # for line in lines:
        # if "METROPOLITAN STATE UNIVERSITY" in line:
            # date_match = re.search(r'(\d{2}-[A-Z]{3}-\d{4})', line)
            # if date_match:
                # header_metadata['report_date'] = date_match.group(1)
        # if "Term:" in line and 'term' not in header_metadata:
            # t_match = re.search(r'Term:\s*(\d+)', line)
            # d_match = re.search(r'Dept:\s*([^\s-]+)', line)
            # if t_match: header_metadata['term'] = t_match.group(1)
            # if d_match: header_metadata['dept'] = d_match.group(1)

    # ignorable = ["SWRCGSR", "METROPOLITAN STATE", "Class Enrollment", "Term:",
                 # "Subj Nmbr CRN", "---- ---- ----", "Subject Code", "** TOTALS **",
                 # "Cr Hr Prod", "Sections", "------------"]

    # for line in lines:
        # if any(kw in line for kw in ignorable) or not line.strip():
            # continue
        # if line.strip().startswith('\x0c') or line.strip().isdigit():
            # continue
        # cleaned_rows.append(line)

    # return header_metadata, reconstruct_records(cleaned_rows)

def parse_enrollment_file(file_content):
    if not file_content or not file_content.strip():
        return {}, pd.DataFrame()

    lines = file_content.split('\n')
    header_metadata = {}
    cleaned_rows = []

    for line in lines:
        if "METROPOLITAN STATE UNIVERSITY" in line:
            date_match = re.search(r'(\d{2}-[A-Z]{3}-\d{4})', line)
            if date_match:
                header_metadata['report_date'] = date_match.group(1)
        if "Term:" in line and 'term' not in header_metadata:
            t_match = re.search(r'Term:\s*(\d+)', line)
            d_match = re.search(r'Dept:\s*([^\s-]+)', line)
            if t_match: header_metadata['term'] = t_match.group(1)
            if d_match: header_metadata['dept'] = d_match.group(1)

    ignorable = ["SWRCGSR", "METROPOLITAN STATE", "Class Enrollment", "Term:",
                 "Subj Nmbr CRN", "---- ---- ----", "Subject Code", "** TOTALS **",
                 "Cr Hr Prod", "Sections", "------------"]

    for line in lines:
        if any(kw in line for kw in ignorable) or not line.strip():
            continue
        if line.strip().startswith('\x0c') or line.strip().isdigit():
            continue
        cleaned_rows.append(line)

    # 1. Runs the entire reconstruction, slicing, and splitting pipeline
    df_final = reconstruct_records(cleaned_rows)

    # 2. Calculate CHP safely after all splits have run and zeroed out credits
    if not df_final.empty:
        # Explicitly enforce numeric types to ensure multiplication doesn't break
        df_final['Credit'] = pd.to_numeric(df_final['Credit'], errors='coerce').fillna(0)
        df_final['Enrl'] = pd.to_numeric(df_final['Enrl'], errors='coerce').fillna(0)

        # Calculate Credit Hour Production
        df_final['CHP'] = df_final['Credit'] * df_final['Enrl']

    df_final = apply_custom_course_titles(df_final)

    return header_metadata, df_final


def reconstruct_records(cleaned_rows):
    logical_records = []
    current_record = None
    valid_subject_pattern = re.compile(r'^(MTH|MTL|MTLM)\s+\d+')

    for line in cleaned_rows:
        if valid_subject_pattern.match(line.lstrip()):
            if current_record:
                logical_records.append(current_record)
            current_record = {"base": line, "wraps": []}
        else:
            if current_record:
                current_record["wraps"].append(line)

    if current_record:
        logical_records.append(current_record)

    return slice_fields(logical_records)

def slice_fields(logical_records):
    parsed_data = []

    for record in logical_records:
        base = record["base"]

        subj = base[0:5].strip()
        nmbr = base[5:10].strip()
        crn  = base[10:16].strip()
        sec  = base[16:20].strip()
        s    = base[20:22].strip()
        cam  = base[22:26].strip()
        t    = base[26:28].strip()
        title = base[28:44].strip()
        credit = base[44:51].strip()
        max_enrl = base[51:56].strip()
        enrl = base[56:61].strip()
        wcap = base[61:66].strip()
        wlst = base[66:71].strip()
        days = base[71:79].strip()
        time = base[79:91].strip()
        loc  = base[91:99].strip()
        rcap = base[99:104].strip()
        pct_ful = base[104:109].strip()
        beg_end = base[109:121].strip()
        inst = base[121:].strip()

        if not re.match(r'^\d+$', crn):
            continue

        for wrap in record["wraps"]:
            w_days = wrap[71:79].strip() if len(wrap) > 71 else ""
            w_time = wrap[79:91].strip() if len(wrap) > 79 else ""
            w_loc  = wrap[91:99].strip() if len(wrap) > 91 else ""
            w_inst = wrap[121:].strip() if len(wrap) > 121 else ""

            if w_days or w_time:
                if w_days: days += f" / {w_days}"
                if w_time: time += f" / {w_time}"
                if w_loc: loc += f" / {w_loc}"
            else:
                if w_loc:
                    loc = f"{loc}{w_loc}".strip() if loc else w_loc
                if w_inst:
                    inst = f"{inst}{w_inst}".strip() if inst else w_inst

        time_parts = [convert_to_24hr(t) for t in time.split(' / ')]
        formatted_time = " / ".join(time_parts)

        try:
            max_val = int(max_enrl) if max_enrl.isdigit() else 0
            enrl_val = int(enrl) if enrl.isdigit() else 0
            ratio = round(100 * enrl_val / max_val, 2) if max_val > 0 else 0.0
        except ValueError:
            ratio = 0.0

        course_str = f"{subj}{nmbr}"

        if not nmbr.isdigit():
            calc_status = "N"
        elif course_str in ["MTH1082", "MTH1101", "MTH1116", "MTH1312"]:
            calc_status = "L"
        elif course_str in ["MTL3850", "MTL3858", "MTL4690"]:
            calc_status = "N"
        else:
            calc_status = "Y"

        parsed_data.append({
            'Subj': subj, 'Nmbr': nmbr, 'CRN': crn, 'Sec': sec, 'S': s,
            'Cam': cam, 'T': t, 'Title': title, 'Credit': credit,
            'Max Enrl': max_enrl, 'Enrl': enrl, 'WCap': wcap, 'WLst': wlst,
            'Days': days, 'Time': formatted_time, 'Loc': loc, 'Rcap': rcap,
            '%Ful': pct_ful, 'Begin/End': beg_end, 'Instructor': inst,
            'Course': course_str, 'Ratio': ratio, 'Calc': calc_status,
        })

    # --- Convert records to a temporary DataFrame to clean up numeric types ---
    df_temp = pd.DataFrame(parsed_data)

    # Safely convert specific columns to numeric values, leaving non-numeric items blank (NaN)
    numeric_cols = ['CRN', 'Max Enrl', 'Enrl', 'WCap', 'WLst', 'Rcap', '%Ful']
    for col in numeric_cols:
        if col in df_temp.columns:
            df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')

    # Convert records back to a dictionary format for the next function pipeline stage
    cleaned_records = df_temp.to_dict('records')

    return expand_and_split_courses(cleaned_records)


def expand_and_split_courses(raw_records):
    expanded_records = []

    for row in raw_records:
        if row['Subj'] == 'MTH' and row['Nmbr'] in ['1108', '1109']:
            day_parts = row['Days'].split(' / ')
            time_parts = row['Time'].split(' / ')
            loc_parts = row['Loc'].split(' / ')

            # --- FIXED: Extract absolute string elements using indexing instead of copying entire arrays ---
            lab_days = day_parts[0] if len(day_parts) > 0 else row['Days']
            lab_time = time_parts[0] if len(time_parts) > 0 else row['Time']
            lab_loc  = loc_parts[0]  if len(loc_parts) > 0  else row['Loc']

            lec_days = day_parts[1] if len(day_parts) > 1 else (day_parts[0] if len(day_parts) > 0 else "")
            lec_time = time_parts[1] if len(time_parts) > 1 else (time_parts[0] if len(time_parts) > 0 else "")
            lec_loc  = loc_parts[1]  if len(loc_parts) > 1  else (loc_parts[0] if len(loc_parts) > 0 else "")

            # Row 1: Primary Lecture Component (Clean String Assigned)
            lec_row = row.copy()
            lec_row['Days'], lec_row['Time'], lec_row['Loc'] = lec_days, lec_time, lec_loc
            expanded_records.append(lec_row)

            # Row 2: Lab Component #1 (Clean String Assigned)
            lab_row_1 = row.copy()
            lab_row_1['Days'], lab_row_1['Time'], lab_row_1['Loc'] = lab_days, lab_time, lab_loc
            lab_row_1['Max Enrl'], lab_row_1['Enrl'], lab_row_1['Credit'] = 0, 0, 0
            lab_row_1['WCap'], lab_row_1['WLst'], lab_row_1['Rcap'], lab_row_1['%Ful'] = 0, 0, 0, 0
            expanded_records.append(lab_row_1)

            # Row 3: Lab Component #2 (Clean String Assigned)
            lab_row_2 = lab_row_1.copy()
            lab_row_2['Instructor'] = ","
            lab_row_2['Credit'] = 1
            expanded_records.append(lab_row_2)

        elif " / " in row['Days'] or " / " in row['Time']:
            day_parts = row['Days'].split(' / ')
            time_parts = row['Time'].split(' / ')
            loc_parts = row['Loc'].split(' / ')

            num_components = max(len(day_parts), len(time_parts), len(loc_parts))

            for i in range(num_components):
                split_row = row.copy()
                split_row['Days'] = day_parts[i] if i < len(day_parts) else ""
                split_row['Time'] = time_parts[i] if i < len(time_parts) else ""
                split_row['Loc']  = loc_parts[i]  if i < len(loc_parts)  else ""

                # --- Only the first split component (index 0) keeps original credits ---
                if i > 0:
                    split_row['Credit'] = 0

                expanded_records.append(split_row)
        else:
            expanded_records.append(row)

    return pd.DataFrame(expanded_records)


# def process_excel_import(file_content_bytes):
    # import io

    # # Read raw bytes directly from the base64 Dash upload stream
    # df = pd.read_excel(io.BytesIO(file_content_bytes))

    # # 2. Define the normalization map (Inconsistent Name -> Standard Name)
    # column_mapping = {
        # 'Subj': 'Subj',
        # 'Subject': 'Subj',
        # 'Nmbr': 'Nmbr',
        # 'Number': 'Nmbr',
        # 'Sec': 'Sec',
        # 'Section': 'Sec',
        # 'Cam': 'Cam',
        # 'Campus': 'Cam',
        # 'Max Enrl': 'Max Enrl',
        # 'Max': 'Max Enrl',
        # 'Enrl': 'Enrl',
        # 'Enrolled': 'Enrl',
        # 'WLst': 'WLst',
        # 'WList': 'WLst',
        # '%Ful': '%Ful',
        # 'Full': '%Ful',
    # }

    # # Optional: Clean column names (remove whitespace and standardize casing)
    # # df.columns = df.columns.str.strip().str.title()

    # # 3. Rename the columns safely
    # df = df.rename(columns=column_mapping)

    # # Define the canonical master schema layout your dashboard expects
    # expected_columns = [
        # 'Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title',
        # 'Credit', 'Max Enrl', 'Enrl', 'WCap', 'WLst', 'Days',
        # 'Time', 'Loc', 'Rcap', '%Ful', 'Begin/End', 'Instructor',
        # 'Course', 'CHP', 'Ratio', 'Calc'
    # ]

    # # Add any missing columns and fill them with safe default empty values
    # for col in expected_columns:
        # if col not in df.columns:
            # if col in ['Max Enrl', 'Enrl', 'WCap', 'WLst', 'Rcap', 'Credit', 'CHP']:
                # df[col] = 0
            # else:
                # df[col] = ""

    # # Reorder columns to match standard layout, keeping extra excel columns at the end
    # all_cols = expected_columns + [c for c in df.columns if c not in expected_columns]
    # df = df[all_cols]

    # # Safely convert specific columns to numeric values, leaving non-numeric items blank (NaN)
    # numeric_cols = ['CRN', 'Max Enrl', 'Enrl', 'WCap', 'WLst', 'Rcap', '%Ful']
    # for col in numeric_cols:
        # if col in df.columns:
            # df[col] = pd.to_numeric(df[col], errors='coerce')

    # if not df.empty:
        # # Explicitly enforce numeric types to ensure multiplication doesn't break
        # df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        # df['Enrl'] = pd.to_numeric(df['Enrl'], errors='coerce').fillna(0)

        # # Calculate Credit Hour Production
        # df['CHP'] = df['Credit'] * df['Enrl']

    # # Dummy metadata for excel imports since there's no report header to parse
    # metadata = {'report_date': 'Excel Import', 'term': 'N/A', 'dept': 'N/A'}

    # return metadata, df

def process_excel_import(file_content_bytes):
    import io
    import pandas as pd
    import numpy as np

    # 1. Read raw bytes directly from the base64 Dash upload stream
    df = pd.read_excel(io.BytesIO(file_content_bytes))

    # 2. Define the normalization map (Inconsistent Name -> Standard Name)
    column_mapping = {
        'Subj': 'Subj',
        'Subject': 'Subj',
        'Nmbr': 'Nmbr',
        'Number': 'Nmbr',
        'Sec': 'Sec',
        'Section': 'Sec',
        'Cam': 'Cam',
        'Campus': 'Cam',
        'Max Enrl': 'Max Enrl',
        'Max': 'Max Enrl',
        'Enrl': 'Enrl',
        'Enrolled': 'Enrl',
        'WLst': 'WLst',
        'WList': 'WLst',
        '%Ful': '%Ful',
        'Full': '%Ful',
    }

    # Rename the columns safely
    df = df.rename(columns=column_mapping)

    # Ensure critical columns exist and are clean strings/numbers for downstream calculations
    if 'Subj' not in df.columns: df['Subj'] = ""
    if 'Nmbr' not in df.columns: df['Nmbr'] = ""

    df['Subj'] = df['Subj'].astype(str).str.strip()
    df['Nmbr'] = df['Nmbr'].astype(str).str.strip()

    # --- POPULATE DERIVED VALUE COLUMNS IF THEY DON'T EXIST ---

    # A. Calculate 'Course' (Subj + Nmbr)
    if 'Course' not in df.columns:
        df['Course'] = df['Subj'] + df['Nmbr']

    # B. Calculate 'Ratio' (Enrl / Max Enrl * 100)
    if 'Ratio' not in df.columns:
        # Enforce clean numeric data types for calculations
        max_enrl_numeric = pd.to_numeric(df['Max Enrl'], errors='coerce').fillna(0)
        enrl_numeric = pd.to_numeric(df['Enrl'], errors='coerce').fillna(0)

        # Avoid division-by-zero errors safely using numpy where conditions
        df['Ratio'] = np.where(
            max_enrl_numeric > 0,
            (100 * enrl_numeric / max_enrl_numeric).round(2),
            0.0
        )

    # C. Calculate 'Calc' (Strict translation of your text-parser course-filtering rules)
    if 'Calc' not in df.columns:
        def determine_calc_status(row):
            course_str = row['Course']
            nmbr_str = row['Nmbr']

            if not nmbr_str.isdigit():
                return "N"
            elif course_str in ["MTH1082", "MTH1101", "MTH1116", "MTH1312"]:
                return "L"
            elif course_str in ["MTL3850", "MTL3858", "MTL4690"]:
                return "N"
            else:
                return "Y"

        df['Calc'] = df.apply(determine_calc_status, axis=1)


    # D. Calculate 'CHP' (Enrl * Credit)
    if 'CHP' not in df.columns:
        # Enforce clean numeric data types for calculations
        credit_numeric = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        enrl_numeric = pd.to_numeric(df['Enrl'], errors='coerce').fillna(0)

        df['CHP'] = enrl_numeric * credit_numeric


    # Define the canonical master schema layout your dashboard expects
    expected_columns = [
        'Subj', 'Nmbr', 'CRN', 'Sec', 'S', 'Cam', 'T', 'Title',
        'Credit', 'Max Enrl', 'Enrl', 'WCap', 'WLst', 'Days',
        'Time', 'Loc', 'Rcap', '%Ful', 'Begin/End', 'Instructor',
        'Course', 'CHP', 'Ratio', 'Calc'
    ]

    # Add any missing columns and fill them with safe default empty values
    for col in expected_columns:
        if col not in df.columns:
            if col in ['Max Enrl', 'Enrl', 'WCap', 'WLst', 'Rcap', 'Credit']:
                df[col] = 0
            else:
                df[col] = ""

    # Reorder columns to match standard layout, keeping extra excel columns at the end
    all_cols = expected_columns + [c for c in df.columns if c not in expected_columns]
    df = df[all_cols]

    df = apply_custom_course_titles(df)

    # Dummy metadata for excel imports since there's no report header to parse
    metadata = {'report_date': 'Excel Import', 'term': 'N/A', 'dept': 'N/A'}

    return metadata, df


def detect_academic_term(df):
    """
    Scans spreadsheet columns for date ranges or term entries and automatically
    returns a formatted string like 'Fall 2026 Schedule', 'Spring 2026 Schedule', etc.
    """
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    # Pre-set sensible system defaults
    month = current_month
    year = current_year

    # 1. Look for a date or registration window column header
    date_col = None
    for col in df.columns:
        c_clean = str(col).lower().replace(" ", "").replace("/", "").replace("_", "")
        if "begin" in c_clean or "date" in c_clean or "start" in c_clean or "term" in c_clean:
            date_col = col
            break

    # 2. Safely extract dates from the first valid record row
    if date_col and not df[date_col].dropna().empty:
        first_val = df[date_col].dropna().iloc[0]

        # Check if Pandas automatically parsed the column as a datetime object
        if hasattr(first_val, 'month'):
            month = first_val.month
            year = getattr(first_val, 'year', current_year)
        else:
            # Otherwise, use RegEx to pull digit tokens from raw text (e.g., '08/17-12/13')
            val_str = str(first_val).strip()
            nums = re.findall(r'\d+', val_str)
            if nums:
                # If the first number token is 1 or 2 digits, it's standard US (MM/DD)
                if len(nums[0]) <= 2:
                    potential_month = int(nums[0])
                    if 1 <= potential_month <= 12:
                        month = potential_month
                # If the first number token is 4 digits, it's standard ISO format (YYYY-MM-DD)
                elif len(nums[0]) == 4:
                    year = int(nums[0])
                    if len(nums) > 1:
                        potential_month = int(nums[1])
                        if 1 <= potential_month <= 12:
                            month = potential_month

                # Scan remaining tokens to grab a proper 4-digit year if present
                for n in nums:
                    if len(n) == 4:
                        year = int(n)
                        break

    # 3. Apply seasonal month buckets using Tuples to prevent system rendering bugs
    fall_months = (8, 9, 10, 11, 12)
    spring_months = (1, 2, 3, 4, 5)

    if month in fall_months:
        term = "Fall"
    elif month in spring_months:
        term = "Spring"
    else:
        term = "Summer"

    return f"{term} {year}"


def draw_canvas_decorations(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setStrokeColor(colors.HexColor("#CBD5E0"))
    canvas.setLineWidth(1)
    canvas.line(36, 45, 576, 45)
    current_time_str = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
    canvas.drawString(36, 32, current_time_str)
    canvas.drawRightString(576, 32, f"Page {doc.page}")
    canvas.restoreState()

def build_grouped_pdf(dataframe, group_by_col, term_title, output_target):
    doc = SimpleDocTemplate(
        output_target, pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=60
    )
    styles = getSampleStyleSheet()
    dept_hdr = ParagraphStyle('DeptHdr', fontName='Helvetica-Bold', fontSize=14, leading=16, spaceAfter=4)
    sub_title = ParagraphStyle('SubTitle', fontName='Helvetica-Bold', fontSize=11, leading=14)
    th_style = ParagraphStyle('TH', fontName='Helvetica-BoldOblique', fontSize=8, leading=10)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=8, leading=10)

    story = [
        Paragraph("DEPARTMENT OF MATHEMATICS AND STATISTICS", dept_hdr),
        Paragraph(f"{term_title} Schedule Profile Sorted By {group_by_col}", sub_title),
        HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10)
    ]
    headers = ['CRN', 'Days', 'Time', 'Class', 'Sec', 'CR', 'Title', 'Instructor', 'Bldg', 'Room']
    table_matrix = [[Paragraph(h, th_style) for h in headers]]
    dataframe = dataframe.sort_values(by=[group_by_col, 'Class', 'Section'])
    grouped = dataframe.groupby(group_by_col)

    for _, group_data in grouped:
        for _, row in group_data.iterrows():
            loc_str = str(row.get('Loc', 'ONLI'))
            bldg_val = loc_str.split()[0] if ' ' in loc_str else "ONLI"
            room_val = loc_str.split()[1] if ' ' in loc_str else ""
            table_matrix.append([
                Paragraph(str(row.get('CRN', '')).split('.')[0], td_style),
                Paragraph(str(row.get('Days', '')), td_style),
                Paragraph(str(row.get('Time', '')), td_style),
                Paragraph(str(row.get('Class', '')), td_style),
                Paragraph(str(row.get('Section', '')), td_style),
                Paragraph(str(int(row.get('Credit', 3))), td_style),
                Paragraph(str(row.get('Title', '')), td_style),
                Paragraph(str(row.get('Instructor', 'TBA')), td_style),
                Paragraph(bldg_val, td_style),
                Paragraph(room_val, td_style)
            ])

    col_widths = (40, 35, 60, 60, 25, 20, 130, 90, 40, 40)
    pdf_table = Table(table_matrix, colWidths=col_widths, repeatRows=1)
    pdf_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(pdf_table)
    doc.build(story, onFirstPage=draw_canvas_decorations, onLaterPages=draw_canvas_decorations)

def build_grouped_replica_pdf(dataframe, group_by_col, term_title, output_target):
    """
    Assembles cleaned row blocks into independent tabular grid boxes separated
    by custom padding rows.
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, HRFlowable
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    doc = SimpleDocTemplate(
        output_target, pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=60
    )
    styles = getSampleStyleSheet()

    dept_hdr = ParagraphStyle('DeptHdr', fontName='Helvetica-Bold', fontSize=15, leading=18, spaceAfter=2)
    sub_title = ParagraphStyle('SubTitle', fontName='Helvetica-Bold', fontSize=13, leading=16)
    sort_tag = ParagraphStyle('SortTag', fontName='Helvetica-Oblique', fontSize=11, leading=14, alignment=2)
    th_style = ParagraphStyle('TH', fontName='Helvetica-BoldOblique', fontSize=9, leading=11)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=9, leading=11)

    story = [
        Paragraph("DEPARTMENT OF MATHEMATICS AND STATISTICS", dept_hdr),
        Table([[Paragraph(term_title + " Schedule", sub_title), Paragraph("Instructor Sort" if group_by_col == 'Instructor' else "Course Sort", sort_tag)]], colWidths=[270, 270]),
        HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceBefore=1, spaceAfter=1),
        HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=12)
    ]

    col_widths = (38, 32, 55, 60, 26, 24, 135, 96, 40, 34)
    headers = ['CRN', 'Days', 'Time', 'Class', 'Sec', 'CR', 'Title', 'Instructor', 'Bldg', 'Room']
    table_matrix = [[Paragraph(h, th_style) for h in headers]]

    sorted_df = dataframe.sort_values(by=['Instructor', 'Class', 'Section'] if group_by_col == 'Instructor' else ['Class', 'Section', 'Instructor'])
    grouped = sorted_df.groupby(group_by_col)

    blank_row_indices = []
    current_row_idx = 1

    total_groups = len(grouped)
    for i, (group_name, group_data) in enumerate(grouped):
        for _, row in group_data.iterrows():
            table_matrix.append([
                Paragraph(str(row.get('CRN', '')).split('.')[0], td_style),
                Paragraph(str(row.get('Days', '')), td_style),
                Paragraph(str(row.get('Time', '')), td_style),
                Paragraph(str(row.get('Class', '')), td_style),
                Paragraph(str(row.get('Section', '')), td_style),
                Paragraph(str(int(row.get('Credit', 3) if pd.notna(row.get('Credit')) else 3)), td_style),
                Paragraph(str(row.get('Title', '')), td_style),
                Paragraph(str(row.get('Instructor', 'TBA')), td_style),
                Paragraph(str(row.get('Bldg', 'ONLI')), td_style),
                Paragraph(str(row.get('Room', '')).split('.')[0], td_style)
            ])
            current_row_idx += 1
        if i < total_groups - 1:
            table_matrix.append([""] * len(headers))
            blank_row_indices.append(current_row_idx)
            current_row_idx += 1

    table_styles = [
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2), ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
    ]

    start_row = 1
    for gap_idx in blank_row_indices:
        table_styles.append(('GRID', (0, start_row), (-1, gap_idx - 1), 0.5, colors.HexColor("#A0AEC0")))
        table_styles.append(('ROWBACKGROUNDS', (0, gap_idx), (-1, gap_idx), [colors.white]))
        table_styles.append(('TOPPADDING', (0, gap_idx), (-1, gap_idx), 0))
        table_styles.append(('BOTTOMPADDING', (0, gap_idx), (-1, gap_idx), 14)) # ➔ Structural padding spacing gap size
        start_row = gap_idx + 1

    table_styles.append(('GRID', (0, start_row), (-1, len(table_matrix) - 1), 0.5, colors.HexColor("#A0AEC0")))
    pdf_table = Table(table_matrix, colWidths=col_widths, repeatRows=1)
    pdf_table.setStyle(TableStyle(table_styles))
    story.append(pdf_table)

    # from utilities import draw_canvas_decorations
    doc.build(story, onFirstPage=draw_canvas_decorations, onLaterPages=draw_canvas_decorations)


def parse_contents_integrated(contents, filename):
    """
    Upgraded file parsing engine powered by utils.py logic.
    Maintains compatibility with the scheduling preset queries and preview grid.
    """
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # 1. Leverage the superior engine from utils.py to process data
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        _, df = process_excel_import(decoded)
    else:
        file_text = decoded.decode('utf-8', errors='ignore')
        _, df = parse_enrollment_file(file_text)

    if df.empty:
        return pd.DataFrame()

    # 2. Normalize standard condensed column naming conventions to match dashboard mappings
    column_normalization = {
        'Subj': 'Subject',
        'Nmbr': 'Number',
        'Sec': 'Section',
        'Cam': 'Campus',
        'Enrl': 'Enrolled',
        'Calc': 'Calc'
    }
    df = df.rename(columns=column_normalization)

    # 3. Handle default columns expected downstream by interactive dashboards
    if 'S' not in df.columns:
        df['S'] = 'A'
    if 'Time' in df.columns:
        # Convert derived times slot strings safely
        df['Time'] = df['Time'].apply(lambda x: convert_to_24hr(x) if pd.notna(x) else x)
        # df['Time'] = df['Time'].apply(lambda x: convertAMPMtime(x) if pd.notna(x) else x)

    # Filter to active status courses if present
    # if 'S' in df.columns:
        # df = df[df['S'] == 'A']

    # 3. Clean up formatting and execute the explicit override rule
    # This cleanly acts on the data framework after all type conversions are finalized.
    df['S'] = df['S'].astype(str).str.strip()

    if 'Calc' in df.columns:
        df.loc[df['S'] == 'C', 'Calc'] = 'N'

    # Master dashboard schema fields configuration mapping
    dashboard_fields = ['Subject', 'Number', 'CRN', 'Section', 'S', 'Campus', 'T', 'Title', 'Credit',
       'Max', 'Enrolled', 'WCap', 'WLst', 'Days', 'Time', 'Loc', 'Rcap',
       '%Ful', 'Begin/End', 'Instructor', 'Course', 'Ratio', 'Calc', 'CHP']


    # Secure defaults if field columns aren't filled via excel schema variant mappings
    for col in dashboard_fields:
        if col not in df.columns:
            if col == 'Max':
                df['Max'] = df['Max Enrl'] if 'Max Enrl' in df.columns else 0
            else:
                df[col] = ""

    df = df[dashboard_fields].copy()
    return df


def create_datatable(df, filter_query):
    if filter_query is None:
        filter_query = ''

    accent_colors = ['#b3cde3', '#fbb4ae', '#ccebc5', '#decbe4', '#fed9a6', '#ffffcc', '#e5d8bd', '#fddaec', '#f2f2f2']

    # visible_columns = [{"name": i, "id": i} for i in df.columns if i != 'SortKey']

    return [
        dash_table.DataTable(
            id='datatable-interactivity',
            data=df.to_dict('records'),
            columns = [{"name": i, "id": i} for i in df.columns],
            # columns=visible_columns,
            # sort_by=[{'column_id': 'SortKey', 'direction': 'asc'}],
            style_header={
                'backgroundColor': '#f8fafc',
                'fontWeight': '700',
                'color': '#1e293b',
                'fontFamily': '"Inter", sans-serif',
                'fontSize': '1.05rem',
                'border': '1px solid #e2e8f0',
                'padding': '14px 10px',
                'textTransform': 'uppercase',
                'letterSpacing': '0.05em'
            },
            style_cell={
                'fontFamily': '"Inter", sans-serif',
                'fontSize': '1.15rem',
                'padding': '6px 10px',
                # 'border': '1px solid #f1f5f9',
                # 'color': '#334155',
                'whiteSpace': 'nowrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_table={'height': '600px', 'overflowY': 'auto', 'overflowX': 'auto'},
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                    } for c in ['Title', 'Instructor', 'Days']
                ],
            style_data_conditional=[
                # *data_bars('Ratio', 'Max'),
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(248, 248, 248)",
                },
                {
                    'if': {
                        'filter_query': '{WLst} > 0',
                        'column_id': 'WLst'
                    },
                    'backgroundColor': '#FEFCBF',
                    'color': '#744210'
                },
                {
                    'if': {
                        'filter_query': '{Ratio} > 80',
                        'column_id': 'Enrolled'
                    },
                    'backgroundColor': '#C6EFCE',
                    'color': '#006100'
                },
                {
                    'if': {
                        'filter_query': '{Ratio} > 94',
                        'column_id': 'Enrolled'
                    },
                    'backgroundColor': '#008000',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Calc} = "L"', 'column_id': 'Calc'
                    },
                    'backgroundColor': '#EBF8FF',
                    'color': '#2B6CB0',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'filter_query': '{Calc} = "N"', 'column_id': 'Calc'
                    },
                    'backgroundColor': '#FFF5F5',
                    'color': '#C53030'
                },
                # 1000 level min of 20; 2000 level min of 18, 3000 level min of 15; 4000 level min of 10
                {
                    'if': {
                        'filter_query': '{S} contains "A" && {Credit} > 0 && {Max} > 0 && ({Subject} contains MTH || {Subject} contains MTL) && ({Number} != "1082" && {Number} != "1101" && {Number} != "1116" && {Number} != "1312") && ({Enrolled} < 20 && {Number} < 2000) || ({Enrolled} < 18 && ({Number} >= 2000 && {Number} < 3000)) || ({Enrolled} < 15 && ({Number} >= 3000 && {Number} < 4000)) || ({Enrolled} < 10 && {Number} >= 4000)',
                        'column_id': 'Enrolled'
                    },
                    'backgroundColor': '#FFC7CE',
                    'color': '#9C0006'
                },
                *[
                    {
                        'if': {'filter_query': '{{colorRec}} = "{}"'.format(color), 'column_id': 'colorRec'},
                        'color': 'transparent',
                        'backgroundColor': color,
                    } for color in accent_colors
                ],
                {
                    'if': {
                        'filter_query': '{S} contains C',
                    },
                    'backgroundColor': '#FFF5F5',
                    'color': '#C53030'
                },
                {
                    'if': {
                        'filter_query': '{S} contains "C"', 'column_id': 'colorRec'
                    },
                    'backgroundColor': '#FFF5F5',
                    'color': '#FFF5F5'
                },
            ],
            fixed_rows={'headers': True, 'data': 0},
            editable=True,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            filter_query=filter_query,
            style_data={
                'whiteSpace': 'nowrap',
                'height': 'auto',
            },
        )
    ]


def update_grid(data, filtered_data, slctd_row_indices):
    _dfLoc = pd.DataFrame(data)
    if len(filtered_data) > 0:
        _df = pd.DataFrame(filtered_data)
    else:
        return [blankFigure() for k in range(6)]

    if _df.empty or _dfLoc.empty:
        figs = []
        for d in ['M', 'T', 'W', 'R', 'F', 'S']:
            fig = go.Figure()
            fig.update_layout(
                height=150,
                paper_bgcolor='#f8fafc',
                plot_bgcolor='#f8fafc',
                xaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'bottom', 'showticklabels': False},
                showlegend=False,
                annotations=[dict(
                    text="No scheduled courses found for this query context.",
                    showarrow=False,
                    font=dict(size=14, family='"Inter", sans-serif', color='#64748b')
                )]
            )
            fig.add_trace(go.Scatter(x=[], y=[], xaxis='x2', hoverinfo='none', showlegend=False, marker={'opacity': 0}))
            figs.append(fig)
        return figs

    _dfLoc['Loc'] = _dfLoc['Loc'].fillna('TBA').astype(str)
    _df['Loc'] = _df['Loc'].fillna('TBA').astype(str)

    if 'Days' in _df.columns:
        _df['Days'] = _df['Days'].fillna('').astype(str)

    _dfLoc = _dfLoc[_dfLoc['Campus'] != 'I']
    _df = _df[_df['Campus'] != 'I']

    exclude_mask_loc = _dfLoc['Loc'].str.contains('OFFC|ONLI|TBA', case=False, na=False)
    exclude_mask_df = _df['Loc'].str.contains('OFFC|ONLI|TBA', case=False, na=False)

    _dfLoc = _dfLoc[~exclude_mask_loc]
    _df = _df[~exclude_mask_df]

    _dfLoc = _dfLoc[_dfLoc['S'] != 'C']
    _df = _df[_df['S'] != 'C']

    if _df.empty or _dfLoc.empty:
        figs = []
        for d in ['M', 'T', 'W', 'R', 'F', 'S']:
            fig = go.Figure()
            fig.update_layout(
                height=150,
                paper_bgcolor='#f8fafc',
                plot_bgcolor='#f8fafc',
                xaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'bottom', 'showticklabels': False},
                showlegend=False,
                annotations=[dict(
                    text="No scheduled courses found for this query context.",
                    showarrow=False,
                    font=dict(size=14, family='"Inter", sans-serif', color='#64748b')
                )]
            )
            fig.add_trace(go.Scatter(x=[], y=[], xaxis='x2', hoverinfo='none', showlegend=False, marker={'opacity': 0}))
            figs.append(fig)
        return figs

    if not 'xRec' in _df.columns:
        _df.insert(len(_df.columns), 'xRec', 0.0)
    if not 'yRec' in _df.columns:
        _df.insert(len(_df.columns), 'yRec', 0.0)
    if not 'wRec' in _df.columns:
        _df.insert(len(_df.columns), 'wRec', 1.0)
    if not 'hRec' in _df.columns:
        _df.insert(len(_df.columns), 'hRec', 0.0)
    if not 'textRec' in _df.columns:
        _df.insert(len(_df.columns), 'textRec', '')
    if not 'alphaRec' in _df.columns:
        _df.insert(len(_df.columns), 'alphaRec', 1.0)

    if not 'timeLoc' in _df.columns:
        _df.insert(len(_df.columns), 'timeLoc', 0.0)
    _df['timeLoc'] = _df['Time'].astype(str) + _df['Loc'].astype(str)

    figs = []
    for d in ['M', 'T', 'W', 'R', 'F', 'S']:
        mask = _df['Days'].str.contains(d, case=True, na=False)
        df = _df[mask].copy()

        rooms = _dfLoc['Loc'].dropna().unique()
        Loc = dict(zip(sorted(rooms), range(len(rooms))))
        nLoc = len(list(Loc.keys()))

        timeLoc = {}
        for row in df.index.tolist():
            strTime = str(df.loc[row, 'Time'])
            s = strTime[:5]
            e = strTime[-5:]
            try:
                yRec = 12*(int(s[:2])-8) + int(s[3:])//5
            except ValueError:
                yRec = 0
            try:
                hRec = 12*(int(e[:2])-8) + int(e[3:])//5 - yRec
            except ValueError:
                hRec = 0
            try:
                df.loc[row, 'xRec'] = Loc[df.loc[row, 'Loc']]
            except:
                df.loc[row, 'xRec'] = 0

            df.loc[row, 'yRec'] = yRec
            df.loc[row, 'hRec'] = hRec

            try:
                df.loc[row, 'textRec'] = str(df.loc[row, 'Subject']) + ' ' + str(df.loc[row, 'Number']) + '-' + str(df.loc[row, 'Section'])
            except TypeError:
                df.loc[row, 'textRec'] = ''

            if df.loc[row, 'timeLoc'] in timeLoc:
                timeLoc[df.loc[row, 'timeLoc']].append(row)
            else:
                timeLoc[df.loc[row, 'timeLoc']] = [row]

        for row in timeLoc.values():
            if len(row) > 1:
                for k in range(len(row)):
                    df.loc[row[k], 'xRec'] += k/len(row)
                    df.loc[row[k], 'wRec'] -= (len(row)-1)/len(row)

        fig = go.Figure()
        ply_shapes = {}
        ply_annotations = {}
        for row in df.index.tolist():
            wRec = df.loc[row, 'wRec']
            hRec = df.loc[row, 'hRec']
            xRec = df.loc[row, 'xRec']
            yRec = df.loc[row, 'yRec']
            textRec = df.loc[row, 'textRec']
            colorRec = df.loc[row, 'colorRec']
            alphaRec = df.loc[row, 'alphaRec']

            ply_shapes['shape_' + str(row)] = go.layout.Shape(
                type='rect',
                xref='x', yref='y',
                y0 = xRec, x0 = yRec,
                y1 = xRec + wRec, x1 = (yRec + hRec),
                line=dict(color='LightGray', width=1),
                fillcolor=colorRec,
                opacity=alphaRec,
            )
            ply_annotations['annotation_' + str(row)] = go.layout.Annotation(
                xref='x', yref='y',
                y = xRec + wRec/2,
                x = (yRec + hRec/2),
                text = textRec,
                hoverlabel = {'bgcolor': '#0f172a'},
                hovertext = "Course: {}<br>Title: {}<br>CRN: {}<br>Time: {}<br>Credits: {}<br>Instr: {}".format(
                    textRec, df.loc[row, 'Title'], df.loc[row, 'CRN'], df.loc[row, 'Time'], df.loc[row, 'Credit'], df.loc[row, 'Instructor']
                ),
                showarrow = False,
                font = dict(size=max(1,min(int(.75*hRec),12)), family='"Inter", sans-serif'),
            )

        for k in range(nLoc):
            fill = '#f8fafc' if k % 2 else 'white'
            ply_shapes['shape_vertbar_' + str(k)] = go.layout.Shape(
                type='rect', xref='x', yref='y',
                y0 = k, y1 = k+1, x0 = 0, x1 = 170,
                fillcolor=fill, layer='below', line_width=0,
            )

        lst_shapes=list(ply_shapes.values())
        lst_annotations=list(ply_annotations.values())

        if nLoc:
            fig.update_layout(
                autosize=True,
                height=50*nLoc + 40,
                margin=dict(l=60, r=40, b=40, t=40, pad=0),
                paper_bgcolor='white',
                plot_bgcolor='white',
                yaxis = dict(
                    range=[0,nLoc],
                    tickvals=[k+.5 for k in range(nLoc)],
                    ticktext=list(Loc.keys()),
                    showgrid=False,
                    linecolor='#cbd5e1',
                    tickfont=dict(family='"Inter", sans-serif', color='#475569')
                ),
                xaxis = dict(
                    range=[0,168.2],
                    tickvals=[k*12 for k in range(15)],
                    ticktext=[('0{:d}:00'.format(k))[-5:] for k in range(8,23)],
                    showgrid=True,
                    side='top',
                    gridwidth=1,
                    gridcolor='#f1f5f9',
                    linecolor='#cbd5e1',
                    tickfont=dict(family='"Inter", sans-serif', color='#475569')
                ),
                xaxis2 = dict(
                    range=[0,168.2],
                    tickvals=[k*12 for k in range(15)],
                    ticktext=[('0{:d}:00'.format(k))[-5:] for k in range(8,23)],
                    showgrid=False,
                    overlaying='x',
                    side='bottom',
                    linecolor='#cbd5e1',
                    tickfont=dict(family='"Inter", sans-serif', color='#475569')
                ),
                showlegend=False,
                annotations = lst_annotations,
                shapes=lst_shapes,
            )
        else:
            fig.update_layout(
                height=120,
                xaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'bottom', 'showticklabels': False},
                showlegend=False,
                paper_bgcolor='#f8fafc',
                plot_bgcolor='#f8fafc'
            )

        fig.add_trace(
            go.Scatter(x=[], y=[-0.8], xaxis='x2', hoverinfo='none', showlegend=False, marker={'opacity': 0})
        )
        figs.append(fig)

    return figs

def to_excel(df, report_term):
    _df = df.copy()
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': False}})
    _df.to_excel(writer, sheet_name=report_term, index=False)
    writer.close()
    xlsx_io.seek(0)
    data = base64.b64encode(xlsx_io.read()).decode('utf-8')
    return data


def to_excel_stacked(df, report_term):
    _df = df.copy()
    _df = labs_combined(_df)
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': False}})
    _df.to_excel(writer, sheet_name=report_term, index=False)
    writer.close()
    xlsx_io.seek(0)
    data = base64.b64encode(xlsx_io.read()).decode('utf-8')
    return data


    # # only grab needed columns and correct ordering
    # cols = ["Subject", "Number", "CRN", "Section", "S", "Campus", "T", "Title",
            # "Credit", "Max", "Enrolled", "WCap", "WList", "Days", "Time", "Loc",
            # "Rcap", "Full", "Begin/End", "Instructor", "CHP", "Course", "Ratio", "Calc"]
    # _df = _df[cols]

    # xlsx_io = io.BytesIO()
    # writer = pd.ExcelWriter(
        # xlsx_io, engine='xlsxwriter', engine_kwargs={'options':{'strings_to_numbers': True}}
    # )
    # _df["Section"] = _df["Section"].apply(lambda x: '="{x:s}"'.format(x=x))
    # _df["Number"] = _df["Number"].apply(lambda x: '="{x:s}"'.format(x=x))
    # _df.to_excel(writer, sheet_name=report_term, index=False)

    # workbook = writer.book
    # worksheet = writer.sheets[report_term]

    # # bold = workbook.add_format({"bold": True})

    # rowCount = len(_df.index)

    # worksheet.freeze_panes(1, 0)
    # worksheet.set_column("A:A", 6.5)
    # worksheet.set_column("B:B", 7)
    # worksheet.set_column("C:C", 5.5)
    # worksheet.set_column("D:D", 6.5)
    # worksheet.set_column("E:E", 2)
    # worksheet.set_column("F:F", 6.5)
    # worksheet.set_column("G:G", 2)
    # worksheet.set_column("H:H", 13.2)
    # worksheet.set_column("I:I", 5.5)
    # worksheet.set_column("J:J", 4)
    # worksheet.set_column("K:K", 7)
    # worksheet.set_column("L:L", 5)
    # worksheet.set_column("M:M", 5)
    # worksheet.set_column("N:N", 5.5)
    # worksheet.set_column("O:O", 12)
    # worksheet.set_column("P:P", 7)
    # worksheet.set_column("Q:Q", 4)
    # worksheet.set_column("R:R", 3.5)
    # worksheet.set_column("S:S", 10.5)
    # worksheet.set_column("T:T", 14)
    # worksheet.set_column("U:U", 8)

    # # Common cell formatting
    # # Light red fill with dark red text
    # format1 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
    # # Light yellow fill with dark yellow text
    # format2 = workbook.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"})
    # # Green fill with dark green text.
    # format3 = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
    # # Darker green fill with black text.
    # format4 = workbook.add_format({"bg_color": "#008000", "font_color": "#000000"})

    # # Add enrollment evaluation conditions

    # # 1000 level classes that have fewer than 20 students
    # worksheet.conditional_format(
        # 1,  # row 2
        # 10,  # column K
        # rowCount,  # last row
        # 10,  # column K
        # {"type": "formula", "criteria": "=_xlfn.AND($K2<20,_xlfn.NUMBERVALUE($B2)<2000)", "value": "TRUE", "format": format1},
    # )

    # # 2000 level classes that have fewer than 18 students
    # worksheet.conditional_format(
        # 1,  # row 2
        # 10,  # column K
        # rowCount,  # last row
        # 10,  # column K
        # {"type": "formula", "criteria": "=_xlfn.AND($K2<18,_xlfn.NUMBERVALUE($B2)>1999,_xlfn.NUMBERVALUE($B2)<3000)", "value": "TRUE", "format": format1},
    # )

    # # 3000 level classes that have fewer than 15 students
    # worksheet.conditional_format(
        # 1,  # row 2
        # 10,  # column K
        # rowCount,  # last row
        # 10,  # column K
        # {"type": "formula", "criteria": "=_xlfn.AND($K2<15,_xlfn.NUMBERVALUE($B2)>2999,_xlfn.NUMBERVALUE($B2)<4000)", "value": "TRUE", "format": format1},
    # )

    # # 4000 level classes that have fewer than 10 students
    # worksheet.conditional_format(
        # 1,  # row 2
        # 10,  # column K
        # rowCount,  # last row
        # 10,  # column K
        # {"type": "formula", "criteria": "=_xlfn.AND($K2<10,_xlfn.NUMBERVALUE($B2)>3999)", "value": "TRUE", "format": format1},
    # )

    # # classes that have students on the waitlist
    # worksheet.conditional_format(
        # 1,  # row 2
        # 12,  # column M
        # rowCount,  # last row
        # 12,  # column M
        # {"type": "cell", "criteria": ">", "value": 0, "format": format2},
    # )

    # # Save it
    # writer.close()
    # xlsx_io.seek(0)
    # # media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    # data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    # return data

def labs_combined(df):
    # Combine Max, Enrollments, and WaitLists for Co-Requisite Labs with their parents

    # only use the active courses
    df = df[df["S"]=="A"]

    parent_lab = {"1080": "1081", "1110": "1111", "1112": "1115", "1310": "1311"}
    # filter for parent sections
    for parent in parent_lab.keys():
        mask_parents = (df['Number'] == parent)

        #filter for lab sections
        mask_labs = (df['Number'] == parent_lab[parent])
        for row_p in df[mask_parents].index.tolist():
            for row_l in df[mask_labs].index.tolist():
                if (df.loc[row_p, 'Days'] == df.loc[row_l, 'Days']) and (df.loc[row_p, 'Time'] == df.loc[row_l, 'Time']) and (df.loc[row_p, 'Loc'] == df.loc[row_l, 'Loc']):
                    df.loc[row_p, 'Max'] += df.loc[row_l, 'Max']
                    df.loc[row_p, 'Enrolled'] += df.loc[row_l, 'Enrolled']
                    df.loc[row_p, 'WLst'] += df.loc[row_l, 'WLst']

                    # recalculate the CHP and Ratio
                    df.loc[row_p, 'CHP'] = df.loc[row_p, 'Credit'] * df.loc[row_p, 'Enrolled']
                    df.loc[row_p, 'Ratio'] = 100 * df.loc[row_p, 'Enrolled'] / df.loc[row_p, 'Max']

    # remove the lab sections from the data
    for lab in parent_lab.values():
        mask = df[df['Number'] != lab].index.to_list()
        df = df.loc[mask]
        # df.drop(df[df['Number'] == lab].index, inplace=True)

    return df


def data_bars(column_data, column_apply):
    n_bins = 20
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [100 * i for i in bounds]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column_data, min_bound=min_bound, max_bound=max_bound),
                'column_id': column_apply
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #CACACA 0%,
                    #CACACA {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles

def apply_co_requisite_sorting_keys(df):
    """
    Creates a hidden tracking column to group parent classes and their
    co-requisite lab sessions while strictly maintaining proper sequential section order.
    """
    if df.empty:
        return df

    subj_str = df['Subject'].astype(str).str.strip()
    nmbr_str = df['Number'].astype(str).str.strip()
    sec_str = df['Section'].astype(str).str.strip()

    lab_to_parent_map = {
        "1081": "1080",
        "1111": "1110",
        "1115": "1112",
        "1311": "1310"
    }

    # 1. Resolve Cohort Base Number
    cohort_base_nmbr = nmbr_str.apply(lambda x: lab_to_parent_map.get(x, x))

    # 2. Normalize Section Codes with uniform 3-digit zero padding
    def extract_and_pad_section(section_val):
        match = re.match(r'^(\d+)', section_val)
        if match:
            # Convert to integer and pad to exactly 3 digits (e.g., "01A" -> "001", "010" -> "010")
            return f"{int(match.group(1)):03d}"
        return section_val.zfill(3)

    padded_sec_prefix = sec_str.apply(extract_and_pad_section)

    # 3. Calculate Structural Hierarchy Level (Parent=1, Lab Child=2)
    is_lab_weight = nmbr_str.apply(lambda x: "2" if x in lab_to_parent_map else "1")

    # Unified Sort Key: Subject_Course_PaddedSection_Weight_OriginalSection
    df['SortKey'] = (
        subj_str + "_" +
        cohort_base_nmbr + "_" +
        padded_sec_prefix + "_" +
        is_lab_weight + "_" +
        sec_str
    )

    return df

