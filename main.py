import flet as ft
import flet_charts as fc
from database import DB
from utils import parse_ai_input, export_to_csv

def main(page: ft.Page):
    page.title = "Smart Expense Tracker Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 850
    page.bgcolor = "#0D1117"  # Deep modern dark blue/grey
    page.padding = 0

    # Fonts
    page.fonts = {
        "Poppins": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
        "Poppins-Bold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
    }
    
    page.theme = ft.Theme(
        font_family="Poppins",
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary="#4F46E5", # Indigo 600
            secondary="#10B981", # Emerald 500
            surface="#161B22",
        )
    )

    db = DB()
    
    content_area = ft.Container(expand=True, padding=20)

    # Dynamic vibrant colors for charts
    COLORS = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6"]

    def get_color_for_category(index):
        return COLORS[index % len(COLORS)]

    # --- SHARED UI COMPONENTS ---
    def modern_card(content_widget, padding=20, gradient=None):
        return ft.Container(
            content=content_widget,
            padding=padding,
            bgcolor="#161B22" if not gradient else None,
            gradient=gradient,
            border_radius=16,
            border=ft.border.all(1, "#30363D"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#0A0A0A",
                offset=ft.Offset(0, 4)
            )
        )

    # --- VIEWS ---

    # 1. Dashboard View
    def build_dashboard_view():
        stats = db.get_stats_by_category()
        budgets = db.get_budgets()
        total_spent = sum([s[1] for s in stats])
        
        # Total Balance Hero Card
        hero_card = modern_card(
            ft.Column([
                ft.Text("Total Spent This Month", color="#8B949E", size=14),
                ft.Text(f"${total_spent:,.2f}", size=36, weight=ft.FontWeight.W_900, color="white"),
            ], spacing=5),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#1E1B4B", "#312E81", "#4338CA"]
            )
        )

        sections = []
        for i, s in enumerate(stats):
            sections.append(
                fc.PieChartSection(
                    value=s[1],
                    title=f"{s[1]/total_spent*100:.0f}%",
                    color=get_color_for_category(i),
                    radius=50,
                    title_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color="white"),
                )
            )
            
        chart_container = modern_card(
            ft.Column([
                ft.Text("Expense Breakdown", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                fc.PieChart(
                    sections=sections,
                    sections_space=3,
                    center_space_radius=45,
                    expand=True
                ) if sections else ft.Text("No data.", color="#8B949E")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25
        )

        budget_cards = ft.Column(spacing=15)
        for i, s in enumerate(stats):
            cat, spent = s
            limit = budgets.get(cat, 0)
            progress = spent / limit if limit > 0 else 0
            bar_color = "#EF4444" if progress > 1 else "#10B981"
            if progress > 1: progress = 1
            
            budget_cards.controls.append(
                ft.Container(
                    bgcolor="#1C2128",
                    padding=15,
                    border_radius=12,
                    content=ft.Column([
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, color=get_color_for_category(i), size=12),
                                ft.Text(cat, weight=ft.FontWeight.W_600, color="white")
                            ]),
                            ft.Text(f"${spent:,.2f}" + (f" / ${limit:,.0f}" if limit > 0 else ""), color="#C9D1D9", size=13)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=progress, color=bar_color, bgcolor="#30363D", height=6) if limit > 0 else ft.Container()
                    ], spacing=10)
                )
            )

        return ft.ListView(
            controls=[
                ft.Row([ft.Text("Dashboard", size=24, weight=ft.FontWeight.W_800, color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                hero_card,
                ft.Container(height=20),
                chart_container,
                ft.Container(height=20),
                ft.Text("Budget Progress", size=18, weight=ft.FontWeight.W_700, color="white"),
                ft.Container(height=5),
                budget_cards,
                ft.Container(height=30), # Padding
            ],
            spacing=0,
            expand=True
        )

    # 2. Add Expense View
    def build_add_view():
        def input_style(label, prefix=""):
            return {
                "label": label,
                "hint_text": prefix,
                "border_radius": 12,
                "border_color": "#30363D",
                "focused_border_color": "#4F46E5",
                "bgcolor": "#161B22",
                "content_padding": 20
            }

        expense_name = ft.TextField(**input_style("Item Description"))
        expense_amount = ft.TextField(**input_style("Amount ($)"), keyboard_type=ft.KeyboardType.NUMBER)
        expense_category = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option(x) for x in ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Others"]],
            border_radius=12,
            border_color="#30363D",
            bgcolor="#161B22",
            value="Others"
        )
        is_recurring = ft.Switch(label="Recurring Payment", active_color="#10B981")
        recurrence_period = ft.Dropdown(
            options=[ft.dropdown.Option("daily"), ft.dropdown.Option("weekly"), ft.dropdown.Option("monthly")],
            value="monthly",
            visible=False,
            border_color="#30363D", bgcolor="#161B22", border_radius=12
        )

        def toggle_recurring(e):
            recurrence_period.visible = is_recurring.value
            page.update()

        is_recurring.on_change = toggle_recurring

        def manual_add(e):
            if not expense_name.value or not expense_amount.value:
                show_snack("Fill all fields!")
                return
            try:
                amt = float(expense_amount.value)
            except ValueError:
                show_snack("Invalid amount!")
                return
            db.add_expense(expense_name.value, amt, expense_category.value, is_recurring=is_recurring.value, recurrence_period=recurrence_period.value if is_recurring.value else 'none')
            expense_name.value = ""
            expense_amount.value = ""
            show_snack("Expense logged seamlessly ✨")
            page.update()

        ai_input = ft.TextField(
            hint_text="Type naturally e.g., '$15 for coffee'",
            border_radius=25,
            bgcolor="#21262D",
            border_color="transparent",
            prefix_icon=ft.Icons.AUTO_AWESOME,
            content_padding=20,
            on_submit=lambda e: process_ai(e)
        )

        def process_ai(e):
            parsed = parse_ai_input(ai_input.value)
            if parsed['amount'] is not None:
                db.add_expense(parsed['item'], parsed['amount'], parsed['category'], date=parsed['date'])
                ai_input.value = ""
                show_snack(f"Smart logged: ${parsed['amount']} for {parsed['item']}")
                page.update()
            else:
                show_snack("Couldn't extract amount!")

        return ft.ListView([
            ft.Text("Log Expense", size=24, weight=ft.FontWeight.W_800, color="white"),
            ft.Container(height=10),
            ft.Text("AI Smart Entry", color="#8B949E", size=13),
            ai_input,
            ft.Container(height=20),
            ft.Divider(color="#30363D", height=1),
            ft.Container(height=20),
            ft.Text("Manual Entry", color="#8B949E", size=13),
            ft.Container(height=10),
            expense_name,
            ft.Container(height=15),
            ft.Row([expense_amount, expense_category], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=15),
            modern_card(ft.Row([is_recurring, recurrence_period])),
            ft.Container(height=25),
            ft.ElevatedButton(
                "Save Transaction",
                icon=ft.Icons.CHECK_CIRCLE,
                on_click=manual_add,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    bgcolor="#4F46E5",
                    color="white",
                    padding=20
                ),
                width=float('inf')
            )
        ], expand=True)

    # 3. Transactions View
    def build_transactions_view():
        def delete_tx(id):
            db.delete_expense(id)
            refresh_list()
            show_snack("Transaction deleted.")
            
        tx_list = ft.Column(spacing=15)
        
        def refresh_list():
            tx_list.controls.clear()
            expenses = db.get_all_expenses(limit=50)
            if not expenses:
                tx_list.controls.append(ft.Container(content=ft.Text("No transactions found.", color="#8B949E"), padding=20))
            for ex in expenses:
                date_str = ex[4].split()[0] if ex[4] else "Unknown"
                subtitle = f"{ex[3]} • {date_str}"
                
                tx_item = modern_card(
                    ft.ListTile(
                        leading=ft.Container(
                            content=ft.Icon(ft.Icons.MONEY, color="#10B981"),
                            bgcolor="#161B22", padding=10, border_radius=10, border=ft.border.all(1, "#30363D")
                        ),
                        title=ft.Text(ex[1], weight=ft.FontWeight.W_600, color="white", size=15),
                        subtitle=ft.Text(subtitle, color="#8B949E", size=12),
                        trailing=ft.Row([
                            ft.Text(f"-${ex[2]:.2f}", weight=ft.FontWeight.BOLD, size=16, color="white"),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="#EF4444", tooltip="Delete", on_click=lambda e, id=ex[0]: delete_tx(id))
                        ], tight=True)
                    ),
                    padding=5
                )
                tx_list.controls.append(tx_item)
            page.update()

        refresh_list()
        
        return ft.ListView([
            ft.Text("History", size=24, weight=ft.FontWeight.W_800, color="white"),
            ft.Text("Recent 50 transactions", size=14, color="#8B949E"),
            ft.Container(height=15),
            tx_list
        ], expand=True)

    # 4. Settings View
    def build_settings_view():
        def do_export(e):
            success, msg = export_to_csv("smart_expenses.db", "expenses_export.csv")
            show_snack("Exported to expenses_export.csv" if success else f"Export failed: {msg}")

        b_cat = ft.Dropdown(
            options=[ft.dropdown.Option(x) for x in ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Others"]],
            value="Food", border_color="#30363D", bgcolor="#161B22", border_radius=10, expand=1
        )
        b_amt = ft.TextField(label="Budget Limit", hint_text="$ ", keyboard_type=ft.KeyboardType.NUMBER, border_color="#30363D", bgcolor="#161B22", border_radius=10, expand=1)
        
        def save_budget(e):
            if b_amt.value:
                db.set_budget(b_cat.value, float(b_amt.value))
                show_snack(f"Budget for {b_cat.value} set to ${b_amt.value}")
                b_amt.value = ""
                page.update()

        return ft.ListView([
            ft.Text("Settings", size=24, weight=ft.FontWeight.W_800, color="white"),
            ft.Container(height=20),
            modern_card(ft.Column([
                ft.Text("Set Category Budget", weight=ft.FontWeight.BOLD, color="white"),
                ft.Row([b_cat, b_amt], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ElevatedButton("Save Limit", on_click=save_budget, style=ft.ButtonStyle(bgcolor="#4F46E5", color="white", shape=ft.RoundedRectangleBorder(radius=10)), width=float('inf'))
            ])),
            ft.Container(height=20),
            modern_card(ft.Column([
                ft.Text("Data Management", weight=ft.FontWeight.BOLD, color="white"),
                ft.ElevatedButton("Export Data to CSV", icon=ft.Icons.CLOUD_DOWNLOAD, on_click=do_export, style=ft.ButtonStyle(bgcolor="#30363D", color="white", shape=ft.RoundedRectangleBorder(radius=10)), width=float('inf'))
            ]))
        ], expand=True)

    # --- ROUTING / NAVIGATION ---
    views = [build_dashboard_view, build_add_view, build_transactions_view, build_settings_view]

    def on_nav_change(e):
        content_area.content = views[e.control.selected_index]()
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Overview"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Log"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT_OUTLINED, selected_icon=ft.Icons.LIST_ALT, label="History"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_nav_change,
        selected_index=0,
        bgcolor="#0D1117",
        indicator_color="#30363D",
    )

    def show_snack(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg, font_family="Poppins"), bgcolor="#30363D", behavior=ft.SnackBarBehavior.FLOATING)
        page.snack_bar.open = True
        page.update()

    content_area.content = views[0]()
    page.add(ft.Column([content_area], expand=True))
    page.navigation_bar = nav_bar
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
