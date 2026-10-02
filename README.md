<div align="center">

# 📊 LoL MicroCoach Pro

**A live League of Legends dashboard that reads your game in real time and scores your micro play against baselines.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?logo=plotly&logoColor=white)
![Riot](https://img.shields.io/badge/Riot-Live_Client_%2B_LCU-D32936?logo=riotgames&logoColor=white)

</div>

---

## ✨ Features

- 🔌 **Connects automatically** to the **Live Client Data API** (`127.0.0.1:2999`) and the **League client (LCU)** through its lockfile
- 🎮 **Live snapshot:** champion, level, gold, KDA, CS, CS/min and game time
- 🏃 **Movement score** compared against editable baselines in `data/baselines.json`
- 📈 **Time-series charts** that update every second
- 🗂️ **Three tabs:** Dashboard · Insights · Settings
- 🔒 **Read-only:** never sends inputs to the game

## 🚀 Quick start (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
streamlit run app/streamlit_app.py
```

Then start a League game. Live data appears once you're loaded in.

> If port `2999` is closed, you're either not in a game yet or the Live Client API is disabled in the League client settings.

## 📁 Structure

```
app/streamlit_app.py        # dashboard UI
src/microcoach/
├── live_client.py          # Live Client Data API
├── lcu.py                  # League client (lockfile auth)
├── metrics.py              # game snapshot + movement score
├── baselines.py            # load baselines
├── compare.py              # compare against baselines
└── config.py
data/baselines.json         # edit these to tune the coach
tests/                      # pytest
```

## 🧪 Tests

```bash
pytest
```

---

<div align="center">Built by <a href="https://github.com/vpapirian">Vatche Papirian</a></div>
