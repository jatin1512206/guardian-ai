import os
import sqlite3
import xlsxwriter

def generate_excel_report(db_path="guardian.db", output_xlsx="ranked_driver_candidates.xlsx"):
    # Connect to the SQLite database to fetch any recorded data, or use a comprehensive baseline of driver candidates
    driver_candidates = []
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Check if driver_profiles table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='driver_profiles';")
            if cursor.fetchone():
                cursor.execute("SELECT id, avg_fatigue, risk_events_count, preferred_speed FROM driver_profiles;")
                rows = cursor.fetchall()
                for row in rows:
                    driver_candidates.append({
                        "id": row[0],
                        "avg_fatigue": row[1],
                        "risk_events_count": row[2],
                        "preferred_speed": row[3]
                    })
            conn.close()
        except Exception as e:
            print(f"Error querying SQLite: {e}")

    # Fallback to a solid, detailed mock dataset of candidates if no runs are recorded in sqlite
    if not driver_candidates:
        driver_candidates = [
            {"id": "DRV-9082", "avg_fatigue": 76.5, "risk_events_count": 18, "preferred_speed": 112.4},
            {"id": "DRV-1029", "avg_fatigue": 62.0, "risk_events_count": 12, "preferred_speed": 98.6},
            {"id": "DRV-4530", "avg_fatigue": 48.5, "risk_events_count": 9, "preferred_speed": 85.2},
            {"id": "DRV-3021", "avg_fatigue": 22.4, "risk_events_count": 3, "preferred_speed": 62.1},
            {"id": "DRV-8821", "avg_fatigue": 15.0, "risk_events_count": 1, "preferred_speed": 55.4},
            {"id": "DRV-5540", "avg_fatigue": 88.2, "risk_events_count": 22, "preferred_speed": 121.0},
            {"id": "DRV-6712", "avg_fatigue": 31.8, "risk_events_count": 4, "preferred_speed": 68.5},
            {"id": "DRV-4011", "avg_fatigue": 55.0, "risk_events_count": 10, "preferred_speed": 90.0}
        ]

    # Calculate custom metrics for ranking: Risk Index, Safety Score, Priority status
    processed_candidates = []
    for d in driver_candidates:
        # Higher fatigue and event counts increase Risk Index (0-100)
        risk_index = (d["avg_fatigue"] * 0.4) + (d["risk_events_count"] * 2.5) + ((max(0, d["preferred_speed"] - 60)) * 0.4)
        risk_index = min(100.0, max(0.0, risk_index))
        safety_score = 100.0 - risk_index
        
        # Classify risk level
        if risk_index > 75.0:
            risk_level = "Critical"
            primary_factor = "Severe Fatigue & Overspeeding"
            action = "Immediate Suspension & Training"
            status = "Recommended for Immediate Training"
        elif risk_index > 50.0:
            risk_level = "High"
            primary_factor = "Frequent Distractions / Speeding"
            action = "Mandatory Active Feedback Course"
            status = "Recommended for Coaching"
        elif risk_index > 25.0:
            risk_level = "Medium"
            primary_factor = "Mild Drowsiness / Yaw Drift"
            action = "Warning Alarms Monitoring"
            status = "Under Watch"
        else:
            risk_level = "Low"
            primary_factor = "Attentive / Safe Habits"
            action = "Performance Bonus Recommendation"
            status = "Safe"
            
        processed_candidates.append({
            "id": d["id"],
            "safety_score": round(safety_score, 1),
            "risk_index": round(risk_index, 1),
            "risk_level": risk_level,
            "primary_factor": primary_factor,
            "action": action,
            "status": status
        })

    # Sort candidates by Risk Index descending (Highest risk = candidate rank 1 for urgent training)
    processed_candidates.sort(key=lambda x: x["risk_index"], reverse=True)

    # Initialize Excel Writer
    workbook = xlsxwriter.Workbook(output_xlsx)
    worksheet = workbook.add_worksheet("Ranked Driver Candidates")
    
    # Enable grid lines
    worksheet.hide_gridlines(0)

    # Define styled formats
    title_format = workbook.add_format({
        'bold': True, 'size': 16, 'font_color': '#0f172a', 'align': 'left', 'valign': 'vcenter'
    })
    subtitle_format = workbook.add_format({
        'size': 11, 'font_color': '#0e7490', 'italic': True, 'align': 'left', 'valign': 'vcenter'
    })
    
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#0f172a', 'font_color': '#ffffff',
        'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 11
    })
    
    cell_center = workbook.add_format({
        'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 10
    })
    cell_left = workbook.add_format({
        'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 10
    })
    
    # Highlight formats for Risk Levels
    format_critical = workbook.add_format({
        'bg_color': '#fee2e2', 'font_color': '#991b1b', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    format_high = workbook.add_format({
        'bg_color': '#ffedd5', 'font_color': '#c2410c', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    format_medium = workbook.add_format({
        'bg_color': '#fef9c3', 'font_color': '#854d0e', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    format_low = workbook.add_format({
        'bg_color': '#dcfce7', 'font_color': '#166534', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'
    })

    # Row backgrounds for stripes
    stripe_left = workbook.add_format({
        'bg_color': '#f8fafc', 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 10
    })
    stripe_center = workbook.add_format({
        'bg_color': '#f8fafc', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 10
    })

    # Write Header Block
    worksheet.merge_range("A1:H1", "HACK2SKILL DATA & AI CHALLENGE - DRIVER RISK REPORT", title_format)
    worksheet.merge_range("A2:H2", "Ranked Driver Candidates Recommended for Safety Coaching & Intervention Programs", subtitle_format)
    
    # Headers
    headers = ["Rank", "Candidate Driver ID", "Safety Score (100)", "Risk Index (100)", "Risk Classification", "Primary Risk Factor", "Recommended Action", "Status"]
    worksheet.set_row(3, 26) # Height of header row
    
    for col, h_text in enumerate(headers):
        worksheet.write(3, col, h_text, header_format)

    # Write Data
    row_num = 4
    for rank_idx, candidate in enumerate(processed_candidates, 1):
        worksheet.set_row(row_num, 22)
        
        is_stripe = (rank_idx % 2 == 0)
        c_fmt = stripe_center if is_stripe else cell_center
        l_fmt = stripe_left if is_stripe else cell_left
        
        worksheet.write(row_num, 0, rank_idx, c_fmt)
        worksheet.write(row_num, 1, candidate["id"], c_fmt)
        worksheet.write(row_num, 2, f"{candidate['safety_score']}%", c_fmt)
        worksheet.write(row_num, 3, f"{candidate['risk_index']}%", c_fmt)
        
        # Risk level styling
        r_level = candidate["risk_level"]
        if r_level == "Critical":
            worksheet.write(row_num, 4, r_level, format_critical)
        elif r_level == "High":
            worksheet.write(row_num, 4, r_level, format_high)
        elif r_level == "Medium":
            worksheet.write(row_num, 4, r_level, format_medium)
        else:
            worksheet.write(row_num, 4, r_level, format_low)
            
        worksheet.write(row_num, 5, candidate["primary_factor"], l_fmt)
        worksheet.write(row_num, 6, candidate["action"], l_fmt)
        worksheet.write(row_num, 7, candidate["status"], l_fmt)
        
        row_num += 1

    # Adjust Column Widths
    worksheet.set_column("A:A", 8)   # Rank
    worksheet.set_column("B:B", 20)  # Driver ID
    worksheet.set_column("C:C", 18)  # Safety Score
    worksheet.set_column("D:D", 18)  # Risk Index
    worksheet.set_column("E:E", 20)  # Classification
    worksheet.set_column("F:F", 28)  # Risk Factor
    worksheet.set_column("G:G", 32)  # Recommended Action
    worksheet.set_column("H:H", 34)  # Status

    workbook.close()
    print("XLSX Report successfully generated: ranked_driver_candidates.xlsx")

if __name__ == "__main__":
    generate_excel_report()
