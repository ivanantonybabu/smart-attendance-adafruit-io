# ============================================================
# SMARTATTEND
# Cloud-Based Smart Attendance Monitoring System
#
# Platform:
#   Ubuntu + VS Code
#
# Cloud:
#   Adafruit IO
#
# Input:
#   Software-generated Virtual Attendance Data
#
# Dashboard:
#   Flask + Chart.js
# ============================================================


import os
import time
import threading
import random

from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template_string

from dotenv import load_dotenv

from Adafruit_IO import Client, Feed, RequestError


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_NAME = "SMARTATTEND"

UPDATE_INTERVAL = 30


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / "iot.env"


if not ENV_FILE.exists():

    raise RuntimeError(
        f"iot.env file not found.\n"
        f"Please create iot.env in:\n{BASE_DIR}"
    )


load_dotenv(dotenv_path=ENV_FILE)


AIO_USERNAME = os.getenv("AIO_USERNAME", "").strip()

AIO_KEY = os.getenv("AIO_KEY", "").strip()


if not AIO_USERNAME or not AIO_KEY:

    raise RuntimeError(
        "AIO_USERNAME or AIO_KEY missing in iot.env"
    )


print("=" * 60)

print(f"{PROJECT_NAME}")

print("Smart Attendance Monitoring System")

print("=" * 60)


# ============================================================
# 3. ATTENDANCE PARAMETERS
# ============================================================

PARAMETERS = {

    "total-students": {
        "name": "Total Students",
        "unit": ""
    },

    "present-count": {
        "name": "Present Students",
        "unit": ""
    },

    "absent-count": {
        "name": "Absent Students",
        "unit": ""
    },

    "attendance-percentage": {
        "name": "Attendance Percentage",
        "unit": "%"
    },

    "attendance-status": {
        "name": "Attendance Status",
        "unit": ""
    },

    "attendance-log": {
        "name": "Latest Attendance Log",
        "unit": ""
    }

}


FEED_NAMES = list(PARAMETERS.keys())


GRAPH_FEEDS = [

    "present-count",

    "absent-count",

    "attendance-percentage"

]


# ============================================================
# 4. CONNECT TO ADAFRUIT IO
# ============================================================

print("\nConnecting to Adafruit IO...")

try:

    aio = Client(AIO_USERNAME, AIO_KEY)

    print("Successfully connected to Adafruit IO.")

except Exception as e:

    raise RuntimeError(
        f"Adafruit IO connection failed:\n{e}"
    )


# ============================================================
# 5. CREATE / INITIALIZE ADAFRUIT IO FEEDS
# ============================================================

def setup_feeds():

    feeds = {}

    print("\nChecking Adafruit IO feeds...")

    for feed_name in FEED_NAMES:

        try:

            # Try to retrieve existing feed

            feed = aio.feeds(feed_name)

            print(f"Feed exists: {feed_name}")

        except RequestError:

            # If feed does not exist, create it

            try:

                feed = aio.create_feed(
                    Feed(name=feed_name)
                )

                print(f"Created new feed: {feed_name}")

            except Exception as e:

                print(
                    f"Could not create feed "
                    f"{feed_name}: {e}"
                )

                continue

        feeds[feed_name] = feed


    missing = [

        name for name in FEED_NAMES

        if name not in feeds

    ]


    if missing:

        raise RuntimeError(

            "The following feeds could not be initialized:\n"

            + ", ".join(missing)

        )


    print("\nAll required Adafruit IO feeds are ready.")

    return feeds


ADAFRUIT_FEEDS = setup_feeds()


# ============================================================
# 6. RUNTIME DATA STORAGE
# ============================================================

latest_data = {}

attendance_history = []


# ============================================================
# 7. VIRTUAL STUDENT DATABASE
# ============================================================

students = [

    "Arun",

    "Rahul",

    "Anjali",

    "Meera",

    "Vishnu",

    "Akhil",

    "Sneha",

    "Aiswarya",

    "Adithya",

    "Nikhil",

    "Fathima",

    "Sreeram",

    "Amal",

    "Devika",

    "Rohit",

    "Neha",

    "Kiran",

    "Athira",

    "Manu",

    "Sona"

]


# ============================================================
# 8. GENERATE VIRTUAL ATTENDANCE DATA
# ============================================================

def generate_attendance_data():

    """
    Generates software-based virtual attendance data.

    No physical hardware is required.

    Each student receives either Present or Absent status.
    """

    present_students = 0

    absent_students = 0

    attendance_logs = []


    print("\n")

    print("-" * 60)

    print("GENERATING VIRTUAL ATTENDANCE DATA")

    print("-" * 60)


    # Generate attendance for every student

    for student in students:


        # 85% probability of Present
        # 15% probability of Absent

        status = random.choices(

            ["Present", "Absent"],

            weights=[85, 15]

        )[0]


        if status == "Present":

            present_students += 1

        else:

            absent_students += 1


        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )


        log = f"{student} - {status} - {timestamp}"


        attendance_logs.append(log)


        print(log)


    total_students = len(students)


    # Calculate attendance percentage

    attendance_percentage = (

        present_students / total_students

    ) * 100


    attendance_percentage = round(

        attendance_percentage,

        2

    )


    # Attendance condition

    if attendance_percentage >= 75:

        attendance_status = "NORMAL"

    else:

        attendance_status = "WARNING: LOW ATTENDANCE"


    # Latest attendance log

    latest_log = attendance_logs[-1]


    # Prepare data dictionary

    data = {

        "total-students": total_students,

        "present-count": present_students,

        "absent-count": absent_students,

        "attendance-percentage": attendance_percentage,

        "attendance-status": attendance_status,

        "attendance-log": latest_log

    }


    # Display summary

    print("\n")

    print("-" * 60)

    print("ATTENDANCE SUMMARY")

    print("-" * 60)

    print(f"Total Students       : {total_students}")

    print(f"Present Students     : {present_students}")

    print(f"Absent Students      : {absent_students}")

    print(f"Attendance Percentage: {attendance_percentage}%")

    print(f"Attendance Status    : {attendance_status}")

    print("-" * 60)


    return data


# ============================================================
# 9. UPLOAD DATA TO ADAFRUIT IO
# ============================================================

def upload_to_adafruit(data):

    """
    Sends attendance data to Adafruit IO feeds.
    """

    print("\nUploading data to Adafruit IO...")


    for feed_name in FEED_NAMES:

        try:

            aio.send_data(

                ADAFRUIT_FEEDS[feed_name].key,

                data[feed_name]

            )

            print(

                f"Uploaded: "

                f"{feed_name} -> {data[feed_name]}"

            )


        except Exception as e:

            print(

                f"Upload failed for "

                f"{feed_name}: {e}"

            )


    print("Upload completed successfully.")


# ============================================================
# 10. COLLECTION CYCLE
# ============================================================

def collect_measurement():

    """
    Generates attendance data,
    stores it locally,
    and uploads it to Adafruit IO.
    """


    data = generate_attendance_data()


    # Update latest data

    latest_data.clear()

    latest_data.update(data)


    # Store history for dashboard graphs

    attendance_history.append({

        "time": datetime.now(timezone.utc).isoformat(),

        "present": data["present-count"],

        "absent": data["absent-count"],

        "percentage": data["attendance-percentage"]

    })


    # Keep only latest 50 records

    if len(attendance_history) > 50:

        attendance_history.pop(0)


    # Upload data to cloud

    upload_to_adafruit(data)


    return data


# ============================================================
# 11. BACKGROUND DATA COLLECTOR
# ============================================================

def background_collector():

    """
    Runs continuously in the background.

    Generates and uploads attendance data
    every UPDATE_INTERVAL seconds.
    """

    print("\nBackground collector started.")

    print(
        f"Update interval: "
        f"{UPDATE_INTERVAL} seconds"
    )


    while True:

        try:

            collect_measurement()


        except Exception as e:

            print("\nCollection error:")

            print(e)


        time.sleep(UPDATE_INTERVAL)


# ============================================================
# 12. FLASK WEB APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# 13. API - CURRENT DATA
# ============================================================

@app.route("/api/current")
def api_current():

    return jsonify({

        name: {

            "name": PARAMETERS[name]["name"],

            "value": latest_data.get(

                name,

                "Waiting..."

            ),

            "unit": PARAMETERS[name]["unit"]

        }

        for name in FEED_NAMES

    })


# ============================================================
# 14. API - ATTENDANCE HISTORY
# ============================================================

@app.route("/api/history")
def api_history():

    return jsonify({

        "present-count": [

            {

                "time": item["time"],

                "value": item["present"]

            }

            for item in attendance_history

        ],

        "absent-count": [

            {

                "time": item["time"],

                "value": item["absent"]

            }

            for item in attendance_history

        ],

        "attendance-percentage": [

            {

                "time": item["time"],

                "value": item["percentage"]

            }

            for item in attendance_history

        ]

    })


# ============================================================
# 15. HTML DASHBOARD
# ============================================================

HTML_PAGE = """

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">


<title>SMARTATTEND Dashboard</title>


<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>


<style>


* {

    box-sizing: border-box;

}


body {

    margin: 0;

    font-family: Arial, Helvetica, sans-serif;

    background: #eef4f8;

    color: #1e293b;

}


header {

    background: #102a43;

    color: white;

    text-align: center;

    padding: 30px 20px;

}


header h1 {

    margin: 0;

    font-size: 42px;

    letter-spacing: 5px;

}


header p {

    margin-top: 10px;

    font-size: 16px;

}


.container {

    max-width: 1200px;

    margin: auto;

    padding: 25px;

}


h2 {

    margin-top: 20px;

    color: #102a43;

}


.grid {

    display: grid;

    grid-template-columns:
    repeat(auto-fit, minmax(220px, 1fr));

    gap: 18px;

}


.card {

    background: white;

    padding: 22px;

    border-radius: 12px;

    box-shadow: 0 4px 12px rgba(0,0,0,.08);

    min-height: 130px;

}


.parameter-name {

    font-size: 13px;

    color: #64748b;

    font-weight: bold;

    text-transform: uppercase;

}


.parameter-value {

    font-size: 28px;

    font-weight: bold;

    margin-top: 15px;

    word-wrap: break-word;

}


.unit {

    font-size: 16px;

    color: #64748b;

}


.chart-container {

    background: white;

    padding: 20px;

    border-radius: 12px;

    margin-top: 20px;

    box-shadow: 0 4px 12px rgba(0,0,0,.08);

}


.normal {

    color: green;

}


.warning {

    color: red;

}


.footer {

    text-align: center;

    padding: 20px;

    color: #64748b;

    font-size: 13px;

}


</style>

</head>


<body>


<header>

<h1>SMARTATTEND</h1>

<p>

Cloud-Based Smart Attendance Monitoring System

</p>

</header>


<div class="container">


<h2>Live Attendance Monitoring</h2>


<div class="grid" id="cards">

Loading attendance data...

</div>


<h2>Attendance Trends</h2>


<div class="chart-container">

<canvas id="attendanceChart"></canvas>

</div>


<h2>Attendance Percentage History</h2>


<div class="chart-container">

<canvas id="percentageChart"></canvas>

</div>


</div>


<div class="footer">

SmartAttend | Powered by Python + Adafruit IO + Flask

</div>


<script>


let attendanceChart = null;

let percentageChart = null;



// --------------------------------------------------
// Determine Status Color
// --------------------------------------------------

function getStatusClass(value) {


    value = String(value).toLowerCase();


    if (value.includes("normal"))

        return "normal";


    if (value.includes("warning"))

        return "warning";


    return "";

}



// --------------------------------------------------
// Update Dashboard
// --------------------------------------------------

async function updateDashboard() {


    try {


        // Fetch current attendance data

        const currentResponse = await fetch(
            "/api/current"
        );


        const current = await currentResponse.json();


        let cardsHTML = "";


        for (const key in current) {


            const item = current[key];


            const valueClass =

                key === "attendance-status"

                ? getStatusClass(item.value)

                : "";


            const displayValue = item.unit

                ? `${item.value}
                   <span class="unit">
                   ${item.unit}
                   </span>`

                : item.value;


            cardsHTML += `

                <div class="card">

                    <div class="parameter-name">

                        ${item.name}

                    </div>


                    <div class="parameter-value ${valueClass}">

                        ${displayValue}

                    </div>

                </div>

            `;

        }


        document.getElementById("cards").innerHTML = cardsHTML;



        // Fetch history data

        const historyResponse = await fetch(
            "/api/history"
        );


        const history = await historyResponse.json();


        const labels = history["present-count"].map(

            p => new Date(p.time).toLocaleTimeString()

        );


        const present = history["present-count"].map(

            p => Number(p.value)

        );


        const absent = history["absent-count"].map(

            p => Number(p.value)

        );


        const percentage = history["attendance-percentage"].map(

            p => Number(p.value)

        );



        // Destroy previous chart

        if (attendanceChart)

            attendanceChart.destroy();


        // Present vs Absent Chart

        attendanceChart = new Chart(

            document.getElementById("attendanceChart"),

            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Present Students",

                            data: present,

                            tension: 0.3

                        },

                        {

                            label: "Absent Students",

                            data: absent,

                            tension: 0.3

                        }

                    ]

                },

                options: {

                    responsive: true,

                    plugins: {

                        legend: {

                            display: true

                        }

                    }

                }

            }

        );



        // Destroy previous percentage chart

        if (percentageChart)

            percentageChart.destroy();


        // Attendance Percentage Chart

        percentageChart = new Chart(

            document.getElementById("percentageChart"),

            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Attendance Percentage",

                            data: percentage,

                            tension: 0.3

                        }

                    ]

                },

                options: {

                    responsive: true,

                    scales: {

                        y: {

                            min: 0,

                            max: 100

                        }

                    }

                }

            }

        );


    }


    catch (error) {


        console.error(

            "Dashboard update error:",

            error

        );


    }

}



// Initial dashboard load

updateDashboard();


// Refresh dashboard every 5 seconds

setInterval(updateDashboard, 5000);


</script>


</body>

</html>

"""


# ============================================================
# 16. DASHBOARD ROUTE
# ============================================================

@app.route("/")
def dashboard():

    return render_template_string(HTML_PAGE)


# ============================================================
# 17. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":


    print("\nStarting SmartAttend System...")


    # Start background data collection thread

    collector_thread = threading.Thread(

        target=background_collector,

        daemon=True

    )


    collector_thread.start()


    print("Background data collector started.")


    print("\nDashboard available at:")

    print("http://127.0.0.1:5000")


    print("\nPress CTRL+C to stop the application.")


    # Start Flask web server

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False,

        use_reloader=False

    )