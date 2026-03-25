<div align="center">
  <h1 align="center">✨ Smart Expense Tracker Pro ✨</h1>
  <p align="center">
    <strong>A breathtaking, cross-platform personal finance tool built entirely in Python.</strong>
  </p>
</div>

---

## 📸 Application Showcase

Here is a glimpse of our beautiful, custom Dark Mode UI integrating premium Neumorphism and Fintech aesthetics:

<p align="center">
  <img src="Screenshot 2026-03-26 013615.png" width="45%" alt="Dashboard Pie Chart View">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Screenshot 2026-03-26 013635.png" width="45%" alt="Dashboard Budgets View">
</p>
<br>
<p align="center">
  <img src="Screenshot 2026-03-26 013650.png" width="45%" alt="Smart AI Expense Logging">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Screenshot 2026-03-26 013703.png" width="45%" alt="Transaction History & Export">
</p>

---

## 🚀 Key Features

This application isn't just an expense logger—it’s an advanced, scalable powerhouse with a highly polished design.

- **Modern Fintech Aesthetics**: Built with deep dark modes, sleek neon gradients, glass-like drop shadows, and Google's crisp **Poppins** font built-in.
- **Advanced Analytics Dashboard**: Actionable visual insights driven natively by `flet-charts`, dynamically breaking down spending across categories in a vibrant `PieChart`.
- **Smart AI Categorization**: Features a custom natural-language NLP engine parser. Just type `"$15 for a coffee"` and the app automatically extracts the amount, classifies it into `Food`, and logs the time locally!
- **Budget Pacing System**: Instantly set monthly category limits and see real-time visual progress bars alerting you if you hit red.
- **Local SQLite DB Protection**: Lightning-fast offline persistence. Zero cloud requirements, meaning absolute privacy over your financials.
- **CSV Data Export**: One-click robust extraction dropping all your transaction histories directly to a `.csv` spreadsheet.
- **Recurring Subscriptions**: Supports tracking daily, weekly, and monthly recurring overhead.

---

## 📂 Codebase Structure

- `main.py` — The core application runner serving all routing via a mobile-friendly `NavigationBar` and handling the massive Flet visual state definitions.
- `database.py` — A robust object-oriented wrapper managing all SQLite connection pools, migrations, budgets table logic, and dynamic querying.
- `utils.py` — Separated logic housing the AI-powered Regex abstraction model and CSV extraction streams.

---

## 🛠️ Tech Stack & Requirements
- **Core Languages**: Python 3.10+
- **Frontend Toolkit**: [Flet](https://flet.dev/) (Compiles safely into Flutter for Desktop, Web, Android, iOS deployment)
- **Visual Extensions**: [flet-charts](https://pypi.org/project/flet-charts/)
- **Backend Infrastructure**: Local standard `sqlite3` driver.

---

## 💻 Getting Started Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/smart-expense-tracker.git
   cd smart-expense-tracker
   ```
2. **Install exact dependencies:**
   ```bash
   pip install flet flet-charts
   ```
3. **Launch the tracker:**
   ```bash
   python main.py
   ```
   *Note: Ensure you are running Python 3.x in your environment. The application will instantly spawn a native desktop window.*
