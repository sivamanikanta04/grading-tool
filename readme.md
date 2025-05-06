Install All Packages at Once
From your terminal or command prompt, navigate to your app folder, then run
pip install -r requirements.txt

| Package     | Use in Your App                                                      |
| ----------- | -------------------------------------------------------------------- |
| `streamlit` | Main framework to create the web UI for grading                      |
| `pandas`    | Handles Excel reading, data manipulation, DataFrames                 |
| `numpy`     | Useful for numerical computations (e.g., creating bell curve range)  |
| `plotly`    | Generates interactive bar charts and plots (grade dist., bell curve) |
| `openpyxl`  | Required for reading/writing `.xlsx` Excel files                     |
| `scipy`     | Used for statistical functions like normal distribution PDF          |
