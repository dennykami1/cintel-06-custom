from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
Depressioncsv = pd.read_csv(app_dir / "Depression Professional Dataset.csv")
